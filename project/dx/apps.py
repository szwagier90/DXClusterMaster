from django.apps import AppConfig

class DXConfig(AppConfig):
    name = 'dx'
    verbose_name = 'DX Application'

    def ready(self):
        import dx.signals
