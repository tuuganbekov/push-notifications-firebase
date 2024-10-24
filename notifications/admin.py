from django.contrib import admin
from notifications import models


admin.site.register(models.Topic)
admin.site.register(models.Category)
admin.site.register(models.Notification)
admin.site.register(models.UserDevice)
admin.site.register(models.DetailInfo)
