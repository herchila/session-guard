from django.conf import settings


DEFAULTS = {
    "DEVICE_ID_SIGNING_KEY": getattr(settings, "SECRET_KEY", "changeme"),
    "DID_COOKIE_SIGNED": "did_signed",
    "DID_SALT": "device-id-v1",
    "DID_MAX_AGE": 60 * 60 * 24 * 365 * 2,  # 2 years
    "DID_DOMAIN": None,
    "DID_SAMESITE": "Lax",
    "DID_SECURE": True,
    "SESSION_UNIQUENESS": "by_device",  # by_device, by_ip, by_device_and_ip
}


def get_setting(name: str):
    return getattr(settings, f"SESSION_GUARD_{name}", DEFAULTS[name])
