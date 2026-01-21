from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import CreditTransaction

User = get_user_model()

class Command(BaseCommand):
    help = 'Create a new user with default credits.'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username')
        parser.add_argument('password', type=str, help='Password')
        parser.add_argument('--credits', type=int, help='Initial Credits', default=60)

    def handle(self, *args, **kwargs):
        username = kwargs['username']
        password = kwargs['password']
        credits = kwargs['credits']

        if User.objects.filter(username=username).exists():
             self.stdout.write(self.style.ERROR(f'User "{username}" already exists.'))
             return

        user = User.objects.create_user(username=username, password=password)
        user.credits = credits
        user.save()

        CreditTransaction.objects.create(
            user=user,
            amount=credits,
            balance_after=credits,
            description="Initial Credits (Admin Command)"
        )

        self.stdout.write(self.style.SUCCESS(f'Successfully created user "{username}" with {credits} credits.'))