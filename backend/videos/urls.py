from django.urls import path
from .views import (
    GenerateVideoView,
    VideoListView,
    VideoDetailView,
    PromptGenerationView,
    PromptTaskDetailView,
    ActivePromptTaskView,
    VideoStreamView  # 确保导入了新视图
)

from .views import PromptHistoryListView, PromptHistoryDeleteView

urlpatterns = [
    # 核心功能：生成视频
    path('generate/', GenerateVideoView.as_view(), name='generate-video'),

    # 辅助功能：生成提示词
    path('prompt/generate/', PromptGenerationView.as_view(), name='generate-prompt'),
    path('prompt/task/<int:pk>/', PromptTaskDetailView.as_view(), name='prompt-task-detail'),
    path('prompt/active/', ActivePromptTaskView.as_view(), name='prompt-active-task'),

    # 列表和详情
    path('list/', VideoListView.as_view(), name='video-list'),
    path('<int:pk>/', VideoDetailView.as_view(), name='video-detail'),

    # 【新增】视频流播放专用接口
    # 注意：name='video-stream' 必须与 serializers.py 中 reverse('video-stream', ...) 里的名字完全一致
    path('stream/<int:pk>/', VideoStreamView.as_view(), name='video-stream'),
    path('prompt/history/', PromptHistoryListView.as_view(), name='prompt-history-list'),
    path('prompt/history/<int:pk>/', PromptHistoryDeleteView.as_view(), name='prompt-history-delete'),
]

