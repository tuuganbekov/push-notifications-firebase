from django.db import models, transaction


class CustomManager(models.Manager):
    def update_by_device_id(self, instance, data: dict):
        with transaction.atomic():
            for name, value in data.items():
                if hasattr(instance, name):
                    setattr(instance, name, value)
            instance.save()
        return instance
