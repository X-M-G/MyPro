from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Change user password.'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username')
        parser.add_argument('password', type=str, help='New Password')

    def handle(self, *args, **kwargs):
        username = kwargs['username']
        password = kwargs['password']

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User "{username}" does not exist.'))
            return

        user.set_password(password)
        user.save()

        self.stdout.write(self.style.SUCCESS(f'Successfully changed password for user "{username}".'))