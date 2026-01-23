import json
import threading
import requests
import time
from django.conf import settings
from .models import VideoTask
from django.contrib.auth import get_user_model
from django.db import transaction
from openai import OpenAI
from django.core.files.base import ContentFile

User = get_user_model()

SORA_API_URL = "https://grsai.dakka.com.cn/v1/video/sora-video"
SORA_RESULT_URL = "https://grsai.dakka.com.cn/v1/draw/result"
SORA_API_KEY = settings.SORA_API_KEY

APIMART_API_URL = "https://api.apimart.ai/v1/videos/generations"
APIMART_TASK_URL = "https://api.apimart.ai/v1/tasks"
APIMART_API_KEY = settings.APIMART_API_KEY

# 重试配置 (GRSAI: Align with marketai for faster feedback)
MAX_RETRY_ATTEMPTS = 90  # 90 * 10s = 15分钟
RETRY_INTERVAL = 10     # 10秒检查一次

# Provider Configuration (Now dynamic via SystemSetting)
# Options: "grsai" (Old), "marketai" (New Apimart)
# SORA_PROVIDER = "marketai"  # Hardcoded fallback removed


# Wuyin Keji API Configuration
WUYIN_SUBMIT_URL = "https://api.wuyinkeji.com/api/sora2pro/submit"
WUYIN_DETAIL_URL = "https://api.wuyinkeji.com/api/sora2/detail"
# Using the key provided in the system instruction / or same as SORA_API_KEY if applicable.
# User example uses "nNOtofqXj5LXQ8m41G0OLuvJFn" for detail but normally they share the same key.
# I'll use SORA_API_KEY from settings.
WUYIN_API_KEY = settings.WUYIN_API_KEY


