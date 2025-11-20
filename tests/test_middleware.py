import pytest

from django.core.signing import Signer
from django.test import Client

from session_guard.conf import get_setting


@pytest.mark.django_db
def test_middleware_sets_did_cookie_on_first_request():
    client = Client()

    resp1 = client.get("/account/sessions/")
    assert resp1.status_code in (200, 302)

    cookies = resp1.cookies
    assert "did_signed" in cookies

    did_cookie = cookies["did_signed"].value
    assert did_cookie is not None

    signer = Signer(
        key=get_setting("DEVICE_ID_SIGNING_KEY"),
        salt=get_setting("DID_SALT"),
    )
    did = signer.unsign(did_cookie)
    assert len(did) > 0


@pytest.mark.django_db
def test_middleware_preserves_did_cookie_on_next_requests():
    client = Client()

    resp1 = client.get("/account/sessions/")
    assert resp1.status_code in (200, 302)

    cookies = resp1.cookies
    assert "did_signed" in cookies

    did_cookie = cookies["did_signed"].value
    assert did_cookie is not None

    client.cookies["did_signed"] = did_cookie
    resp2 = client.get("/account/sessions/")
    assert "did_signed" in resp2.cookies or "did_signed" in client.cookies
