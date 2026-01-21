from django.db import models
from django.utils import timezone

# Create your models here.
class DailyStats(models.Model):
    date = models.DateField(unique=True, default=timezone.now)
    # Total API calls (legacy + aggregate)
    api_call_count = models.IntegerField(default=0)
    # Granular API stats
    video_gen_count = models.IntegerField(default=0)
    prompt_gen_count = models.IntegerField(default=0)
    # Site visits
    visit_count = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = 'Daily Statistic'
        verbose_name_plural = 'Daily Statistics'
        ordering = ['-date']
        
    def __str__(self):
        return f"{self.date} - API: {self.api_call_count} - Visits: {self.visit_count}"

class UserApiUsage(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='api_usage')
    date = models.DateField(default=timezone.now)
    # Counts
    count = models.IntegerField(default=0) # Total
    video_gen = models.IntegerField(default=0)
    prompt_gen = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ('user', 'date')
        ordering = ['-date']
        
    def __str__(self):
        return f"{self.user.username} - {self.date} - Total: {self.count}"

class ApiRequestLog(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)
    endpoint = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    timestamp = models.DateTimeField(default=timezone.now)
    type = models.CharField(max_length=20, choices=[('video', 'Video'), ('prompt', 'Prompt'), ('other', 'Other')], default='other')

    class Meta:
        ordering = ['-timestamp']

class UserVisitLog(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='visit_logs')
    timestamp = models.DateTimeField(default=timezone.now)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    path = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        ordering = ['-timestamp']
        
    def __str__(self):
        return f"{self.user.username} - {self.timestamp} - {self.path}"

class SystemSetting(models.Model):
    key = models.CharField(max_length=100, unique=True, verbose_name="配置键")
    value = models.TextField(verbose_name="配置值")
    description = models.CharField(max_length=255, blank=True, null=True, verbose_name="描述")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "系统设置"
        verbose_name_plural = "系统设置"

    def __str__(self):
        return f"{self.key}: {self.value}"

    @classmethod
    def get_setting(cls, key, default=None):
        try:
            return cls.objects.get(key=key).value
        except cls.DoesNotExist:
            return default
