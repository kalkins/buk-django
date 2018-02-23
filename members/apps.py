from django.apps import AppConfig


class MembersConfig(AppConfig):
    name = 'members'
    verbose_name = 'medlemmer'

    def ready(self):
        import members.signals
