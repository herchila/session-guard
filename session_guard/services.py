from django.utils import timezone

from session_guard.models import Device, DeviceSession


def _mask_ip(ip: str) -> str:
    return ip


def upsert_on_login(request, user, platform_id=None, session_type=None):
    platform_id = platform_id or Device.Platform.WEB
    session_type = session_type or DeviceSession.SessionType.WEB

    did = getattr(request, "did", None)
    trusted = getattr(request, "did_trusted", False)

    # if not did:
    #     did = str(uuid.uuid4())
    #     trusted = False

    ua_family = request.META.get("HTTP_USER_AGENT", "")[:128]
    ip_raw = request.META.get("REMOTE_ADDR")
    ip_masked = _mask_ip(ip_raw)

    device, created = Device.objects.get_or_create(
        user=user,
        device_id=did,
        defaults={
            "platform_id": platform_id,
            "ua_family": ua_family,
            "ip_masked": ip_masked,
            "trusted": bool(trusted),
        },
    )

    if not created:
        Device.objects.filter(pk=device.pk).update(
            ua_family=ua_family,
            ip_masked=ip_masked,
            trusted=bool(trusted),
            last_seen=timezone.now(),
        )

    DeviceSession.objects.filter(
        user=user,
        device=device,
        session_type=session_type,
        is_active=True,
    ).update(is_active=False)

    if not request.session.session_key:
        request.session.save()
    server_session_key = request.session.session_key

    device_session = DeviceSession.objects.create(
        user=user,
        device=device,
        session_type=session_type,
        server_session_key=server_session_key,
        is_active=True,
    )

    return device, device_session


def revoke_session(user, device_session: DeviceSession) -> None:
    """
    Closes the web session: marks is_active=False and invalidates server_session_key.
    """
    from django.contrib.sessions.models import Session

    if device_session.user_id != user.id:
        raise PermissionError("Session does not belong to user")

    device_session.is_active = False
    device_session.save(update_fields=["is_active", "last_active"])

    Session.objects.filter(session_key=device_session.server_session_key).delete()


def revoke_all_except_current(request, user) -> None:
    """
    Closes all active sessions for the user except the current one (useful for 'Close all' button).
    """
    current_key = request.session.session_key
    qs = DeviceSession.objects.filter(
        user=user,
        is_active=True,
    ).exclude(server_session_key=current_key)

    from django.contrib.sessions.models import Session

    for ds in qs:
        Session.objects.filter(session_key=ds.server_session_key).delete()
    qs.update(is_active=False, last_active=timezone.now())
