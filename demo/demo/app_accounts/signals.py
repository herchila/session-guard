from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

from session_guard.services import upsert_on_login


@receiver(user_logged_in)
def on_user_logged_in(sender, request, user, **kwargs):
    upsert_on_login(request, user)
