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

  // Prompt & Chat Task persistence
  const activePromptTask = ref<any>(null)
  const activeChatTask = ref<any>(null)

  const authStore = useAuthStore()

  // 提示词历史相关状态
  const promptHistories = ref<PromptHistory[]>([])
  const historyLoading = ref(false)


  async function generateVideo(prompt: string, ratio: string, duration: number, refImage: string | null = null, model: string = 'sora2') {
    loading.value = true
    error.value = null

    try {
      const payload: any = {
        prompt,
        ratio,
        duration,
        ref_image: refImage,
        model
      }

      const response = await api.post('videos/generate/', payload, {
        timeout: 30000
      })

      activeTask.value = response.data
      tasks.value.unshift(response.data)

      if (authStore.user) {
        const cost = model === 'sora2-pro' ? 300 : 30
        authStore.user.credits -= cost
      }

      pollTask(response.data.id)
      return true

    } catch (e: any) {
      console.error("Generate Video Error Debug:", e)

      if (e.code === 'ECONNABORTED' || e.message?.includes('timeout')) {
        error.value = "Request timed out. The server is busy, please try again."
        return false
      }

      if (e.response && e.response.data) {
        if (e.response.data.error) {
          error.value = e.response.data.error
        }
        else if (e.response.data.detail) {
          error.value = e.response.data.detail
        }
        else {
          error.value = typeof e.response.data === 'string'
            ? e.response.data
            : "Server returned an error. Check console for details."
        }
      }
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

  async function fetchHistory(force = false) {
    if (!force && tasks.value.length > 0) {
      api.get('videos/list/').then(response => {
        tasks.value = response.data
        tasks.value.forEach(task => {
          if (task.status === 'PENDING' || task.status === 'PROCESSING') {
            pollTask(task.id)
          }
        })
      })
      return
    }

    loading.value = true
    try {
      const response = await api.get('videos/list/')
      tasks.value = response.data

      tasks.value.forEach(task => {
        if (task.status === 'PENDING' || task.status === 'PROCESSING') {
          pollTask(task.id)
        }
      })
    } finally {
      loading.value = false
    }
  }

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

  async function checkActiveChatTask() {
    try {
      const response = await api.get('videos/ai-chat/active/')
      if (response.data && response.data.id) {
        activeChatTask.value = response.data
        pollChatTask(response.data.id)
      } else {
        activeChatTask.value = null
      }
    } catch (e) {
      console.error("Failed to check active chat task:", e)
    }
  }

  async function handleAIChat(prompt: string) {
    try {
      activeChatTask.value = null
      const response = await api.post('videos/ai-chat/generate/', { prompt })

      if (response.data.task_id) {
        activeChatTask.value = {
          id: response.data.task_id,
          status: 'PENDING',
          raw_prompt: prompt
        }
        pollChatTask(response.data.task_id)
        await authStore.fetchUser()
        return true
      }
      return false
    } catch (e: any) {
      console.error(e)
      if (e.response && e.response.data && e.response.data.error) {
        throw new Error(e.response.data.error)
      }
      throw e
    }
  }

  async function optimizePrompt(concept: string, style: string, language: string, duration: string, model: string = 'sora2') {
    try {
      activePromptTask.value = null
      const response = await api.post('videos/prompt/generate/', {
        prompt: concept,
        style,
        language,
        duration,
        model
      })

      if (response.data.task_id) {
        activePromptTask.value = {
          id: response.data.task_id,
          status: 'PENDING',
          raw_prompt: concept
        }
        pollPromptTask(response.data.task_id)
        await authStore.fetchUser()
        return true
      } else {
        return response.data.prompt
      }
    } catch (e: any) {
      console.error(e)
      if (e.response && e.response.data && e.response.data.error) {
        throw new Error(e.response.data.error)
      }
      throw e
    }
  }

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

  async function deletePromptHistory(id: number) {
    try {
      await api.delete(`videos/prompt/history/${id}/`)
      promptHistories.value = promptHistories.value.filter(h => h.id !== id)
    } catch (error: any) {
      console.error('Failed to delete prompt history:', error)
      throw error
    }
  }

  const pollIntervals = new Map<number, number>()
  const promptPollInterval = ref<number | null>(null)
  const chatPollInterval = ref<number | null>(null)

  function pollTask(taskId: number) {
    if (pollIntervals.has(taskId)) return

    // @ts-ignore
    const intervalId = setInterval(async () => {
      try {
        const response = await api.get(`videos/${taskId}/`)
        const task = response.data

        const index = tasks.value.findIndex(t => t.id === task.id)
        if (index !== -1) tasks.value[index] = task
        if (activeTask.value && activeTask.value.id === task.id) activeTask.value = task

        if (task.status === 'SUCCESS' || task.status === 'FAILED') {
          clearInterval(intervalId)
          pollIntervals.delete(taskId)
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
          if (task.status === 'SUCCESS') fetchPromptHistory()
          else authStore.fetchUser()
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

  function pollChatTask(taskId: number) {
    if (chatPollInterval.value) return

    // @ts-ignore
    chatPollInterval.value = setInterval(async () => {
      try {
        const response = await api.get(`videos/prompt/task/${taskId}/`)
        const task = response.data
        activeChatTask.value = task

        if (task.status === 'SUCCESS' || task.status === 'FAILED') {
          if (chatPollInterval.value) {
            clearInterval(chatPollInterval.value)
            chatPollInterval.value = null
          }
          if (task.status === 'SUCCESS') fetchPromptHistory()
          else authStore.fetchUser()
        }
      } catch (e) {
        if (chatPollInterval.value) {
          clearInterval(chatPollInterval.value)
          chatPollInterval.value = null
        }
        activeChatTask.value = null
      }
    }, 2000)
  }

  return {
    tasks,
    activeTask,
    loading,
    error,
    activePromptTask,
    activeChatTask,
    generateVideo,
    fetchHistory,
    checkActivePromptTask,
    checkActiveChatTask,
    optimizePrompt,
    handleAIChat,
    promptHistories,
    historyLoading,
    fetchPromptHistory,
    deletePromptHistory
  }
})