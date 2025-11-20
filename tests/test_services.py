import uuid

import pytest
from django.contrib.auth import get_user_model
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.sessions.models import Session
from django.test import RequestFactory

from session_guard.models import Device, DeviceSession
from session_guard.services import (
    _mask_ip,
    revoke_all_except_current,
    revoke_session,
    upsert_on_login,
)


def _make_request(
    user_agent="Agent/1.0", remote_addr="203.0.113.10", did=None, trusted=False
):
    factory = RequestFactory()
    request = factory.get("/", HTTP_USER_AGENT=user_agent, REMOTE_ADDR=remote_addr)
    SessionMiddleware(lambda req: None).process_request(request)
    request.session.save()
    request.did = did or str(uuid.uuid4())
    request.did_trusted = trusted
    return request


@pytest.mark.django_db
def test_mask_ip_returns_original_value():
    assert _mask_ip("198.51.100.5") == "198.51.100.5"


@pytest.mark.django_db
def test_upsert_on_login_creates_device_and_session():
    user = get_user_model().objects.create_user(username="alice")
    request = _make_request(
        remote_addr="198.51.100.9", did=str(uuid.uuid4()), trusted=True
    )

    device, device_session = upsert_on_login(request, user)

    assert Device.objects.count() == 1
    assert device.user == user
    assert device.platform_id == Device.Platform.WEB
    assert device.ua_family == "Agent/1.0"
    assert device.ip_masked == "198.51.100.9"
    assert device.trusted is True

    assert DeviceSession.objects.count() == 1
    assert device_session.user == user
    assert device_session.device == device
    assert device_session.session_type == DeviceSession.SessionType.WEB
    assert device_session.is_active is True
    assert device_session.server_session_key == request.session.session_key


@pytest.mark.django_db
def test_upsert_on_login_updates_existing_device_and_deactivates_previous_session():
    user = get_user_model().objects.create_user(username="bob")
    did = str(uuid.uuid4())
    request1 = _make_request(
        user_agent="FirstAgent", remote_addr="203.0.113.1", did=did
    )

    device, first_session = upsert_on_login(request1, user)
    initial_last_seen = device.last_seen

    long_agent = "Mozilla/" + ("X" * 200)
    request2 = _make_request(
        user_agent=long_agent, remote_addr="203.0.113.2", did=did, trusted=True
    )
    device, second_session = upsert_on_login(request2, user)

    device.refresh_from_db()
    first_session.refresh_from_db()
    second_session.refresh_from_db()

    assert device.ua_family == long_agent[:128]
    assert device.ip_masked == "203.0.113.2"
    assert device.trusted is True
    assert device.last_seen > initial_last_seen

    assert first_session.is_active is False
    assert second_session.is_active is True
    assert second_session.id != first_session.id


@pytest.mark.django_db
def test_revoke_session_deactivates_and_deletes_server_session():
    user = get_user_model().objects.create_user(username="carol")
    request = _make_request(did=str(uuid.uuid4()))
    _, device_session = upsert_on_login(request, user)
    original_last_active = device_session.last_active

    assert Session.objects.filter(
        session_key=device_session.server_session_key
    ).exists()

    revoke_session(user, device_session)

    device_session.refresh_from_db()
    assert device_session.is_active is False
    assert device_session.last_active > original_last_active
    assert (
        Session.objects.filter(session_key=device_session.server_session_key).exists()
        is False
    )


@pytest.mark.django_db
def test_revoke_session_raises_for_other_user():
    owner = get_user_model().objects.create_user(username="owner")
    intruder = get_user_model().objects.create_user(username="intruder")
    request = _make_request(did=str(uuid.uuid4()))
    _, device_session = upsert_on_login(request, owner)

    with pytest.raises(PermissionError):
        revoke_session(intruder, device_session)

    device_session.refresh_from_db()
    assert device_session.is_active is True
    assert Session.objects.filter(
        session_key=device_session.server_session_key
    ).exists()


@pytest.mark.django_db
def test_revoke_all_except_current_closes_other_active_sessions():
    user = get_user_model().objects.create_user(username="dana")
    current_request = _make_request(did=str(uuid.uuid4()))
    _, current_session = upsert_on_login(current_request, user)

    device1 = Device.objects.create(user=user, device_id=uuid.uuid4())
    device2 = Device.objects.create(user=user, device_id=uuid.uuid4())

    store1 = SessionStore()
    store1.create()
    store2 = SessionStore()
    store2.create()

    session1 = DeviceSession.objects.create(
        user=user,
        device=device1,
        session_type=DeviceSession.SessionType.WEB,
        server_session_key=store1.session_key,
        is_active=True,
    )
    session2 = DeviceSession.objects.create(
        user=user,
        device=device2,
        session_type=DeviceSession.SessionType.MOBILE,
        server_session_key=store2.session_key,
        is_active=True,
    )

    revoke_all_except_current(current_request, user)

    session1.refresh_from_db()
    session2.refresh_from_db()
    current_session.refresh_from_db()

    assert session1.is_active is False
    assert session2.is_active is False
    assert Session.objects.filter(session_key=store1.session_key).exists() is False
    assert Session.objects.filter(session_key=store2.session_key).exists() is False

    assert current_session.is_active is True
    assert Session.objects.filter(
        session_key=current_request.session.session_key
    ).exists()
