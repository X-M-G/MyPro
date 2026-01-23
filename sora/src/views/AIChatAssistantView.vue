<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useVideoStore } from '@/stores/video'
import { useI18n } from 'vue-i18n'
import { 
  Trash2, Zap, User, Bot, Sparkles, Clock, Copy, ChevronDown, ChevronUp,
  Eye, Maximize2, Minimize2, X, Send, Loader2, AlertTriangle, MessageSquare
} from 'lucide-vue-next'
import { toast } from '@/utils/toast'

const videoStore = useVideoStore()
const { t } = useI18n()

const userInput = ref('')
const isProcessing = ref(false)
const errorMsg = ref('')
const showHistory = ref(true)
const selectedHistoryItem = ref<any>(null)
const isModalResultOnly = ref(false)
const isFullScreen = ref(false)
const fullScreenInput = ref('')

const toggleFullScreen = () => {
    if (!isFullScreen.value) {
        fullScreenInput.value = userInput.value
        isFullScreen.value = true
    }
}

const applyFullScreen = () => {
    userInput.value = fullScreenInput.value
    isFullScreen.value = false
}

import { computed } from 'vue'

const chatHistories = computed(() => {
    return videoStore.promptHistories.filter(h => h.style === 'Chat')
})

onMounted(async () => {
    try {
        await videoStore.checkActiveChatTask()
        await videoStore.fetchPromptHistory()
    } catch (error) {
        console.error('Failed to initialize chat:', error)
    }
})

// Watch active task status
watch(() => videoStore.activeChatTask, (task) => {
    if (task) {
        if (task.status === 'PENDING' || task.status === 'PROCESSING') {
            isProcessing.value = true
        } else if (task.status === 'SUCCESS') {
            isProcessing.value = false
        } else if (task.status === 'FAILED') {
            isProcessing.value = false
            errorMsg.value = task.failure_reason || "Chat failed"
        }
    }
}, { deep: true })

async function handleSend() {
    if (!userInput.value || isProcessing.value) return
    
    isProcessing.value = true
    errorMsg.value = ''
    
    try {
        const success = await videoStore.handleAIChat(userInput.value)
        if (success) {
            // Keep userInput as requested
        } else {
            isProcessing.value = false
            errorMsg.value = "Failed to start chat"
        }
    } catch (e: any) {
        isProcessing.value = false
        errorMsg.value = e.message || "An error occurred"
    }
}

function copyText(text: string) {
    navigator.clipboard.writeText(text)
    toast.success(t('common.copied'))
}

function openHistoryDetail(chat: any, resultOnly: boolean = false) {
    selectedHistoryItem.value = chat
    isModalResultOnly.value = resultOnly
}

function closeHistoryDetail() {
    selectedHistoryItem.value = null
    isModalResultOnly.value = false
}

function formatDate(dateString: string) {
    if (!dateString) return ''
    const date = new Date(dateString)
    return date.toLocaleString()
}
</script>

