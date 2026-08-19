from django.apps import AppConfig


class StructuresConfig(AppConfig):
    name = 'structures'

    def ready(self):
        import structures.signals  # noqa
