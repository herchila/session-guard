import uuid

from django.conf import settings
from django.db import models


class Device(models.Model):
    class Platform(models.TextChoices):
        WEB = "WEB", "Web"
        IOS = "IOS", "iOS"
        ANDROID = "ANDROID", "Android"

    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="devices",
    )
    device_id = models.UUIDField(default=uuid.uuid4, editable=False)
    platform_id = models.CharField(
        max_length=16,
        choices=Platform.choices,
        default=Platform.WEB,
    )
    ua_family = models.CharField(max_length=128, blank=True)
    ip_masked = models.GenericIPAddressField(null=True, blank=True)
    trusted = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    last_seen = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "device_id")
        indexes = [
            models.Index(fields=["user", "last_seen"]),
            models.Index(fields=["trusted"]),
        ]

    def __str__(self) -> str:  # type: ignore[override]
        return f"{self.user_id} / {self.device_id} ({self.platform_id})"


class DeviceSession(models.Model):
    class SessionType(models.TextChoices):
        WEB = "WEB", "Web"
        MOBILE = "MOBILE", "Mobile"
        OPENID = "OPENID", "OIDC"

    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="device_sessions",
    )
    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name="sessions",
    )
    session_type = models.CharField(
        max_length=16,
        choices=SessionType.choices,
        default=SessionType.WEB,
    )
    server_session_key = models.CharField(max_length=64)  # Django session key
    is_active = models.BooleanField(default=True)
    last_active = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "session_type", "is_active"]),
            models.Index(fields=["device", "is_active"]),
        ]

    def __str__(self) -> str:  # type: ignore[override]
        return f"{self.user_id} / {self.device_id} / {self.session_type}"
