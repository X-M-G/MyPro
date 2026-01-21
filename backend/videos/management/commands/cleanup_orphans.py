from django.core.management.base import BaseCommand
from videos.models import VideoTask, PromptHistory
from users.models import User

class Command(BaseCommand):
    help = 'Cleans up VideoTasks and PromptHistories with invalid user references'

    def handle(self, *args, **options):
        # 1. Get all valid User IDs
        valid_user_ids = User.objects.values_list('id', flat=True)
        
        # --- Clean VideoTask ---
        orphans_video = VideoTask.objects.exclude(user_id__in=valid_user_ids)
        count_video = orphans_video.count()
        
        if count_video > 0:
            self.stdout.write(self.style.WARNING(f'Found {count_video} orphaned VideoTasks. Deleting...'))
            orphans_video.delete()
            self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count_video} orphaned VideoTasks.'))
        else:
            self.stdout.write(self.style.SUCCESS('No orphaned VideoTasks found.'))

        # --- Clean PromptHistory ---
        orphans_history = PromptHistory.objects.exclude(user_id__in=valid_user_ids)
        count_history = orphans_history.count()

        if count_history > 0:
            self.stdout.write(self.style.WARNING(f'Found {count_history} orphaned PromptHistories. Deleting...'))
            orphans_history.delete()
            self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count_history} orphaned PromptHistories.'))
        else:
            self.stdout.write(self.style.SUCCESS('No orphaned PromptHistories found.'))
