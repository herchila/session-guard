from django.utils.deprecation import MiddlewareMixin

from session_guard.conf import get_setting
from session_guard.helper import _decode_did, _mint_device_id, _get_signer



class SessionGuardMiddleware(MiddlewareMixin):
    """
    Make sure each request has:
      - request.did: str
      - request.did_trusted: bool
    And set the cookie did_signed in the response.
    """

    def process_request(self, request) -> None:
        cookie_name = get_setting("DID_COOKIE_SIGNED")
        cookie_value = request.COOKIES.get(cookie_name)

        if cookie_value:
            did, trusted = _decode_did(cookie_value)
        else:
            did = _mint_device_id()
            trusted = False

        request.did = did
        request.did_trusted = trusted
        request._session_guard_should_set_cookie = True

    def process_response(self, request, response) -> None:
        # If the request did not pass through process_request, exit.
        if not hasattr(request, "did"):
            return response

        cookie_name = get_setting("DID_COOKIE_SIGNED")
        signer = _get_signer()
        signed = signer.sign(request.did)

        max_age = get_setting("DID_MAX_AGE")
        domain = get_setting("DID_DOMAIN")
        samesite = get_setting("DID_SAMESITE")
        secure = get_setting("DID_SECURE")

        response.set_cookie(
            cookie_name,
            signed,
            max_age=max_age,
            domain=domain,
            httponly=True,
            secure=secure,
            samesite=samesite,
        )
        return response
