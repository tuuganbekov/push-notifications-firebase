# Generated by Django 5.0.6 on 2024-05-28 08:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0003_alter_userdevice_device_id_alter_userdevice_subs_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='notification',
            old_name='user_device_id',
            new_name='device_id',
        ),
        migrations.RemoveField(
            model_name='userdevice',
            name='subs',
        ),
        migrations.RemoveField(
            model_name='userdevice',
            name='token',
        ),
        migrations.AddField(
            model_name='userdevice',
            name='allow_notifications',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='userdevice',
            name='push_notification_token',
            field=models.CharField(default=1, max_length=250),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='userdevice',
            name='subs_id',
            field=models.CharField(default=1, max_length=250),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='userdevice',
            name='device_id',
            field=models.CharField(max_length=250),
        ),
    ]
