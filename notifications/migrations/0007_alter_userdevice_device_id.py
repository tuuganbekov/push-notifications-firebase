# Generated by Django 5.0.6 on 2024-05-29 04:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0006_remove_notification_description_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userdevice',
            name='device_id',
            field=models.CharField(max_length=250),
        ),
    ]
