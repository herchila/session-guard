from django.apps import AppConfig


class AppAccountsConfig(AppConfig):
    name = "demo.app_accounts"
    verbose_name = "Demo Accounts"

    def ready(self):
        from . import signals  # noqa
