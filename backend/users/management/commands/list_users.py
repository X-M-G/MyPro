from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.timezone import localtime
from tabulate import tabulate

User = get_user_model()

class Command(BaseCommand):
    help = 'Displays a list of users.'

    def add_arguments(self, parser):
        parser.add_argument('--sort', type=str, help='Sort by field (e.g., credits_desc)', default='id')
        parser.add_argument('--limit', type=int, help='Limit number of results', default=50)

    def handle(self, *args, **kwargs):
        sort = kwargs['sort']
        limit = kwargs['limit']

        queryset = User.objects.all()

        if sort == 'credits_desc':
            queryset = queryset.order_by('-credits')
        else:
            queryset = queryset.order_by('id')

        users = queryset[:limit]

        data = []
        for user in users:
            joined_at = localtime(user.date_joined).strftime('%Y-%m-%d %H:%M')
            inviter = user.invited_by.username if user.invited_by else '-'
            status = 'Effective' if user.is_invite_effective() else 'Invalid'
            if not user.invited_by:
                status = '-'

            data.append([
                user.id,
                user.username,
                user.email,
                user.phone_number or '-',
                user.credits,
                joined_at,
                inviter,
                status
            ])

        self.stdout.write(
            tabulate(
                data,
                headers=['ID', 'Username', 'Email', 'Phone', 'Credits', 'Joined At', 'Inviter', 'Status'],
                tablefmt='grid'
            )
        )
