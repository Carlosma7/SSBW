from django.apps import AppConfig

class SenderosConfig(AppConfig):
    name = 'senderos'

    def ready(self):
    	import senderos.signals