from rest_framework import serializers
from notifications.models import (
    UserDevice,
    Notification,
    UserNotification,
    Topic,
    DetailInfo,
)


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ("title",)


class DetailInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetailInfo
        fields = "__all__"


class NotificationSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    detail = DetailInfoSerializer()
     
    class Meta:
        model = Notification
        fields = "__all__"
    
    def get_category(self, obj):
        return obj.category.title


class UserDeviceSerializer(serializers.ModelSerializer):
    # rtpl_id = serializers.IntegerField(required=True)
    class Meta:
        model = UserDevice
        fields = "__all__"


class UserNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserNotification
        fields = "__all__"
