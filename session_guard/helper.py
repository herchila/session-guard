import uuid
from typing import Tuple

from django.core.signing import Signer, BadSignature

from .conf import get_setting


def _get_signer() -> Signer:
    key = get_setting("DEVICE_ID_SIGNING_KEY")
    salt = get_setting("DID_SALT")
    return Signer(key=key, salt=salt)


def _mint_device_id() -> str:
    return str(uuid.uuid4())


def _decode_did(cookie_value: str) -> Tuple[str, bool]:
    signer = _get_signer()
    try:
        did = signer.unsign(cookie_value)
        return did, True
    except BadSignature:
        return _mint_device_id(), False
