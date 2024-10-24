from django.db import models
from django.utils.translation import gettext_lazy as _
from markdownx.models import MarkdownxField
from notifications.managers import manager

class UserDevice(models.Model):
    class BILLGROUP(models.IntegerChoices):
        INDIVID = 0, 'Индивидуальный'
        CORP = 1, 'Корпоративный'
        
    device_id = models.CharField(max_length=250)
    push_notification_token = models.CharField(max_length=250)
    subs_id = models.CharField(max_length=250)
    bill_group = models.IntegerField(
        choices=BILLGROUP.choices
    )
    rtpl_id = models.IntegerField(null=True)
    allow_notifications = models.BooleanField(default=True)
    
    objects = manager.CustomManager()
    
    def __str__(self) -> str:
        return f"{self.subs_id} - {self.device_id}"


class Topic(models.Model):
    title = models.CharField(
        _("Название"),
        max_length=100
    )
    value = models.CharField(
        _("Значение (техническое)"),
        max_length=100,
        default="all"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self) -> str:
        return self.title
    

class Category(models.Model):
    title = models.CharField(
        _("Название"),
        max_length=100
    )
    icon = models.ImageField(
        _("Иконка"),
        max_length=255,
        null=True,
        blank=True,
    )

    def __str__(self) -> str:
        return self.title
    

class DetailInfo(models.Model):
    image = models.ImageField(
        _("Картинка"),
        max_length=255,
        null=True,
        blank=True,
    )
    body = MarkdownxField(_("Раздел детальной информации"))
    button_title = models.CharField(
        _("Название кнопки"),
        max_length=100,
        null=True,
        blank=True,
    )
    button_route = models.CharField(
        _("Ссылка на кнопке"),
        max_length=255,
        null=True,
        blank=True,
    )


class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('topic', 'Topic'),
        ('personal', 'Personal'),
    )
    title = models.CharField(
        _("Заголовок"),
        max_length=64
    )
    body = models.TextField(
        _("Текст уведомления"),
    )
    date = models.DateTimeField(
        verbose_name=_("Дата отправки"),
    )
    notification_type = models.CharField(
        _("Тип уведомления"),
        max_length=20,
        choices=NOTIFICATION_TYPES,
        default='topic',
    )
    category = models.ForeignKey(
        Category,
        verbose_name=_("Категория"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    topic = models.ForeignKey(
        Topic,
        verbose_name=_("Кому"),
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    detail = models.OneToOneField(
        DetailInfo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    active = models.BooleanField(_("Активный"), default=True)

    def __str__(self) -> str:
        return self.title


class UserNotification(models.Model):
    device = models.ForeignKey(UserDevice, on_delete=models.CASCADE, related_name="device")
    notification = models.ForeignKey(UserDevice, on_delete=models.CASCADE, related_name="notification")


class UserTopicSubscription(models.Model):
    user = models.ForeignKey(UserDevice, on_delete=models.CASCADE, related_name="device_subscription")
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="topic_subscription")
