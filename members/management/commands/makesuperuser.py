from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from members.models import Member

class Command(BaseCommand):
    help = 'Turns the user with the given email address into a superuser'

    def add_arguments(self, parser):
        parser.add_argument('email', nargs='+', type=str)
        parser.add_argument(
            '--remove',
            action = 'store_true',
            dest = 'remove',
            default = False,
            help = 'Remove the given superusers instead of adding them.',
        )

    def handle(self, *args, **options):
        for email in options['email']:
            try:
                member = Member.objects.get(email=email)
            except ObjectDoesNotExist:
                self.stderr.write('No member with email %s' % email)
                return

            if options['remove']:
                member.is_superuser = False
                self.stdout.write('%s removed as superuser' % str(member))
            else:
                member.is_superuser = True
                member.is_admin = True
                self.stdout.write('%s added as superuser' % str(member))

            member.save()
