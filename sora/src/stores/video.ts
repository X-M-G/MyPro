import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/utils/api'
import { useAuthStore } from './auth'

export interface PromptHistory {
  id: number
  raw_prompt: string
  style: string
  language: string
  optimized_prompt: string
  credits_used: number
  created_at: string
}

export interface VideoTask {
  id: number
  prompt: string
  status: 'PENDING' | 'PROCESSING' | 'SUCCESS' | 'FAILED'
  result_url: string
  failure_reason?: string
  ratio: string
  duration: number
  created_at: string
  model?: string
}

export const useVideoStore = defineStore('video', () => {
  const tasks = ref<any[]>([])
  const activeTask = ref<any>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Prompt Task persistence
  const activePromptTask = ref<any>(null)

  const authStore = useAuthStore()

  // 提示词历史相关状态
  const promptHistories = ref<PromptHistory[]>([])
  const historyLoading = ref(false)


  async function generateVideo(prompt: string, ratio: string, duration: number, refImage: string | null = null, model: string = 'sora2') {
    loading.value = true
    error.value = null // 重置错误

    try {
      const payload: any = {
        prompt,
        ratio,
        duration,
        ref_image: refImage,
        model
      }

      // 注意：这里建议临时增加 timeout 时间，防止网络波动导致误报超时
      const response = await api.post('videos/generate/', payload, {
        timeout: 30000 // 将超时时间单独延长到 30秒
      })

      activeTask.value = response.data
      tasks.value.unshift(response.data)

      // Deduct credits based on model (300 for sora2-pro, 30 for sora)
      if (authStore.user) {
        const cost = model === 'sora2-pro' ? 300 : 30
        authStore.user.credits -= cost
      }

      pollTask(response.data.id)
      return true

    } catch (e: any) {
      console.error("Generate Video Error Debug:", e) // 方便调试

      // --- 核心修复逻辑 ---

      // 1. 处理超时错误 (没有 response 对象)
      if (e.code === 'ECONNABORTED' || e.message?.includes('timeout')) {
        error.value = "Request timed out. The server is busy, please try again."
        return false
      }

      // 2. 处理后端返回的明确错误 (429, 503, 400 等)
      if (e.response && e.response.data) {
        // 优先读取 backend 返回的 "error" 字段
        if (e.response.data.error) {
          error.value = e.response.data.error
        }
        // Django DRF 有时会返回 "detail" 字段 (例如权限问题)
        else if (e.response.data.detail) {
          error.value = e.response.data.detail
        }
        // 如果返回的是一个对象但没有特定key，尝试序列化显示
        else {
          // 避免显示 [object Object]
          error.value = typeof e.response.data === 'string'
            ? e.response.data
            : "Server returned an error. Check console for details."
        }
      }
      // 3. 处理网络断开等其他无响应错误
      else if (e.message) {
        error.value = e.message
      }
      else {
        error.value = "Unknown error occurred."
      }

      return false
    } finally {
      loading.value = false
    }
  }

  async function fetchHistory() {
    loading.value = true
    try {
      const response = await api.get('videos/list/')
      tasks.value = response.data

      // Resume polling for active tasks
      tasks.value.forEach(task => {
        if (task.status === 'PENDING' || task.status === 'PROCESSING') {
          pollTask(task.id)
        }
      })
    } finally {
      loading.value = false
    }
  }

  // Check for any active prompt generation task on load
  async function checkActivePromptTask() {
    try {
      const response = await api.get('videos/prompt/active/')
      if (response.data && response.data.id) {
        activePromptTask.value = response.data
        pollPromptTask(response.data.id)
      } else {
        activePromptTask.value = null
      }
    } catch (e) {
      console.error("Failed to check active prompt task:", e)
    }
  }

  async function optimizePrompt(concept: string, style: string, language: string, duration: string, model: string = 'sora2') {
    try {
      // Clean up previous active task state
      activePromptTask.value = null

      const response = await api.post('videos/prompt/generate/', {
        prompt: concept,
        style,
        language,
        duration,
        model
      })

      if (response.data.task_id) {
        // Async flow
        activePromptTask.value = {
          id: response.data.task_id,
          status: 'PENDING',
          raw_prompt: concept
        }
        pollPromptTask(response.data.task_id)
        // Credits are deducted on backend start
        await authStore.fetchUser()
        return true // Signal started
      } else {
        // Fallback sync flow (if backend didn't change for some reason, though we changed it)
        return response.data.prompt
      }
    } catch (e: any) {
      console.error(e)
      // Extract error message
      if (e.response && e.response.data && e.response.data.error) {
        throw new Error(e.response.data.error)
      }
      throw e
    }
  }

  // 获取提示词历史记录
  async function fetchPromptHistory(page = 1) {
    historyLoading.value = true
    try {
      const response = await api.get('videos/prompt/history/', {
        params: { page }
      })
      promptHistories.value = response.data.results
      return response.data
    } catch (error: any) {
      console.error('Failed to fetch prompt history:', error)
      throw error
    } finally {
      historyLoading.value = false
    }
  }

  // 删除提示词历史记录
  async function deletePromptHistory(id: number) {
    try {
      await api.delete(`videos/prompt/history/${id}/`)
      // 从本地列表中移除
      promptHistories.value = promptHistories.value.filter(h => h.id !== id)
    } catch (error: any) {
      console.error('Failed to delete prompt history:', error)
      throw error
    }
  }

  const pollIntervals = new Map<number, number>()
  const promptPollInterval = ref<number | null>(null)

  function pollTask(taskId: number) {
    if (pollIntervals.has(taskId)) return

    // @ts-ignore
    const intervalId = setInterval(async () => {
      try {
        const response = await api.get(`videos/${taskId}/`)
        const task = response.data

        // Update local task
        const index = tasks.value.findIndex(t => t.id === task.id)
        if (index !== -1) tasks.value[index] = task
        if (activeTask.value && activeTask.value.id === task.id) activeTask.value = task

        if (task.status === 'SUCCESS' || task.status === 'FAILED') {
          clearInterval(intervalId)
          pollIntervals.delete(taskId)
          // Refresh user credits if failed (refund)
          if (task.status === 'FAILED') authStore.fetchUser()
        }
      } catch (e) {
        clearInterval(intervalId)
        pollIntervals.delete(taskId)
      }
    }, 2000)

    pollIntervals.set(taskId, intervalId)
  }

  function pollPromptTask(taskId: number) {
    if (promptPollInterval.value) return

    // @ts-ignore
    promptPollInterval.value = setInterval(async () => {
      try {
        const response = await api.get(`videos/prompt/task/${taskId}/`)
        const task = response.data

        activePromptTask.value = task

        if (task.status === 'SUCCESS' || task.status === 'FAILED') {
          if (promptPollInterval.value) {
            clearInterval(promptPollInterval.value)
            promptPollInterval.value = null
          }

          if (task.status === 'SUCCESS') {
            // Refresh history
            fetchPromptHistory()
          }
        }
      } catch (e) {
        if (promptPollInterval.value) {
          clearInterval(promptPollInterval.value)
          promptPollInterval.value = null
        }
        activePromptTask.value = null
      }
    }, 2000)
  }

  return {
    tasks,
    activeTask,
    loading,
    error,
    activePromptTask,
    generateVideo,
    fetchHistory,
    checkActivePromptTask,
    optimizePrompt,
    promptHistories,
    historyLoading,
    fetchPromptHistory,
    deletePromptHistory
  }
})