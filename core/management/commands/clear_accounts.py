from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import connection
from django.contrib.sites.models import Site
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount, SocialToken, SocialApp

User = get_user_model()

class Command(BaseCommand):
    help = 'Clears all user accounts and related data'

    def handle(self, *args, **options):
        self.stdout.write('Starting to clear all accounts...')

        # Clear user-related data
        self.stdout.write('Clearing user accounts...')
        User.objects.all().delete()

        # Clear email addresses
        self.stdout.write('Clearing email addresses...')
        EmailAddress.objects.all().delete()

        # Clear social accounts
        self.stdout.write('Clearing social accounts...')
        SocialAccount.objects.all().delete()
        SocialToken.objects.all().delete()
        SocialApp.objects.all().delete()

        # Reset SQLite sequences
        self.stdout.write('Resetting database sequences...')
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM sqlite_sequence")

        self.stdout.write(self.style.SUCCESS('Successfully cleared all accounts and related data!'))
        self.stdout.write('You can now create new accounts.') 