<template>
  <div class="page-container chat-assistant">
    <!-- Full-screen Input Editor Overlay -->
    <Teleport to="body">
      <Transition name="fade">
        <div v-if="isFullScreen" class="fullscreen-editor-overlay">
          <div class="editor-container glass-card">
            <header class="editor-header">
              <div class="header-info">
                <Sparkles :size="20" class="text-primary" />
                <h3>{{ t("chatAssistant.inputLabel") }} - {{ t("common.edit") || "Edit" }}</h3>
              </div>
              <div class="header-actions">
                <button class="btn btn-ghost btn-sm" @click="fullScreenInput = ''">
                  {{ t("common.clear") || "Clear" }}
                </button>
                <button class="btn btn-primary btn-sm" @click="applyFullScreen">
                  {{ t("common.confirm") }}
                </button>
              </div>
            </header>
            <main class="editor-main">
              <textarea
                v-model="fullScreenInput"
                class="fullscreen-textarea"
                :placeholder="t('chatAssistant.inputPlaceholder')"
                autofocus
              ></textarea>
            </main>
          </div>
        </div>
      </Transition>
    </Teleport>

    <header class="page-header animate-fade-up">
       <div class="header-badge">
         <Sparkles :size="16" class="text-primary" />
         <span>GPT-5.1</span>
       </div>
       <h1 class="main-title">{{ t('chatAssistant.title') }}</h1>
       <p class="subtitle">{{ t('chatAssistant.subtitle') }}</p>
       
       <div class="chat-tips glass-card">
         <div class="tip-header">
           <Zap :size="18" class="text-warning" />
           <span>{{ t('chatAssistant.tips.title') }}</span>
         </div>
         <p>{{ t('chatAssistant.tips.desc') }}</p>
       </div>
    </header>

    <div class="chat-main animate-fade-up" style="animation-delay: 0.1s">
      <!-- Top Section: Input and Result -->
      <div class="chat-top-grid">
        <!-- Left: Input Area -->
        <div class="glass-card input-panel">
          <div class="panel-header">
            <Zap :size="18" class="text-primary" />
            <h2>{{ t('chatAssistant.inputLabel') }}</h2>
          </div>
          <div class="input-content">
            <div class="input-wrapper" :class="{ 'focused': userInput }">
              <textarea 
                v-model="userInput" 
                class="chat-textarea" 
                :placeholder="t('chatAssistant.inputPlaceholder')"
                @keydown.enter.exact.prevent="handleSend"
                :disabled="isProcessing"
                rows="12"
              ></textarea>
              
              <button 
                class="btn-expand" 
                @click="toggleFullScreen"
                :title="t('common.expand')"
              >
                <Maximize2 :size="16" />
              </button>
              
              <div class="input-footer">
                <div class="cost-badge">
                  <Zap :size="12" class="text-warning" />
                  <span>20 {{ t('chatAssistant.credits') }}</span>
                </div>
                <button 
                  @click="handleSend" 
                  class="send-btn"
                  :disabled="isProcessing || !userInput.trim()"
                >
                  <Loader2 v-if="isProcessing" class="animate-spin" :size="20" />
                  <Send v-else :size="20" />
                  <span>{{ isProcessing ? t('chatAssistant.sending') : t('chatAssistant.send') }}</span>
                </button>
              </div>
            </div>
            <p v-if="errorMsg" class="error-msg animate-fade-in">
              <AlertTriangle :size="14" /> {{ errorMsg }}
            </p>
          </div>
        </div>

        <!-- Right: Result Area -->
        <div class="glass-card result-panel">
          <div class="panel-header">
            <MessageSquare :size="18" class="text-primary" />
            <h2>{{ isProcessing ? t('chatAssistant.sending') : t('chatAssistant.result') }}</h2>
            <div class="panel-actions">
              <button 
                v-if="videoStore.activeChatTask && videoStore.activeChatTask.optimized_prompt"
                @click="openHistoryDetail(videoStore.activeChatTask, true)" 
                class="btn btn-ghost btn-sm" 
                :title="t('common.expand')"
              >
                <Maximize2 :size="16" />
              </button>
            </div>
          </div>
          <div class="result-content" ref="messageContainer">
            <div v-if="!videoStore.activeChatTask" class="welcome-placeholder">
              <div class="bot-icon">
                <Bot :size="48" />
              </div>
              <p>{{ t('chatAssistant.noHistory') }}</p>
            </div>

            <div v-else class="assistant-response-box animate-fade-in">
               <!-- Generation Loading State -->
               <div v-if="isProcessing && !videoStore.activeChatTask.optimized_prompt" class="thinking-state">
                 <div class="spinner-container">
                   <Loader2 class="animate-spin text-primary" :size="48" />
                   <div class="pulse-ring"></div>
                 </div>
                 <p class="loading-text">{{ t('chatAssistant.sending') }}</p>
               </div>
               
                <!-- AI Response Content -->
                <div v-else-if="videoStore.activeChatTask.optimized_prompt" class="response-text">
                  <pre>{{ videoStore.activeChatTask.optimized_prompt }}</pre>
                  <div class="response-actions">
                    <div class="left-actions">
                      <button @click="copyText(videoStore.activeChatTask.optimized_prompt)" class="action-btn">
                        <Copy :size="14" /> {{ t('common.copy') || 'Copy' }}
                      </button>
                      <button @click="openHistoryDetail(videoStore.activeChatTask, true)" class="action-btn" title="View Result">
                        <Eye :size="14" />
                      </button>
                    </div>
                    <span class="balance-note">-20 {{ t('chatAssistant.credits') }}</span>
                  </div>
                </div>
               
               <!-- Failure State -->
               <div v-else-if="videoStore.activeChatTask.status === 'FAILED'" class="error-text">
                 <AlertTriangle :size="16" />
                 <span>{{ videoStore.activeChatTask.failure_reason || t('common.error') }}</span>
               </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Bottom: History Section -->
      <div class="history-section-wrapper animate-fade-up" style="animation-delay: 0.2s">
        <div class="glass-card history-panel">
          <div class="panel-header history-header clickable" @click="showHistory = !showHistory">
            <div class="title-with-icon">
              <Clock :size="18" class="text-primary" />
              <h2>{{ t('common.history') || 'History' }}</h2>
              <span class="history-count" v-if="chatHistories.length">({{ chatHistories.length }})</span>
            </div>
            <button class="btn btn-ghost btn-sm">
               {{ showHistory ? t('common.hide') : t('common.show') }}
               <ChevronDown :class="{ rotated: !showHistory }" :size="18" />
            </button>
          </div>

          <Transition name="slide">
            <div v-if="showHistory" class="history-content">
              <div v-if="chatHistories.length === 0" class="empty-history">
                <p>{{ t('chatAssistant.noHistory') }}</p>
              </div>
              <div v-else class="history-grid">
                <div v-for="chat in chatHistories" :key="chat.id" class="history-card glass-card">
                  <div class="history-header">
                    <span class="date">{{ formatDate(chat.created_at) }}</span>
                    <div class="history-actions">
                      <button @click="openHistoryDetail(chat, false)" class="action-btn" title="View Detail">
                        <Eye :size="14" />
                      </button>
                      <button @click="copyText(chat.optimized_prompt)" class="action-btn" title="Copy">
                        <Copy :size="14" />
                      </button>
                    </div>
                  </div>
                  <div class="history-body">
                    <div class="history-q">
                      <User :size="14" />
                      <p>{{ chat.raw_prompt }}</p>
                    </div>
                    <div class="history-a">
                      <Bot :size="14" />
                      <pre>{{ chat.optimized_prompt }}</pre>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </Transition>
        </div>
      </div>
    </div>

    <!-- History Detail Modal -->
    <Transition name="fade">
      <div v-if="selectedHistoryItem" class="modal-overlay" @click.self="closeHistoryDetail">
        <div class="modal-content glass-card animate-scale-up">
          <div class="modal-header">
            <div class="title-info">
              <Clock :size="18" class="text-primary" />
              <h3>{{ t('chatAssistant.conversationDetail') }}</h3>
              <span class="modal-date">{{ formatDate(selectedHistoryItem.created_at) }}</span>
            </div>
            <button @click="closeHistoryDetail" class="close-btn">
              <X :size="20" />
            </button>
          </div>
          <div class="modal-body">
            <div v-if="!isModalResultOnly" class="detail-section">
              <div class="section-label">
                <User :size="16" />
                <span>{{ t('chatAssistant.inputLabel') }}</span>
              </div>
              <div class="section-content question-content">
                {{ selectedHistoryItem.raw_prompt }}
              </div>
            </div>
            <div class="detail-section">
              <div class="section-label">
                <Bot :size="16" />
                <span>{{ t('chatAssistant.result') }}</span>
              </div>
              <div class="section-content response-content">
                <pre>{{ selectedHistoryItem.optimized_prompt }}</pre>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button @click="copyText(selectedHistoryItem.optimized_prompt)" class="btn btn-primary">
              <Copy :size="16" /> {{ t('common.copy') || 'Copy Result' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.chat-assistant {
  padding-top: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 2.5rem;
}

.header-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: var(--bg-200);
  border: 1px solid var(--bg-300);
  border-radius: 12px;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-main);
  margin-bottom: 1.5rem;
}

