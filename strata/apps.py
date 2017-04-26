from django.apps import AppConfig


class StrataConfig(AppConfig):
    name = 'strata'

    def ready(self):
        import strata.signals