class SoraService:
    @staticmethod
    def generate_video(task_id, prompt, ratio="16:9", duration=15, ref_image=None, model="sora"):
        try:
            task = VideoTask.objects.get(id=task_id)

            if model in ["sora2-pro", "sora2-pro-c1"]:
                # Use Wuyin Keji API for sora2-pro channel 1
                thread = threading.Thread(target=SoraService._handle_wuyin_task, args=(task.id, prompt, ratio, duration, ref_image))
                thread.start()
                return True

            if model == "sora2-pro-c2":
                # Use Apimart (marketai) for channel 2
                model_to_call = "sora-2-pro"
                thread = threading.Thread(target=SoraService._handle_apimart_task, args=(task.id, prompt, ratio, duration, ref_image, model_to_call))
                thread.start()
                return True

            from SoraApp.models import SystemSetting
            provider = SystemSetting.get_setting("SORA_PROVIDER", "marketai")

            if provider == "marketai":

                 # Use Apimart (marketai)
                 # Hardcoded model "sora-2" as requested
                 model = "sora-2"
                 thread = threading.Thread(target=SoraService._handle_apimart_task, args=(task.id, prompt, ratio, duration, ref_image, model))
                 thread.start()
                 return True

            # Legacy Logic (grsai)
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {SORA_API_KEY}"
            }

            payload = {
                "model": "sora-2",
                "prompt": prompt,
                "aspectRatio": ratio,
                "duration": duration,
                "shutProgress": False,
                "size": 'large'
            }

            if ref_image:
                payload["url"] = ref_image

            thread = threading.Thread(target=SoraService._handle_stream, args=(task.id, headers, payload))
            thread.start()

            return True

        except Exception as e:
            print(f"Error starting generation: {str(e)}")
            SoraService._fail_task(task_id, str(e))
            return False

    @staticmethod
    def _handle_stream(task_id, headers, payload):
        """处理流式响应"""
        print(f"Starting stream for task {task_id}")
        task = VideoTask.objects.get(id=task_id)
        task.status = 'PROCESSING'
        task.save()

        try:
            with requests.post(SORA_API_URL, headers=headers, json=payload, stream=True, timeout=60) as response:
                if response.status_code != 200:
                    raise Exception(f"API Error: {response.status_code} - {response.text}")

                for line in response.iter_lines():
                    if line:
                        decoded_line = line.decode('utf-8')
                        if decoded_line.startswith("data:"):
                            decoded_line = decoded_line[5:].strip()

                        if decoded_line == "[DONE]":
                            break

                        try:
                            data = json.loads(decoded_line)

                            # Update IDs
                            if 'id' in data:
                                task.sora_task_id = data['id']

                            # Update Progress
                            if 'progress' in data:
                                task.progress = data['progress']

                            # Update Status
                            if 'status' in data:
                                # Calculate generation time if available
                                if 'start_time' in data and 'end_time' in data:
                                    try:
                                        start_ts = float(data['start_time'])
                                        end_ts = float(data['end_time'])
                                        task.generation_time = end_ts - start_ts
                                    except (ValueError, TypeError):
                                        pass

                                if data['status'] == 'succeeded':
                                    task.status = 'SUCCESS'

                                    # 如果有结果 URL，执行下载并保存
                                    if 'results' in data and len(data['results']) > 0:
                                        video_url = data['results'][0]['url']
                                        SoraService._download_and_save_video(task, video_url)

                                    task.save()
                                    return  # 任务成功结束

                                elif data['status'] == 'failed':
                                    task.save() # Ensure generation_time is saved even if failed
                                    raise Exception(data.get('failure_reason', 'Unknown failure'))

                            task.save()

                        except json.JSONDecodeError:
                            continue

        except Exception as e:
            print(f"Stream error: {str(e)}")
            # 【关键修改】流式传输失败时，启动重试机制
            SoraService._retry_check_task(task_id)

    @staticmethod
    def _retry_check_task(task_id):
        """
        【新增方法】失败后重试检查任务状态
        如果是网络问题导致的传输失败，API可能已经成功生成
        """
        print(f"Starting retry mechanism for task {task_id}")
        
        try:
            task = VideoTask.objects.get(id=task_id)
            
            # 如果没有 sora_task_id，说明连API都没调用成功，直接失败
            if not task.sora_task_id:
                print(f"No sora_task_id found, task failed at API call stage")
                SoraService._fail_task_final(task_id, "Failed to get task ID from API")
                return

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {SORA_API_KEY}"
            }

            # 开始重试循环
            for attempt in range(1, MAX_RETRY_ATTEMPTS + 1):
                print(f"Retry attempt {attempt}/{MAX_RETRY_ATTEMPTS} for task {task_id}")
                
                try:
                    # 调用结果查询接口
                    payload = {"id": task.sora_task_id}
                    response = requests.post(
                        SORA_RESULT_URL,
                        headers=headers,
                        json=payload,
                        timeout=30
                    )

                    if response.status_code == 200:
                        result = response.json()
                        
                        # 检查业务层返回
                        if result.get("code") == 0:
                            data = result.get("data", {})
                            
                            # 更新任务状态
                            task.refresh_from_db()
                            
                            # 更新进度
                            if 'progress' in data:
                                task.progress = data['progress']
                                task.save()
                            
                            # 检查任务状态
                            task_status = data.get('status')
                            
                            # Calculate generation time if available
                            if 'start_time' in data and 'end_time' in data:
                                try:
                                    start_ts = float(data['start_time'])
                                    end_ts = float(data['end_time'])
                                    task.generation_time = end_ts - start_ts
                                except (ValueError, TypeError):
                                    pass
                            
                            if task_status == 'succeeded':
                                # 🎉 成功生成！
                                print(f"Task {task_id} succeeded on retry attempt {attempt}")
                                task.status = 'SUCCESS'
                                
                                # 下载并保存视频
                                if 'results' in data and len(data['results']) > 0:
                                    video_url = data['results'][0]['url']
                                    SoraService._download_and_save_video(task, video_url)
                                
                                task.save()
                                print(f"Task {task_id} completed successfully after retry")
                                return  # 成功，退出
                            
                            elif task_status == 'failed':
                                # API明确返回失败
                                failure_reason = data.get('failure_reason', 'Unknown failure')
                                print(f"Task {task_id} confirmed failed by API: {failure_reason}")
                                task.save() # Save generation time if calculated
                                SoraService._fail_task_final(task_id, failure_reason)
                                return  # 确认失败，退出
                            
                            elif task_status in ['pending', 'processing']:
                                # 还在处理中，继续等待
                                print(f"Task {task_id} still processing (status: {task_status})")
                            
                        elif result.get("code") == -22:
                            # 任务不存在
                            print(f"Task {task_id} not found in API system")
                            SoraService._fail_task_final(task_id, "Task not found in API system")
                            return
                
                except Exception as retry_error:
                    print(f"Retry attempt {attempt} error: {str(retry_error)}")
                
                # 如果不是最后一次尝试，等待后继续
                if attempt < MAX_RETRY_ATTEMPTS:
                    print(f"Waiting {RETRY_INTERVAL} seconds before next retry...")
                    time.sleep(RETRY_INTERVAL)
            
            # 所有重试都用完了，仍未成功
            print(f"Task {task_id} failed after {MAX_RETRY_ATTEMPTS} retry attempts")
            SoraService._fail_task_final(
                task_id, 
                "Generation failed"
            )
            
        except Exception as e:
            print(f"Retry mechanism error for task {task_id}: {str(e)}")
            SoraService._fail_task_final(task_id, str(e))

    @staticmethod
    def _download_and_save_video(task, video_url):
        """
        【新增方法】下载并保存视频到FileField
        """
        print(f"Downloading video from: {video_url}")
        try:
            video_response = requests.get(video_url, timeout=30)
            
            if video_response.status_code == 200:
                temp_file_name = f"sora_result_{task.id}.mp4"
                task.result_file.save(
                    temp_file_name,
                    ContentFile(video_response.content),
                    save=True
                )
                print(f"Video saved successfully for task {task.id}")
            else:
                print(f"Failed to download video: Status {video_response.status_code}")
                
        except Exception as download_error:
            print(f"Download exception: {str(download_error)}")

    @staticmethod
    def _fail_task(task_id, reason):
        """
        【已弃用】原失败方法，现在由 _retry_check_task 接管
        保留此方法以兼容其他调用
        """
        SoraService._fail_task_final(task_id, reason)

    @staticmethod
    def _sanitize_error(reason):
        """
        【新增方法】清洗错误信息，隐藏技术细节
        """
        technical_keywords = [
            "HTTPSConnectionPool",
            "SSLError",
            "Max retries exceeded",
            "Failed to get task ID",
            "Connection refused",
            "RemoteDisconnected",
            "Read timed out",
            "IncompleteRead",
            "[Errno",
            "violation of protocol",
            "Caused by"
        ]
        
        # Check if the reason contains any technical keywords
        for keyword in technical_keywords:
            if keyword in reason:
                return "生成失败：网络连接异常或服务繁忙，请稍后重试"
                
        # If it looks like a raw generic exception string?
        if reason.startswith("Exception:"):
             # Sometimes we want to hide generic exceptions too if they leak internals
             pass

        return reason

    @staticmethod
    def _fail_task_final(task_id, reason):
        """
        【新增方法】最终确认失败，退还积分
        """
        try:
            # Log full error for backend debugging
            print(f"[ERROR] Task {task_id} failing. Raw reason: {reason}")
            
            sanitized_reason = SoraService._sanitize_error(reason)
            
            task = VideoTask.objects.get(id=task_id)
            if task.status != 'FAILED':
                task.status = 'FAILED'
                task.failure_reason = sanitized_reason
                task.save()

                # 退还积分
                from users.models import CreditTransaction
                with transaction.atomic():
                    task.user.refresh_from_db()
                    
                    # Refund based on model
                    if task.model == 'sora2-pro-c2':
                        refund_amount = 500
                    elif task.model in ['sora2-pro', 'sora2-pro-c1']:
                        refund_amount = 300
                    else:
                        refund_amount = 30

                    task.user.credits += refund_amount
                    task.user.save()
                    
                    CreditTransaction.objects.create(
                        user=task.user,
                        amount=refund_amount,
                        balance_after=task.user.credits,
                        description=f"Refund for failed video task #{task.id} (Model: {task.model})"
                    )
                
                print(f"Task {task_id} failed (User view: {sanitized_reason}) and {refund_amount} credits refunded")
                
        except Exception as e:
            print(f"Error failing task: {str(e)}")

    @staticmethod
    def _handle_apimart_task(task_id, prompt, ratio, duration, ref_image, model):
        """Handle execution via Apimart API"""
        print(f"Starting Apimart task for {task_id} with model {model}")
        task = VideoTask.objects.get(id=task_id)
        task.status = 'PROCESSING'
        task.save()
        
        headers = {
            "Authorization": f"Bearer {APIMART_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model, # Use the model passed in (sora-2 or sora-2-pro)
            "prompt": prompt,
            "duration": duration,
            "aspect_ratio": ratio,
            "private": True
        }
        
        if ref_image:
             # Apimart expects array
            payload["image_urls"] = [ref_image]
            
        try:
            response = requests.post(APIMART_API_URL, headers=headers, json=payload, timeout=60)
            
            if response.status_code != 200:
                 raise Exception(f"Apimart API Error: {response.status_code} - {response.text}")
                 
            data = response.json()
            # Expect: {'code': 200, 'data': [{'status': 'submitted', 'task_id': '...'}]}
            # Or {'code': 200, 'data': {'task_id': ...}} depending on exact response.
            # User example: {'code': 200, 'data': [{'status': 'submitted', 'task_id': 'task_...'}]}
            # It's a list in data?
            
            task_data = None
            if isinstance(data.get('data'), list):
                 task_data = data['data'][0]
            elif isinstance(data.get('data'), dict):
                 task_data = data['data']
            else:
                 raise Exception(f"Unexpected response format: {data}")
                 
            apimart_task_id = task_data.get('task_id')
            if not apimart_task_id:
                 raise Exception("No task_id returned")
                 
            task.sora_task_id = apimart_task_id
            task.save()
            
            # Start Polling
            SoraService._poll_apimart_task(task_id, apimart_task_id)
            
        except Exception as e:
            print(f"Apimart submission error: {str(e)}")
            SoraService._fail_task_final(task_id, str(e))

    @staticmethod
    def _poll_apimart_task(task_id, apimart_task_id):
        """Poll Apimart status up to 15 minutes"""
        print(f"Polling Apimart task {apimart_task_id} for VideoTask {task_id}")
        
        headers = {
            "Authorization": f"Bearer {APIMART_API_KEY}"
        }
        
        # Optimize for faster feedback: Poll every 10s
        # 15 minutes total timeout coverage: 15 * 60 / 10 = 90 polls
        MAX_POLLS = 90
        INTERVAL = 10
        
        for attempt in range(MAX_POLLS):
            try:
                task = VideoTask.objects.get(id=task_id)
                url = f"{APIMART_TASK_URL}/{apimart_task_id}"
                
                response = requests.get(url, headers=headers, timeout=30)
                
                if response.status_code != 200:
                    print(f"Poll error: {response.status_code}")
                    time.sleep(INTERVAL)
                    continue
                    
                res_json = response.json()
                # User example: {'code': 200, 'data': {'created': ..., 'status': 'processing', 'progress': 90}}
                # Completed: {'result': {'videos': [{'url': [...]}]}, 'status': 'completed'}
                
                if res_json.get('code') == 200:
                    data = res_json.get('data', {})
                    status_str = data.get('status')
                    
                    # Update Progress
                    if 'progress' in data:
                        task.progress = data['progress']
                        task.save()
                        
                    if status_str == 'completed':
                        # Capture actual generation time if available (in seconds)
                        if 'actual_time' in data:
                            task.generation_time = data['actual_time']

                        result = data.get('result', {})
                        videos = result.get('videos', [])
                        if videos and len(videos) > 0:
                            # It's a list of objects or just string?
                            # Example: 'videos': [{'expires_at': ..., 'url': ['http...']}]
                            # Video url is a list? 'url': ['...']
                            video_info = videos[0]
                            video_url_list = video_info.get('url', [])
                            if video_url_list:
                                final_url = video_url_list[0] if isinstance(video_url_list, list) else video_url_list
                                
                                task.status = 'SUCCESS'
                                SoraService._download_and_save_video(task, final_url)
                                task.save()
                                print(f"Apimart task {task_id} success. Time: {task.generation_time}s")
                                return
                        else:
                             # Completed but no video?
                             raise Exception("Completed but no video result found")
                             
                    elif status_str == 'failed':
                        error = data.get('error', {})
                        # err_type = error.get('type', 'Unknown Type') # Removed as per request
                        err_msg = error.get('message', 'Unknown Error')
                        
                        # Format: "生成失败：Message"
                        fail_reason = f"生成失败：{err_msg}"
                        
                        print(f"Apimart task {task_id} failed: {fail_reason}")
                        SoraService._fail_task_final(task_id, fail_reason)
                        return
                        
                    elif status_str == 'cancelled':
                         SoraService._fail_task_final(task_id, "生成失败：任务被取消")
                         return
                
                
            except Exception as e:
                # Catch connection errors/timeouts and continue polling
                print(f"Poll attempt {attempt} error (network/timeout): {str(e)}")
                # Do not fail immediately on network error, just wait for next poll
                if attempt == MAX_POLLS - 1:
                     SoraService._fail_task_final(task_id, "Generation failed") # Generic error message
                     return
            
            time.sleep(INTERVAL)
            
        # If loop finishes without return
        SoraService._fail_task_final(task_id, "Generation timeout")

    @staticmethod
    def _handle_wuyin_task(task_id, prompt, ratio, duration, ref_image):
        """Handle execution via Wuyin Keji API (sora2pro interface)"""
        print(f"Starting Wuyin Keji task for {task_id}")
        task = VideoTask.objects.get(id=task_id)
        task.status = 'PROCESSING'
        task.save()
        
        headers = {
            "Authorization": WUYIN_API_KEY,
            "Content-Type": "application/x-www-form-urlencoded;charset:utf-8;"
        }
        
        # Request parameters: prompt, aspectRatio, duration, url (optional ref image)
        payload = {
            "prompt": prompt,
            "aspectRatio": ratio,
            "duration": str(duration)
        }
        
        if ref_image:
            # Check if ref_image is base64 or URL. 
            # Usually front-end sends base64 for upload, but API expects URL.
            # If it's a local file path/URL, pass it. 
            # Assuming ref_image is a URL as per backend logic or handled elsewhere.
            payload["url"] = ref_image
            
        try:
            # Wuyin Keji uses x-www-form-urlencoded
            response = requests.post(WUYIN_SUBMIT_URL, headers=headers, data=payload, timeout=60)
            
            if response.status_code != 200:
                 raise Exception("生成失败：API服务响应异常")
                 
            data = response.json()
            if data.get("code") != 200:
                msg = data.get("msg", "未知错误")
                raise Exception(f"生成失败：{msg}")
                
            wuyin_task_id = data["data"]["id"]
            task.sora_task_id = wuyin_task_id
            task.save()
            
            # Start Polling
            SoraService._poll_wuyin_task(task_id, wuyin_task_id)
            
        except Exception as e:
            print(f"Wuyin submission error: {str(e)}")
            SoraService._fail_task_final(task_id, str(e))

    @staticmethod
    def _poll_wuyin_task(task_id, wuyin_task_id):
        """Poll Wuyin Keji status every 30s"""
        print(f"Polling Wuyin task {wuyin_task_id} for VideoTask {task_id}")
        
        headers = {
            "Authorization": WUYIN_API_KEY,
            "Content-Type": "application/x-www-form-urlencoded;charset:utf-8;"
        }
        
        # Optimize for faster feedback: Poll every 10s
        # 10 minutes coverage: 10 * 60 / 10 = 60 polls
        MAX_POLLS = 120 
        INTERVAL = 10 
        
        start_time = time.time()
        
        for attempt in range(MAX_POLLS):
            try:
                task = VideoTask.objects.get(id=task_id)
                params = {"id": wuyin_task_id}
                
                response = requests.get(WUYIN_DETAIL_URL, headers=headers, params=params, timeout=30)
                
                if response.status_code != 200:
                    print(f"Wuyin Poll error: {response.status_code}")
                    time.sleep(INTERVAL)
                    continue
                    
                res_json = response.json()
                if res_json.get('code') == 200:
                    data = res_json.get('data', {})
                    status_int = data.get('status')
                    # 0:排队中，1:成功，2:失败, 3:生成中
                    
                    if status_int == 1:
                        final_url = data.get('remote_url')
                        if final_url:
                            task.status = 'SUCCESS'
                            # Record generation time
                            task.generation_time = round(time.time() - start_time, 2)
                            SoraService._download_and_save_video(task, final_url)
                            task.save()
                            print(f"Wuyin task {task_id} success in {task.generation_time}s")
                            return
                        else:
                             raise Exception("Status success but no remote_url")
                             
                    elif status_int == 2:
                        msg = data.get('fail_reason', '未知错误')
                        fail_reason = f"生成失败：{msg}"
                        print(f"Wuyin task {task_id} failed: {fail_reason}")
                        SoraService._fail_task_final(task_id, fail_reason)
                        return
                        
                    elif status_int in [0, 3]:
                         # Ongoing
                         print(f"Wuyin task {task_id} status: {status_int}, attempt {attempt+1}")
                
            except Exception as e:
                print(f"Wuyin Poll attempt {attempt} error: {str(e)}")
                if attempt == MAX_POLLS - 1:
                     SoraService._fail_task_final(task_id, str(e))
                     return
            
            time.sleep(INTERVAL)
            
        SoraService._fail_task_final(task_id, "Generation timeout")

    # ============================================================
    # 以下是 Prompt 生成相关方法，保持不变
    # ============================================================
    
    @staticmethod
    def start_prompt_generation_task(task_id):
        """启动异步提示词生成任务"""
        thread = threading.Thread(target=SoraService._handle_prompt_task, args=(task_id,))
        thread.start()

    @staticmethod
    def _handle_prompt_task(task_id):
        from .models import PromptTask, PromptHistory
        try:
            task = PromptTask.objects.get(id=task_id)
            task.status = 'PROCESSING'
            task.save()
            
            # 模拟耗时或直接调用
            # 实际调用 OpenAI
            optimized_prompt = SoraService._generate_prompt_logic(
                task.user, task.raw_prompt, task.style, task.language, task.duration
            )
            
            # 更新任务状态
            task.optimized_prompt = optimized_prompt
            task.status = 'SUCCESS'
            task.save()
            
            # 可选：创建历史记录，保持兼容性
            PromptHistory.objects.create(
                user=task.user,
                raw_prompt=task.raw_prompt,
                style=task.style,
                optimized_prompt=optimized_prompt,
                credits_used=getattr(settings, 'PROMPT_GENERATION_COST', 20)
            )
            
        except Exception as e:
            print(f"Prompt task failed: {str(e)}")
            try:
                task = PromptTask.objects.get(id=task_id)
                task.status = 'FAILED'
                task.failure_reason = str(e)
                task.save()
                
                # 退还积分
                with transaction.atomic():
                    from users.models import CreditTransaction
                    cost = getattr(settings, 'PROMPT_GENERATION_COST', 20)
                    task.user.refresh_from_db()
                    task.user.credits += cost
                    task.user.save()
                    
                    CreditTransaction.objects.create(
                        user=task.user,
                        amount=cost,
                        balance_after=task.user.credits,
                        description=f"Refund for failed prompt task #{task.id}"
                    )
            except:
                pass

    @staticmethod
    def _generate_prompt_logic(user, raw_prompt, style, language, duration):
        """实际的 OpenAI 调用逻辑 (同步)"""
        from django.conf import settings
        
        system_content = (
            f"You are a professional video prompt engineer for Sora AI. "
            f"Your task is to transform user's rough ideas into detailed, cinematic video generation prompts. "
            f"Style requirement: {style}. "
            f"Output language: {language}. "
            f"Target video duration: {duration}. "
            f"Requirements: "
            f"1. Make it detailed and specific "
            f"2. Include camera movements and angles "
            f"3. Describe lighting and atmosphere "
            f"4. Add technical details when appropriate "
            f"5. Keep it clear and well-structured "
            f"6. Include the duration requirement in the prompt naturally if relevant, or just ensure the description fits the {duration} length. "
            f"7. Output ONLY the optimized prompt text, no explanations."
            '''参考提示词如下：
            Style & Tone
            Live-action family short scene, British home realism. High-energy cute confrontation. Feels like a TV sitcom moment captured naturally. Clear audio, strong emotional contrast, playful but intense. Not vlog-style, not staged for camera.

            Scene Description
            A bright British living room in daytime.
            Soft daylight pours in through a window.
            A thick, soft carpet covers the floor.

            At the center of the frame, a 2-year-old chubby British toddler is kneeling on the carpet, leaning forward with both hands on the floor, body tense and expressive.
            Directly in front of him sits a small, friendly corgi, ears up, alert but harmless.

            They are very close, face to face, locked in a noisy standoff.

            The toddler cannot speak words — only loud, emotional early vocal sounds.
            The corgi reacts instinctively, barking loudly but playfully, never aggressive.

            Cinematography

            Camera shot: medium-wide shot, eye level with the toddler

            Framing: toddler and corgi both centered, facing each other, always in frame

            Camera movement: minimal handheld drift, TV-drama realism

            Depth of field: moderate, subjects sharp, background softly blurred

            Lighting: soft natural daylight with warm indoor fill

            Mood: playful conflict, high tension, cute chaos

            Actions & Timing (15s total)

            0–3s
            The toddler drops into a firm kneeling position, leans forward suddenly, and shouts loudly with baby sounds.

            3–7s
            The corgi barks back loudly, ears perked, body leaning slightly forward.
            The toddler answers immediately, even louder, pounding one hand on the carpet.

            7–11s
            The toddler squeals at full volume, face intense but not scared.
            The corgi responds with rapid, loud barks, tail wagging — energetic, not aggressive.

            11–15s
            Both pause for a split second, staring each other down.
            Then they erupt together — loud baby yelling versus loud playful barking — the peak of the confrontation.

            Vocalizations / Audio Cues
            (No real words, no subtitles)

            Toddler (very loud, emotional):
            “AH! AH! EH! DAAAH!”

            Corgi (loud but friendly):
            “WOOF! WOOF!”
            “RAFF! RAFF!”
            “Wuh-woof!”

            Audio Notes

            Baby vocalizations clearly louder than room ambience

            Dog barks strong and crisp, non-threatening

            No human speech

            No music

            Natural indoor acoustics

            Behavior & Safety Constraints

            No biting, no lunging

            No real words from the toddler

            No one looks into the camera

            Both remain face to face

            Feels like actors in a short TV scene
            
            '''
        )

        try:
            print(f"Generating refined prompt for user {user.id}")
            # ... calls ...
            client = OpenAI(
                api_key=settings.OPENAI_API_KEY,
                base_url=settings.OPENAI_BASE_URL
            )
            chat_completion_res = client.chat.completions.create(
                model="gpt-5.1",
                messages=[
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": raw_prompt}
                ],
                max_completion_tokens=4096,
            )

            optimized_prompt = chat_completion_res.choices[0].message.content.strip()
            return optimized_prompt

        except Exception as e:
            raise e

    @staticmethod
    def start_chat_assistant_task(task_id):
        """启动异步大模型对话任务"""
        thread = threading.Thread(target=SoraService._handle_chat_task, args=(task_id,))
        thread.start()

    @staticmethod
    def _handle_chat_task(task_id):
        from .models import PromptTask, PromptHistory
        try:
            task = PromptTask.objects.get(id=task_id)
            task.status = 'PROCESSING'
            task.save()
            
            # GPT-5.1 调用
            response_text = SoraService._generate_chat_logic(task.user, task.raw_prompt)
            
            # 更新任务状态
            task.optimized_prompt = response_text
            task.status = 'SUCCESS'
            task.save()
            
            # 创建历史记录
            cost = getattr(settings, 'PROMPT_GENERATION_COST', 20)
            PromptHistory.objects.create(
                user=task.user,
                raw_prompt=task.raw_prompt,
                style='Chat',
                language='N/A',
                optimized_prompt=response_text,
                credits_used=cost
            )
            
        except Exception as e:
            print(f"Chat task failed: {str(e)}")
            try:
                task = PromptTask.objects.get(id=task_id)
                task.status = 'FAILED'
                task.failure_reason = str(e)
                task.save()
                
                # 退还积分
                with transaction.atomic():
                    from users.models import CreditTransaction
                    cost = getattr(settings, 'PROMPT_GENERATION_COST', 20)
                    task.user.refresh_from_db()
                    task.user.credits += cost
                    task.user.save()
                    
                    CreditTransaction.objects.create(
                        user=task.user,
                        amount=cost,
                        balance_after=task.user.credits,
                        description=f"Refund for failed chat task #{task.id}"
                    )
            except:
                pass

    @staticmethod
    def _generate_chat_logic(user, prompt):
        """GPT-5.1 调用逻辑 (无系统提示词)"""
        from django.conf import settings
        
        try:
            print(f"Generating chat response for user {user.id}")
            client = OpenAI(
                api_key=settings.OPENAI_API_KEY,
                base_url=settings.OPENAI_BASE_URL
            )
            chat_completion_res = client.chat.completions.create(
                model="gpt-5.1",
                messages=[
                    {"role": "system", "content": '你是一个大模型对话助手。请务必以纯文本形式回答，不要使用任何 Markdown 语法（如不要使用 ##, **, ---, [], () 等符号）。请使用简单的换行和空行来分隔段落，确保内容清晰易读。'},
                    {"role": "user", "content": prompt}
                ],
                max_completion_tokens=4096,
            )

            result = chat_completion_res.choices[0].message.content.strip()
            return result

        except Exception as e:
            raise e