.subtitle {
  font-size: 1.125rem;
  margin-bottom: 1.5rem;
  color: var(--color-text-secondary);
}

.chat-tips {
  display: inline-block;
  max-width: 650px;
  padding: 1rem 1.5rem;
  background: var(--bg-200);
  border: 1px solid var(--bg-300);
  text-align: left;
}

.tip-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  color: var(--color-text-main);
}

.chat-tips p {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  line-height: 1.6;
  margin: 0;
}

/* New Split Layout Styles */
.chat-main {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.chat-top-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  height: 600px; /* Fixed height for equal panel sizes */
}

@media (max-width: 1100px) {
  .chat-top-grid {
    grid-template-columns: 1fr;
  }
}

.input-panel, .result-panel, .history-panel {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.panel-header {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: rgba(255, 255, 255, 0.5);
}

.panel-header h2 {
  font-size: 1.1rem;
  font-weight: 700;
  margin: 0;
  flex: 1;
}

.panel-header.clickable {
  cursor: pointer;
  transition: background 0.2s;
}

.panel-header.clickable:hover {
  background: rgba(248, 250, 252, 0.8);
}

.input-content, .result-content {
  padding: 1.5rem;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.input-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  border: 2px solid var(--bg-300);
  border-radius: 16px;
  padding: 1rem;
  background: var(--bg-100);
  transition: all 0.3s ease;
}

.input-wrapper.focused {
  border-color: var(--color-primary-glow);
  background: white;
  box-shadow: 0 4px 12px rgba(0, 119, 194, 0.1);
}

.input-wrapper {
  position: relative;
}

.btn-expand {
  position: absolute;
  top: 10px;
  right: 12px;
  background: rgba(255, 255, 255, 0.4);
  border: 1px solid rgba(186, 230, 253, 0.5);
  border-radius: 6px;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--color-primary);
  transition: all 0.2s;
  z-index: 10;
}

