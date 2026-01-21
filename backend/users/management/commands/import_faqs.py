import json
from django.core.management.base import BaseCommand
from users.models import FAQ

class Command(BaseCommand):
    help = 'Import initial FAQ content'

    def handle(self, *args, **options):
        faq_data = [
            {
                "question_zh": "为什么生成的视频比较模糊？",
                "question_en": "Why are the generated videos blurry?",
                "answer_zh": "视频清晰度主要取决于所选模型和提示词描述。建议采取以下措施提升画质：\n\n1. 选择高清模型：对于画质有更高要求，请务必选用 sora2-pro 模型，其默认生成1080P高清视频。\n\n2. 优化提示词：在您的描述中加入如 “电影级画质”、“8K分辨率”、“细节丰富”、“专业摄影” 等关键词，能有效引导AI生成更清晰、更具质感的画面。",
                "answer_en": "Video clarity mainly depends on the selected model and the prompt description. We recommend the following to improve quality:\n\n1. Choose HD Model: For higher quality requirements, use the sora2-pro model, which generates 1080P HD video by default.\n\n2. Optimize Prompts: Include keywords like 'cinematic quality', '8K resolution', 'rich details', or 'professional photography' in your description to effectively guide the AI to generate clearer, more textured visuals.",
                "order": 1,
                "is_active": True
            },
            {
                "question_zh": "为什么会生成失败？",
                "question_en": "Why did the generation fail?",
                "answer_zh": "生成失败通常由内容违规或技术问题导致：\n\n内容安全限制：\n- 禁止使用真人照片或提示词中出现真人姓名。\n- 禁止生成违法、暴力、裸露或侵权内容。\n\n技术性原因：\n- 提示词描述模糊、自相冲突，或超出AI理解范围。\n- 平台系统高负载或技术异常。\n- 图片格式或尺寸不符（针对图生视频）。",
                "answer_en": "Generation failures are usually caused by content violations or technical issues:\n\nContent Safety Restrictions:\n- No real people's photos or names (including celebrities/politicians).\n- No illegal, violent, nude, or infringing content.\n\nTechnical Reasons:\n- Vague or conflicting prompt descriptions beyond the AI's current capabilities.\n- High system load or temporary technical anomalies.\n- Incorrect image format or size (for Image-to-Video).",
                "order": 2,
                "is_active": True
            },
            {
                "question_zh": "视频生成失败，积分会退还吗？",
                "question_en": "Will credits be refunded if generation fails?",
                "answer_zh": "会的。只要是视频或提示词生成失败，系统将自动全额退还本次任务所消耗的积分。您可以登录后在账户中心查看明细。请注意，如果视频成功生成 but 内容不符合您的个人预期，则积分不予退还。",
                "answer_en": "Yes. If a video or prompt fails to generate, the system will automatically refund the full credit cost for that task. You can view details in the Account Center. Please note that credits are not refundable if the video is successfully generated but does not meet your personal expectations.",
                "order": 3,
                "is_active": True
            },
            {
                "question_zh": "生成一个视频需要多长时间？",
                "question_en": "How long does it take to generate a video?",
                "answer_zh": "视频生成耗时根据模型不同而有所差异：\n- 使用 sora 模型生成720P视频，通常需要 4-8分钟。\n- 使用 sora2-pro 模型生成1080P高清视频，通常需要 10-15分钟。\n以上为预估时间，高峰期可能会有所延长。",
                "answer_en": "Generation time varies by model:\n- Sora (720P): Typically 4-8 minutes.\n- Sora2-pro (1080P): Typically 10-15 minutes due to higher complexity.\nThese are estimates; times may vary during peak periods.",
                "order": 4,
                "is_active": True
            },
            {
                "question_zh": "如何编写提示词才能得到更好的视频？",
                "question_en": "How to write better prompts for better videos?",
                "answer_zh": "一个好的提示词应包含：\n- 主体与环境：清晰描述主角和场景。\n- 视觉风格：如\"皮克斯动画\"、\"赛博朋克\"等。\n- 镜头与运镜：描述镜头语言，如\"无人机俯看\"。\n- 动态与细节：说明动作和细微情节。\n具体参考：https://cookbook.openai.com/examples/sora/sora2_prompting_guide",
                "answer_en": "A good prompt should include:\n- Subject & Environment: Clearly describe the character and scene.\n- Visual Style: e.g., 'Pixar style', 'Cyberpunk', 'Ink painting'.\n- Camera & Motion: Describe camera language like 'Drone view' or 'Close-up'.\n- Dynamics & Details: Specify actions and subtle details.\nRefer to: https://cookbook.openai.com/examples/sora/sora2_prompting_guide",
                "order": 5,
                "is_active": True
            }
        ]

        count = 0
        for item in faq_data:
            FAQ.objects.get_or_create(
                question_zh=item['question_zh'],
                defaults=item
            )
            count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Successfully imported {count} FAQ items'))
