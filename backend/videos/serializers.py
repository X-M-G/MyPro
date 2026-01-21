from rest_framework import serializers
from .models import VideoTask
from django.urls import reverse
from django.core.signing import TimestampSigner


class VideoTaskSerializer(serializers.ModelSerializer):
    result_url = serializers.SerializerMethodField()

    class Meta:
        model = VideoTask
        # ... 保持不变 ...
        fields = [
            'id', 'user', 'prompt', 'ratio', 'duration', 'model', 'generation_time',
            'status', 'progress', 'result_url',
            'sora_task_id', 'failure_reason',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'status', 'progress', 'result_url', 'sora_task_id', 'failure_reason', 'created_at',
                            'updated_at', 'generation_time']

    def get_result_url(self, obj):
        if obj.result_file:
            request = self.context.get('request')

            # 1. 初始化签名器
            signer = TimestampSigner()

            # 2. 对 视频ID 进行签名，生成类似 "3:abc123xyz..." 的字符串
            # 这个签名包含了 ID 本身，且无法被伪造
            signed_token = signer.sign(obj.pk)

            # 3. 构造基础 URL
            path = reverse('video-stream', args=[obj.pk])

            # 4. 拼接完整的带签名的 URL
            url = f"{path}?token={signed_token}"

            if request:
                return request.build_absolute_uri(url)
            return url
        return None
    

from .models import PromptHistory, PromptTask

class PromptHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PromptHistory
        fields = [
            'id', 
            'raw_prompt', 
            'style', 
            'language', 
            'optimized_prompt', 
            'credits_used', 
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class PromptTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromptTask
        fields = [
            'id', 'status', 'raw_prompt', 'style', 
            'language', 'duration', 'model', 'optimized_prompt', 
            'failure_reason', 'created_at'
        ]
        read_only_fields = ['id', 'status', 'optimized_prompt', 'failure_reason', 'created_at']