from django.apps import AppConfig

class VideosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'videos'

    def ready(self):
        import sys
        is_server = 'runserver' in sys.argv or 'uwsgi' in sys.argv or 'gunicorn' in sys.argv
        
        # Only run cleanup if it's likely a server process, not during migrations/tasks
        if is_server:
            def run_cleanup():
                import time
                time.sleep(1) # Small delay to ensure DB is ready
                try:
                    from .models import VideoTask
                    from .services import SoraService
                    
                    # Check for tasks left in PROCESSING state
                    # These are likely interrupted by a server restart
                    interrupted_tasks = VideoTask.objects.filter(status='PROCESSING')
                    if interrupted_tasks.exists():
                        print(f"Startup: Found {interrupted_tasks.count()} interrupted video tasks. Cancelling and refunding...")
                        for task in interrupted_tasks:
                            # User requested generic error message "Generation failed" to hide server restart details
                            SoraService._fail_task_final(task.id, "Generation failed")
                except Exception as e:
                    # Catch errors (e.g. during migration when table doesn't exist yet)
                    # print(f"Startup cleanup handling warning: {e}")
                    pass

            import threading
            threading.Thread(target=run_cleanup, daemon=True).start()
