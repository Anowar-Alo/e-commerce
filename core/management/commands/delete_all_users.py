from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()

class Command(BaseCommand):
    help = 'Deletes all users from the database'

    def handle(self, *args, **options):
        with transaction.atomic():
            # Delete all users
            count = User.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f'Successfully deleted all users')) 