.btn-expand:hover {
  background: rgba(255, 255, 255, 0.8);
  border-color: var(--color-primary-glow);
}

.chat-textarea {
  flex: 1;
  width: 100%;
  border: none;
  background: transparent;
  resize: none;
  font-family: inherit;
  font-size: 1rem;
  color: var(--color-text-main);
  margin-bottom: 1rem;
  line-height: 1.6;
}

.chat-textarea:focus { outline: none; }

.input-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  border-top: 1px solid var(--color-border);
}

.cost-badge {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  font-weight: 600;
}

.result-content {
  background: rgba(248, 250, 252, 0.4);
  flex: 1;
  overflow-y: auto;
  border-bottom-left-radius: inherit;
  border-bottom-right-radius: inherit;
}

.welcome-placeholder {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  color: var(--color-text-muted);
}

.bot-icon {
  width: 64px;
  height: 64px;
  background: var(--bg-200);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-primary);
  border: 1px solid var(--bg-300);
}

.user-question-preview {
  display: flex;
  gap: 0.75rem;
  padding: 1rem;
  background: var(--bg-200);
  border-radius: 12px;
  margin-bottom: 1.5rem;
  border: 1px solid var(--bg-300);
}

.user-question-preview p {
  font-size: 0.9rem;
  font-weight: 600;
  margin: 0;
  color: var(--color-text-main);
}

.assistant-response-box {
  background: white;
  padding: 1.5rem;
  border-radius: 16px;
  border: 1px solid var(--color-border);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
}

.thinking-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  gap: 1.5rem;
  color: var(--color-text-muted);
}

.spinner-container {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.pulse-ring {
  position: absolute;
  width: 64px;
  height: 64px;
  border-radius: 50%;
  border: 2px solid var(--color-primary);
  opacity: 0;
  animation: ring-pulse 2s cubic-bezier(0.24, 0, 0.38, 1) infinite;
}

@keyframes ring-pulse {
  0% { transform: scale(0.6); opacity: 0; }
  50% { opacity: 0.3; }
  100% { transform: scale(1.4); opacity: 0; }
}

.loading-text {
  font-size: 1.1rem;
  font-weight: 600;
  background: linear-gradient(90deg, var(--color-text-muted) 0%, var(--color-primary) 50%, var(--color-text-muted) 100%);
  background-size: 200% auto;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  animation: shine 3s linear infinite;
}

@keyframes shine {
  to { background-position: 200% center; }
}

.response-text pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: inherit;
  font-size: 1rem;
  line-height: 1.8;
  margin: 0;
  color: var(--color-text-main);
}

.response-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--color-border);
}

.left-actions {
  display: flex;
  gap: 0.75rem;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: none;
  border: 1px solid var(--color-border);
  padding: 0.5rem 0.8rem;
  border-radius: 8px;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
  background: var(--bg-100);
}

.balance-note {
  font-size: 0.8rem;
  color: var(--color-text-muted);
  font-weight: 700;
}

