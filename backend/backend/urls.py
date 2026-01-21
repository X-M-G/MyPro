from django.contrib import admin
from django.urls import path, include
# 1. 引入以下两个模块
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("api/adym/", include('SoraApp.urls')),
    path("admin/", admin.site.urls),
    path("api/auth/", include('users.urls')),
    path("api/videos/", include('videos.urls')),
    path("api/auth/captcha/", include('captcha.urls')),
]

# 2. 添加这一段：仅在 Debug 模式下生效
# 这段代码的作用是：告诉 Django，当有人访问 /media/ 开头的链接时，
# 去硬盘上的 MEDIA_ROOT (即你的 media 文件夹) 查找对应的文件。
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
