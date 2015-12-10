from django.apps import AppConfig

class MyAppConfig(AppConfig):
    name = 'cityhallmonitor'
    verbose_name = 'City Hall Monitor'

    def ready(self):
        # import signal handlers
        import cityhallmonitor.signals.handlers
