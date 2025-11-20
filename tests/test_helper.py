import uuid

from django.core.signing import Signer
from django.test import override_settings

import session_guard.helper as helper


@override_settings(
    SESSION_GUARD_DEVICE_ID_SIGNING_KEY="custom-key",
    SESSION_GUARD_DID_SALT="custom-salt",
)
def test_get_signer_uses_configured_settings():
    signer = helper._get_signer()

    assert isinstance(signer, Signer)
    assert signer.key == "custom-key"
    assert signer.salt == "custom-salt"


def test_mint_device_id_generates_uuid4():
    did = helper._mint_device_id()
    parsed = uuid.UUID(did)

    assert parsed.version == 4


@override_settings(
    SESSION_GUARD_DEVICE_ID_SIGNING_KEY="custom-key",
    SESSION_GUARD_DID_SALT="custom-salt",
)
def test_decode_did_returns_original_value_for_valid_signature():
    signer = Signer(key="custom-key", salt="custom-salt")
    signed = signer.sign("device-123")

    did, valid = helper._decode_did(signed)

    assert did == "device-123"
    assert valid is True


@override_settings(
    SESSION_GUARD_DEVICE_ID_SIGNING_KEY="custom-key",
    SESSION_GUARD_DID_SALT="custom-salt",
)
def test_decode_did_mints_new_value_when_signature_invalid(monkeypatch):
    monkeypatch.setattr(helper, "_mint_device_id", lambda: "new-device")

    did, valid = helper._decode_did("tampered-value")

    assert did == "new-device"
    assert valid is False
