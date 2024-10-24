# Generated by Django 5.0.6 on 2024-08-28 04:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0008_topic_notification_created_at_notification_date_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notification',
            name='data',
        ),
        migrations.AddField(
            model_name='notification',
            name='body',
            field=models.TextField(default='Обновление'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='notification',
            name='title',
            field=models.CharField(default='Обновление', max_length=64),
            preserve_default=False,
        ),
    ]
