from django.apps import AppConfig


class AccountsConfig(AppConfig):
    name = 'apps.accounts'

    def ready(self):
        try:
            import apps.accounts.signals  # noqa
        except (ImportError, ModuleNotFoundError):
            from . import signals  # noqa
