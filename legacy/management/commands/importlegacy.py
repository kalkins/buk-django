from django.core.management.base import BaseCommand, CommandError
from django.apps import apps

from ...importers import LegacyImporter

from importlib import import_module
from inspect import getmembers, isclass


class Command(BaseCommand):
    help = 'Imports data from the old database'
    done = []

    def add_arguments(self, parser):
        parser.add_argument(
            'args', metavar='app_label', nargs='*',
            help='Specify the app label(s) to import data for',
        )

    def handle(self, *app_labels, **options):
        # Make sure the apps exist
        app_labels = set(app_labels)
        bad_app_labels = set()
        configs = set()

        if app_labels:
            for app_label in app_labels:
                try:
                    configs.add(apps.get_app_config(app_label))
                except LookupError:
                    bad_app_labels.add(app_label)

            if bad_app_labels:
                for app_label in bad_app_labels:
                    self.stderr.write("App '%s' could not be found. Is it in INSTALLED_APPS?" % app_label)
                sys.exit(2)
        else:
            configs = set(apps.get_app_configs())

        for config in configs:
            if 'django' in config.name or config.name is 'legacy':
                continue

            try:
                mod_name = config.name + '.import_legacy'
                mod = import_module(mod_name)
                classes = getmembers(mod, lambda member: isclass(member) and member.__module__ == mod_name)
                for name, cls in classes:
                    self.run_importer(cls)
            except ModuleNotFoundError:
                self.stderr.write("App '%s' does not have a 'import_legacy.py' file. Skipping." % config.name)

    def run_importer(self, cls):
        if issubclass(cls, LegacyImporter) and cls not in self.done:
            obj = cls()
            for dep in obj.dependencies:
                self.run_importer(dep)
            name = obj.name if obj.name else obj.model._meta.verbose_name_plural
            self.stdout.write('Importing ' + name)
            try:
                obj.execute()
            except Exception as e:
                self.stderr.write("Exception occured while importing %s" % str(obj))
                self.stderr.write("SQL: %s" % obj.sql)
                raise e
            self.done.append(cls)
