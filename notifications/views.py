from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, mixins, status
from rest_framework.views import APIView
from rest_framework.response import Response
from generics.mixins import ServiceCreateModelMixin, ServiceRequestMixin

from loguru_conf import logger
from notifications import serializers
from notifications.forms import (
    DetailInfoForm,
    NotificationForm,
    NotificationModelForm,
)
from notifications.services import (
    user_device,
    notify_service,
    notifications_service,
)
from notifications.models import (
    UserDevice,
    Notification,
    DetailInfo
)
from notifications.tasks import send_notification_by_topic
from utils import get_env


class SendNotificationView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        result = notifications_service.send_notif(data)
        if result["sent"]:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)


class NotificationsAPIView(ServiceRequestMixin, generics.ListAPIView):
    queryset = Notification.objects.all()
    serializer_class = serializers.NotificationSerializer
    service = notify_service.NotificationsListService


class UserDeviceAPIView(ServiceCreateModelMixin, generics.CreateAPIView):
    queryset = UserDevice.objects.all()
    serializer_class = serializers.UserDeviceSerializer
    service = user_device.UserDeviceService


class UserDeviceCreateUpdateAPIView(APIView):
    def post(self, request, *args, **kwargs):
        logger.debug(f"User save {request.data}")
        service = notifications_service.UserDeviceService()
        try:
            instance = service.execute(request.data)
            serializer = serializers.UserDeviceSerializer(instance)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserNotificationCreateAPIView(mixins.CreateModelMixin):
    queryset = UserDevice.objects.all()
    serializer_class = serializers.UserNotificationSerializer
    service_class = notifications_service.UserNotificationService


class NotifyUserAPIView(ServiceRequestMixin, generics.CreateAPIView):
    service = notify_service.NotifyUserService


class NotificationReceivedAPIView(ServiceRequestMixin, generics.CreateAPIView):
    service = notify_service.NotificationRecievedService


@csrf_exempt
def notif_create(request):
    """
    We use 1 app for notifications in firebase
    so we divide topics like:
        - all (for test environment)
        - prod_all (prod environment)
    """
    env = get_env(request)
    if request.method == 'POST':
        form = NotificationForm(request.POST)
        detail_form = DetailInfoForm(request.POST, request.FILES)
        if form.is_valid() and detail_form.is_valid():
            # save detail form first
            logger.debug(f"detail: {detail_form.cleaned_data}")
            detail = detail_form.save()
            notification = form.save(commit=False)
            notification.detail = detail
            notification.save()

            # cleaned data for creating task
            data = form.cleaned_data
            data["notification_id"] = notification.id
            date = data.pop("date")
            del data["category"]
            topic = data.pop("topic")
            topic_name = f"{env}{topic.value}"
            logger.debug(f"notification data {topic_name}: {data}")
            send_notification_by_topic.apply_async(
                args=[topic_name, data],
                eta=date
            )
            return redirect('success')
    else:
        form = NotificationForm()
        detail_form = DetailInfoForm()
    return render(request, 'notification.html', locals())


@csrf_exempt
def notifications_list(request):
    host = request.get_host()
    logger.debug(f"HOST: {host}")
    logger.debug(f"host splitted: {host.split(':')}")
    model_list = Notification.objects.all().order_by("created_at")  # Fetch all objects
    paginator = Paginator(model_list, 10)  # Show 10 items per page

    page_number = request.GET.get('page')  # Get the page number from the query parameters
    page_obj = paginator.get_page(page_number)  # Get the paginated page object

    context = {
        'page_obj': page_obj
    }
    return render(request, 'notifications_list.html', locals())


def notification_update(request, pk):
    notification = get_object_or_404(Notification, pk=pk)
    detail_instance = get_object_or_404(
        DetailInfo,
        pk=notification.detail.id
    )
    if request.method == 'POST':
        form = NotificationModelForm(request.POST, instance=notification)
        detail_form = DetailInfoForm(request.POST, request.FILES, instance=detail_instance)
        if form.is_valid() and detail_form.is_valid():
            detail = detail_form.save()
            notification = form.save(commit=False)
            notification.detail = detail
            notification.save()
            return redirect('detail', pk=notification.pk)
    else:
        form = NotificationModelForm(instance=notification)
        detail_form = DetailInfoForm(instance=detail_instance)
    return render(request, 'notification_form.html', locals())

# Delete a notifications
def notification_delete(request, pk):
    notification = get_object_or_404(Notification, pk=pk)
    if request.method == 'POST':
        notification.delete()
        return redirect('list')
    return render(request, 'notification_confirm_delete.html', {'notifications': notification})
