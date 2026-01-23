from django.db import models
from django.conf import settings
import os
import uuid
from django.db import models
from users.models import User  # 假设你的User模型在这里


# 1. 定义动态路径函数
def user_directory_path(instance, filename):
    # instance: VideoTask 的实例 (可以通过 instance.user 访问用户)
    # filename: 原始文件名

    # 获取文件后缀 (例如 .mp4)
    ext = filename.split('.')[-1]

    # 建议重命名文件以避免文件名冲突，这里使用 uuid，也可以保留原名
    new_filename = f"{uuid.uuid4()}.{ext}"

    # 返回格式: videos/user_<id>/<filename>
    # 最终在硬盘上的路径会是: MEDIA_ROOT/videos/user_123/xxxx.mp4
    return f'videos/user_{instance.user.id}/{new_filename}'
class VideoTask(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='video_tasks')
    prompt = models.TextField()
    ratio = models.CharField(max_length=10, default="16:9")
    duration = models.IntegerField(default=10)
    model = models.CharField(max_length=50, default="sora")
    generation_time = models.FloatField(null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    progress = models.IntegerField(default=0)
    # result_url = models.URLField(blank=True, null=True, max_length=500)
    result_file = models.FileField(upload_to=user_directory_path, null=True, blank=True)
    sora_task_id = models.CharField(max_length=100, blank=True, null=True)
    failure_reason = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.status} - {self.created_at}"


class PromptHistory(models.Model):
    """提示词优化历史记录"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='prompt_histories'
    )
    
    # 原始输入
    raw_prompt = models.TextField(help_text="用户输入的原始想法")
    style = models.CharField(max_length=50, default='Cinematic')
    language = models.CharField(max_length=50, default='English')
    
    # 优化后的结果
    optimized_prompt = models.TextField(help_text="AI优化后的提示词")
    
    # 消耗的积分
    credits_used = models.IntegerField(default=20)
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ['-created_at']  # 按创建时间倒序
        verbose_name = "Prompt History"
        verbose_name_plural = "Prompt Histories"
    
    def __str__(self):
        return f"{self.user.username} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class PromptTask(models.Model):
    """
    Async Task for Prompt Generation/Optimization
    Allows persistence across page refreshes.
    """
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='prompt_tasks')
    raw_prompt = models.TextField()
    style = models.CharField(max_length=50, default='Cinematic')
    language = models.CharField(max_length=50, default='English')
    duration = models.CharField(max_length=20, default='10s')
    model = models.CharField(max_length=50, default="sora")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    optimized_prompt = models.TextField(blank=True, null=True)
    failure_reason = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"PromptTask {self.id} - {self.status}"