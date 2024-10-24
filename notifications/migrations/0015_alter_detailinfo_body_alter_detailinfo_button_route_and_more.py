# Generated by Django 5.0.6 on 2024-10-23 05:51

import markdownx.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("notifications", "0014_detailinfo_notification_detail"),
    ]

    operations = [
        migrations.AlterField(
            model_name="detailinfo",
            name="body",
            field=markdownx.models.MarkdownxField(
                verbose_name="Раздел детальной информации"
            ),
        ),
        migrations.AlterField(
            model_name="detailinfo",
            name="button_route",
            field=models.CharField(
                blank=True, max_length=255, null=True, verbose_name="Ссылка на кнопке"
            ),
        ),
        migrations.AlterField(
            model_name="notification",
            name="notification_type",
            field=models.CharField(
                choices=[("topic", "Topic"), ("personal", "Personal")],
                default="topic",
                max_length=20,
                verbose_name="Тип уведомления",
            ),
        ),
    ]