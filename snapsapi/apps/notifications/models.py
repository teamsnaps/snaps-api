# notifications/models.py
from django.db import models
from django.conf import settings

class FCMDevice(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='fcm_devices')
    registration_id = models.TextField()
    type = models.CharField(max_length=10, choices=[('web', 'Web'), ('android', 'Android'), ('ios', 'iOS')])
    active = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('registration_id', 'user')

    def __str__(self):
        return f"{self.user.username}'s {self.type} device"