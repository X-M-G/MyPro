from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import CreditTransaction

User = get_user_model()

class Command(BaseCommand):
    help = 'Add or deduct credits for a user.'

    def add_arguments(self, parser):
        parser.add_argument('user_id', type=int, help='User ID')
        parser.add_argument('amount', type=int, help='Amount to add (negative to deduct)')
        parser.add_argument('--desc', type=str, help='Description for the transaction', default='System admin added credits manually')

    def handle(self, *args, **kwargs):
        user_id = kwargs['user_id']
        amount = kwargs['amount']
        description = kwargs['desc']

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User with ID {user_id} does not exist.'))
            return

        user.credits += amount
        user.save()

        CreditTransaction.objects.create(
            user=user,
            amount=amount,
            balance_after=user.credits,
            description=description
        )

        self.stdout.write(self.style.SUCCESS(f'Successfully updated credits for user {user.username}. New balance: {user.credits}'))
        self.stdout.write(f'Remark: {description}')

        # Check for conditional referral bonus
        # Rule: If user recharge > 399, inviter gets remaining 500 credits
        # Rule: If user recharge > 399, inviter gets remaining 500 credits
        # Only if the invitation is effective (within monthly limit)
        if amount >= 399 and user.invited_by and user.is_invite_effective():
            inviter = user.invited_by
            bonus_amount = 99
            bonus_desc = f"Referral Top-up Bonus (Invitee {user.username} ID:{user.id} > 399)"

            # Check if this specific bonus has already been given
            # We check if a transaction exists for this inviter, with this specific description pattern
            # Note: This is a simple check. For more robustness, we might want a dedicated model or field, 
            # but per requirements, we are using the transaction log.
            already_rewarded = CreditTransaction.objects.filter(
                user=inviter,
                description=bonus_desc
            ).exists()

            if not already_rewarded:
                inviter.credits += bonus_amount
                inviter.save()
                
                CreditTransaction.objects.create(
                    user=inviter,
                    amount=bonus_amount,
                    balance_after=inviter.credits,
                    description=bonus_desc
                )
                self.stdout.write(self.style.SUCCESS(f'Inviter {inviter.username} awarded {bonus_amount} credits.'))
            else:
                self.stdout.write(self.style.WARNING(f'Inviter {inviter.username} already received top-up bonus for this user.'))