/* History Grid Styles */
.history-content {
  padding: 2rem;
  background: #fcfcfc;
}

.history-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.5rem;
}

.history-card {
  padding: 1.25rem;
  border-color: var(--bg-300);
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px dashed var(--bg-300);
}

.date {
  font-size: 0.75rem;
  color: var(--color-text-muted);
  font-weight: 600;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.history-header .btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.history-header .rotated {
  transform: rotate(-90deg);
}

/* Existing styles */
.history-q, .history-a {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

.history-q p {
  font-size: 0.875rem;
  font-weight: 700;
  color: var(--color-text-main);
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.history-a pre {
  flex: 1;
  font-size: 0.85rem;
  color: var(--color-text-secondary);
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: inherit;
  margin: 0;
  max-height: 100px;
  overflow: hidden;
  position: relative;
}

.history-a pre::after {
  content: "";
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 30px;
  background: linear-gradient(to top, white, transparent);
}

.history-count {
  font-size: 0.9rem;
  color: var(--color-text-muted);
  font-weight: 400;
}

.rotated {
  transform: rotate(-90deg);
}

.slide-enter-active, .slide-leave-active {
  transition: all 0.3s ease-out;
  max-height: 2000px;
}
.slide-enter-from, .slide-leave-to {
  max-height: 0;
  opacity: 0;
  overflow: hidden;
}

.panel-actions {
  display: flex;
  gap: 0.5rem;
}

/* Full-screen Editor Styles */
.fullscreen-editor-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 3000;
  padding: 2rem;
}

.editor-container {
  width: 100%;
  max-width: 1200px;
  height: 0;
  min-height: 80vh;
  background: white;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 30px 60px rgba(0, 0, 0, 0.3);
  border-radius: 24px;
}

.editor-header {
  padding: 1.5rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--color-border);
  background: var(--bg-100);
}

.header-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.header-info h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-text-main);
}

.header-actions {
  display: flex;
  gap: 1rem;
}

.editor-main {
  flex: 1;
  padding: 2rem;
  background: white;
}

.fullscreen-textarea {
  width: 100%;
  height: 100%;
  border: none;
  resize: none;
  font-family: inherit;
  font-size: 1.25rem;
  line-height: 1.8;
  color: var(--color-text-main);
  background: transparent;
  padding: 1rem;
}

.fullscreen-textarea:focus {
  outline: none;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 2rem;
}

.modal-content {
  width: 100%;
  max-width: 800px;
  max-height: 90vh;
  background: white;
  border-radius: 24px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 30px 60px rgba(0, 0, 0, 0.15);
}

.modal-header {
  padding: 1.5rem 2rem;
  border-bottom: 1px solid var(--color-border);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--bg-100);
}

.title-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.title-info h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 700;
}

.modal-date {
  font-size: 0.875rem;
  color: var(--color-text-muted);
}

.close-btn {
  background: none;
  border: none;
  color: var(--color-text-muted);
  cursor: pointer;
  transition: all 0.2s;
  padding: 0.5rem;
  border-radius: 50%;
}

.close-btn:hover {
  background: var(--bg-200);
  color: var(--color-text-main);
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.detail-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.section-label {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-weight: 700;
  color: var(--color-text-main);
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.section-content {
  padding: 1.25rem;
  border-radius: 12px;
  background: var(--bg-100);
  border: 1px solid var(--bg-300);
  font-size: 1rem;
  line-height: 1.7;
}

.question-content {
  font-weight: 600;
  color: var(--color-text-main);
}

.response-content pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: inherit;
  margin: 0;
  color: var(--color-text-main);
}

.modal-footer {
  padding: 1.25rem 2rem;
  border-top: 1px solid var(--color-border);
  display: flex;
  justify-content: flex-end;
  background: var(--bg-100);
}

.history-actions {
  display: flex;
  gap: 0.5rem;
}

.error-msg {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #dc3545;
  font-size: 0.875rem;
  margin-top: 1rem;
}

.send-btn {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.625rem 1.25rem;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: 12px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}

.send-btn:hover:not(:disabled) {
  background: var(--color-primary-hover);
  transform: translateY(-1px);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Animations */
.animate-scale-up {
  animation: scaleUp 0.3s ease-out;
}

@keyframes scaleUp {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
