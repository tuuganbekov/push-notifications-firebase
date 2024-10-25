from django import forms
from django.utils.translation import gettext_lazy as _
from markdownx.fields import MarkdownxFormField

from notifications.models import (
    Notification,
    Category,
    Topic,
    DetailInfo
)


class DetailInfoForm(forms.ModelForm):
    # image = forms.ImageField()
    body = MarkdownxFormField(label=_("Текст внутри раздела"))
    class Meta:
        model = DetailInfo
        fields = "__all__"


class NotificationForm(forms.ModelForm):
    title = forms.CharField(
        label=_("Заголовок"),
        max_length=40,
        required=True,
    )
    body = forms.CharField(
        widget=forms.Textarea,
        label=_("Текст уведомления"),
        max_length=1000,
        required=True,
    )
    date = forms.DateTimeField(
        label=_("Дата отправки уведомления"),
        widget=forms.DateInput(
            attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }
        ),
        input_formats=['%Y-%m-%dT%H:%M'],
        required=True,
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        label=_("Категория"),
        widget=forms.Select(attrs={
            'class': 'required-tooltip'
        })
    )
    topic = forms.ModelChoiceField(
        queryset=Topic.objects.all(),
        label=_("Кому"),
        widget=forms.Select(attrs={
            'class': 'required-tooltip'
        })
    )
    
    class Meta:
        model = Notification
        exclude = ("active", "detail", "notification_type",)


class NotificationModelForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = (
            "title",
            "body",
            "date",
            "notification_type",
            "category",
            "topic",
            # "detail",
            "active",
        )
