from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Safely deletes a user and all related data'

    def add_arguments(self, parser):
        parser.add_argument(
            'identifier',
            type=str,
            help='ID, Username or Phone number of the user to delete'
        )

    def handle(self, *args, **options):
        try:
            identifier = options['identifier']
            user = None

            # 1. Try by ID
            if identifier.isdigit():
                user = User.objects.filter(id=int(identifier)).first()

            # 2. Try by username
            if not user:
                user = User.objects.filter(username=identifier).first()

            # 3. Try by phone
            if not user:
                user = User.objects.filter(phone=identifier).first()

            if not user:
                self.stdout.write(
                    self.style.ERROR(
                        f'User "{identifier}" not found (checked ID, username, phone)'
                    )
                )
                return

            self.stdout.write(
                self.style.WARNING(
                    f'Found user: {user.username} (ID: {user.id})'
                )
            )

            confirm = input(
                f'Are you sure you want to delete user "{user.username}"? [y/N]: '
            )
            if confirm.lower() != 'y':
                self.stdout.write(self.style.WARNING('Deletion cancelled.'))
                return

            with transaction.atomic():
                deleted_info = user.delete()

            self.stdout.write(
                self.style.SUCCESS(f'Successfully deleted user {user.username}.')
            )

            for model, count in deleted_info[1].items():
                self.stdout.write(f' - Deleted {count} {model}')

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error deleting user: {e}')
            )
