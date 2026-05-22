from django.apps import AppConfig
import sys
import os

class AppointmentAppConfig(AppConfig):
    name = 'appointment_app'

    def ready(self):
        if 'runserver' in sys.argv and os.environ.get('RUN_MAIN') == 'true':
            from django.core.management import call_command
            try:
                print("Running auto-migrations for new fields...")
                call_command('makemigrations', interactive=False)
                print("Successfully auto-migrated database!")
            except Exception as e:
                print("Auto-migration failed:", e)
