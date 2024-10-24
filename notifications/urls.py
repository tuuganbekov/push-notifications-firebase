from django.urls import path
from django.views.generic import TemplateView

from notifications import views


urlpatterns = [
    path('notifications/', views.notifications_list, name='list'),
    path('notify-user/', views.NotifyUserAPIView.as_view()),
    path('send-notification/', views.SendNotificationView.as_view(), name='send_notification'),
    path('save-device/', views.UserDeviceAPIView.as_view()),
    path('notification-received/', views.NotificationReceivedAPIView.as_view()),
    path('save_device/', views.UserDeviceCreateUpdateAPIView.as_view(), name='user-device-create-update'),
    path('create/', views.notif_create, name='create'),
    path('success/', TemplateView.as_view(template_name='success.html'), name='success'),
    path('notifications/<int:pk>/', views.notification_update, name='detail'),
    path('update/', views.notification_update, name='update'),
    path('delete/', views.notification_delete, name='delete'),
    path('notifications/list/', views.NotificationsAPIView.as_view())
]
