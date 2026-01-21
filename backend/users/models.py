import uuid
import random
import string
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True, help_text="User's verified phone number")
    invitation_code = models.CharField(max_length=10, unique=True, null=True, blank=True, help_text="Unique invitation code for the user")
    invited_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='invitees', help_text="The user who invited this user")
    credits = models.IntegerField(default=60, help_text="User credits for video generation")
    password_verified_at = models.DateTimeField(null=True, blank=True, help_text="Timestamp of last SMS password verification")
    
    def save(self, *args, **kwargs):
        if not self.invitation_code:
            self.invitation_code = self.generate_unique_invitation_code()
        super().save(*args, **kwargs)

    def generate_unique_invitation_code(self):
        length = 8
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
            if not User.objects.filter(invitation_code=code).exists():
                return code

    def is_invite_effective(self):
        """
        Check if the invitation is effective (within the monthly limit of 3 for the inviter).
        """
        if not self.invited_by:
            return False
            
        from django.utils import timezone
        # Get joining month
        join_date = self.date_joined
        
        # Count users invited by the same inviter in the same month, ordered by join date
        # We need to see if 'self' is within the first 3
        monthly_invitees = User.objects.filter(
            invited_by=self.invited_by,
            date_joined__year=join_date.year,
            date_joined__month=join_date.month
        ).order_by('date_joined')
        
        # Get IDs of first 3
        valid_ids = list(monthly_invitees.values_list('id', flat=True)[:3])
        
        return self.id in valid_ids

    def __str__(self):
        return self.username

class CreditTransaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    amount = models.IntegerField(help_text="Negative for cost, positive for refund/add")
    balance_after = models.IntegerField(null=True, help_text="User balance after transaction")
    description = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.amount} - {self.timestamp}"

class Announcement(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class AnnouncementView(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='announcement_views')
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE, related_name='views')
    view_count = models.IntegerField(default=0)
    last_viewed_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'announcement')

    def __str__(self):
        return f"{self.user.username} viewed {self.announcement.title} - {self.view_count} times"

class FAQ(models.Model):
    question_zh = models.CharField(max_length=500)
    question_en = models.CharField(max_length=500)
    answer_zh = models.TextField()
    answer_en = models.TextField()
    order = models.IntegerField(default=0, help_text="Display order")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"

    def __str__(self):
        return self.question_zh
