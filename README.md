没问题，这是为你优化后的 README.md 完整内容。你可以直接将其复制并保存为项目根目录下的文件。SoraGen: AI 视频创作一体化平台SoraGen 是一个基于 Vue.js 3 和 Django 5 构建的全栈 AIGC 创作平台。它集成了 OpenAI 的语言处理能力与 Sora (通过 Apimart API) 的视频生成技术，为用户提供从提示词优化到高清视频生成的闭环体验。🌟 核心功能智能提示词助手：集成 OpenAI (GPT-4o) 接口，自动扩充与润色用户的原始创意，显著提升生成视频的质量与一致性。多模态视频生成：文生视频 (Text-to-Video)：支持复杂的语义理解与场景构建。图生视频 (Image-to-Video)：支持上传参考图。后端具备 Base64 自动转存 逻辑，可将前端预览图转换为公网可访问的 HTTPS URL，确保第三方 API 的兼容性。企业级账户管理：基于 Rest Framework Token 的身份验证。集成 阿里云短信 验证与 数字图形验证码 校验。动态用户画像与生成历史记录管理。高可用生产架构：Nginx：作为反向代理，高效处理静态资源（Vue Dist）并转发 API 请求。Gunicorn：高性能 WSGI HTTP 服务器，驱动 Django 后端。SSL 自动化：集成 Certbot 并配置了 IPv6 支持 与 定时自动续签 任务。🛠️ 技术栈模块技术选型前端 (Frontend)Vue 3, Vite, Pinia, Axios, Tailwind CSS后端 (Backend)Python 3.10, Django 5.x, DRF数据库 (Database)SQLite (轻量生产), 支持扩展至 MySQL代理/托管 (Server)Nginx, Gunicorn证书管理Certbot (Let's Encrypt)AI 接口OpenAI API, Sora (Apimart), 五音 API📂 项目结构Plaintext/home/ubuntu/myPro/sora/
├── sora/               # 前端项目根目录 (Vue.js)
│   ├── dist/           # Nginx 托管的打包静态资源
│   └── ...
├── backend/            # 后端项目根目录 (Django)
│   ├── media/          # 用户上传与自动生成的媒体文件
│   ├── static_root/    # 收集后的后端静态资源 (Admin/SimpleUI)
│   ├── videos/         # 视频生成核心逻辑 (含 Base64 转换)
│   └── ...
└── env/                # Python 虚拟环境
🚀 快速开始1. 本地开发环境后端：Bashcd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8000
前端：Bashcd sora
npm install
npm run dev
2. 生产环境部署同步当你有代码更新时，请遵循以下流程：前端打包：在本地执行 npm run build，将 dist 压缩上传至服务器对应目录。后端更新：Bashcd /home/ubuntu/myPro/sora/backend
python manage.py migrate
python manage.py collectstatic --noinput
sudo pkill -9 gunicorn
gunicorn backend.wsgi:application --bind 127.0.0.1:8000 --daemon
权限修复：Bashsudo chmod -R 777 /home/ubuntu/myPro/sora/backend/media/
🔧 关键配置说明Base64 图像转换逻辑为了适配第三方 API，系统在 GenerateVideoView 中实现了自动转换：识别前端提交的 data:image/... 字符串。解码并保存至 MEDIA_ROOT/uploads/，生成 UUID 唯一文件名。利用 request.build_absolute_uri 生成完整的 HTTPS 链接发送至 Apimart。SSL 自动续签系统配置了 Crontab 定时任务，每日凌晨 3:00 自动执行 renew_certs.sh，确保证书永不过期。代码段0 3 * * * /bin/bash /home/ubuntu/renew_certs.sh >> /home/ubuntu/cert_renew.log 2>&1
