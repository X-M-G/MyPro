import os

# 设置时区
os.environ['TZ'] = 'Asia/Shanghai'

# 基本配置
bind = "0.0.0.0:8000"
workers = 2
timeout = 30000

# 日志配置
accesslog = "-"  # 输出到 stdout
errorlog = "-"   # 错误日志也输出到 stdout

# 访问日志格式（包含北京时间）
access_log_format = '%(h)s - - [%(t)s] "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
