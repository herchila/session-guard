from posix import read
from django.contrib import admin

from .models import Device, DeviceSession


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "platform_id", "trusted", "is_verified", "last_seen")
    list_filter = ("platform_id", "trusted", "is_verified")
    search_fields = ("user__username", "user__email", "device_id")
    # read_only_fields = ("id", "user", "platform_id", "trusted", "is_verified", "last_seen")


@admin.register(DeviceSession)
class DeviceSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "device", "session_type", "is_active", "last_active")
    list_filter = ("session_type", "is_active")
    search_fields = ("user__username", "user__email", "server_session_key")
