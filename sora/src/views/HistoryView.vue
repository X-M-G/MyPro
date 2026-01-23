<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { useVideoStore } from '@/stores/video'
import type { VideoTask } from '@/stores/video'
import { 
  Check, 
  ChevronUp, 
  VideoOff, 
  Loader2, 
  Copy, 
  X, 
  Maximize2, 
  CircleAlert, 
  ChevronDown,
  History,
  PlayCircle,
  Download
} from 'lucide-vue-next'

// Toast mock since it was imported from a chunk - using console or alert fallback if native toast isn't available
// In a real scenario I'd check if there is a global toast availalble
const toast = {
  error: (msg: string) => console.error(msg),
  success: (msg: string) => console.log(msg)
}

const videoStore = useVideoStore()
const { t } = useI18n()
const router = useRouter()

const showAll = ref(false)
const expandedPrompts = ref(new Set<string | number>())
const copiedId = ref<string | number | null>(null)
const showModal = ref(false)
const selectedVideo = ref<VideoTask | null>(null)

onMounted(() => {
  videoStore.fetchHistory()
})

const filteredTasks = computed(() => {
  const tasks = videoStore.tasks || []
  return showAll.value ? tasks : tasks.filter(task => task.status === 'SUCCESS')
})

const isLongPrompt = (prompt: string) => {
  return prompt && prompt.length > 100
}

const togglePrompt = (id: string | number) => {
  if (expandedPrompts.value.has(id)) {
    expandedPrompts.value.delete(id)
  } else {
    expandedPrompts.value.add(id)
  }
}

const copyToClipboard = async (text: string, id: string | number) => {
  if (text) {
    try {
      await navigator.clipboard.writeText(text)
      setCopied(id)
    } catch (err) {
      console.error("Standard copy failed, trying fallback", err)
      try {
        const textarea = document.createElement("textarea")
        textarea.value = text
        textarea.style.position = "fixed"
        textarea.style.opacity = "0"
        document.body.appendChild(textarea)
        textarea.select()
        document.execCommand("copy")
        document.body.removeChild(textarea)
        setCopied(id)
      } catch (fallbackErr) {
        console.error("Fallback copy failed", fallbackErr)
        toast.error("Copy failed. Please select text manually.")
      }
    }
  }
}

const setCopied = (id: string | number) => {
  copiedId.value = id
  setTimeout(() => {
    if (copiedId.value === id) {
      copiedId.value = null
    }
  }, 2000)
}

const openModal = (task: VideoTask) => {
  if ((task.status === 'SUCCESS' && task.result_url) || task.status === 'FAILED') {
    selectedVideo.value = task
    showModal.value = true
  }
}

const closeModal = () => {
  selectedVideo.value = null
  showModal.value = false
}

const downloadingIds = ref<Set<string | number>>(new Set())

const downloadVideo = async (url: string, id: string | number) => {
  if (!url) return
  if (downloadingIds.value.has(id)) return
  
  downloadingIds.value.add(id)
  try {
    const response = await fetch(url)
    const blob = await response.blob()
    const blobUrl = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = blobUrl
    a.download = `sora_video_${id}.mp4`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(blobUrl)
  } catch (e) {
    console.error("Download failed:", e)
    window.open(url, '_blank')
  } finally {
    downloadingIds.value.delete(id)
  }
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return ""
  const date = new Date(dateStr)
  const pad = (n: number) => n.toString().padStart(2, '0')
  return `${date.getFullYear()}.${pad(date.getMonth() + 1)}.${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}`
}

</script>

<template>
  <div class="page-container history-page">
    <div class="header animate-fade-in">
      <div class="header-badge">
        <History :size="16" class="text-primary" />
        <span>{{ t("nav.history") }}</span>
      </div>
      <h1 class="page-title">{{ t("history.title") }}</h1>
      <p class="subtitle">{{ t("history.subtitle") }}</p>
      
      <div class="controls">
        <label class="toggle-pill glass-card">
          <span class="toggle-text">{{ t("history.showAll") }}</span>
          <div class="switch">
            <input type="checkbox" v-model="showAll">
            <span class="slider"></span>
          </div>
        </label>
      </div>
    </div>

    <div v-if="videoStore.loading && filteredTasks.length === 0" class="loading-container">
      <Loader2 class="animate-spin text-primary" :size="48" />
    </div>

    <div v-else-if="filteredTasks.length === 0" class="empty-state-view animate-fade-up">
      <div class="empty-illustration">
        <div class="circle-glow"></div>
        <VideoOff :size="64" class="empty-icon" />
      </div>
      <h3 class="empty-title">{{ t("history.noVideosTitle") || "No Projects Found" }}</h3>
      <p class="empty-text">{{ t("history.noVideos") }}</p>
      <router-link to="/dashboard" class="btn btn-generate mt-6">
        {{ t("nav.dashboard") }}
      </router-link>
    </div>

    <div v-else class="video-grid">
      <div 
        v-for="(task, index) in filteredTasks" 
        :key="task.id" 
        class="glass-card video-card animate-fade-up"
        :style="{ animationDelay: index * 0.05 + 's' }"
      >
        <div class="card-media" @click="openModal(task)">
          <div v-if="task.status === 'SUCCESS' && task.result_url" class="media-container">
            <video 
              :src="task.result_url" 
              class="video-preview" 
              preload="metadata" 
              muted
              @mouseenter="(e) => (e.target as HTMLVideoElement).play()"
              @mouseleave="(e) => (e.target as HTMLVideoElement).pause()"
            ></video>
            <div class="media-overlay">
              <div class="play-circle">
                <Maximize2 color="white" :size="24" />
              </div>
            </div>
          </div>
          
          <div v-else class="media-placeholder" :class="{ clickable: task.status === 'FAILED' }">
            <div class="status-indicator" :class="task.status">
              {{ t(`dashboard.status.${task.status.toLowerCase()}`) }}
            </div>
            <div v-if="task.status === 'FAILED'" class="error-notice">
              <CircleAlert :size="24" />
              <span class="error-hint">{{ t("common.clickDetails") }}</span>
            </div>
            <Loader2 v-else class="animate-spin" :size="32" />
          </div>

          <div class="media-meta">
            <span class="ratio-badge">{{ task.ratio }}</span>
          </div>
        </div>

        <div class="card-body">
          <div class="card-meta">
            <span class="meta-date">{{ formatDate(task.created_at) }}</span>
            <span class="meta-duration">{{ task.duration }}s</span>
          </div>
          
          <div class="prompt-container">
            <p class="prompt-content" :class="{ expanded: expandedPrompts.has(task.id) }">
              {{ task.prompt }}
            </p>
            <div class="card-actions">
              <button 
                v-if="isLongPrompt(task.prompt)" 
                @click="togglePrompt(task.id)" 
                class="btn btn-ghost btn-xs"
              >
                {{ expandedPrompts.has(task.id) ? t("common.collapse") : t("history.showDetails") }}
                <ChevronUp v-if="expandedPrompts.has(task.id)" :size="12" />
                <ChevronDown v-else :size="12" />
              </button>
              <div v-else></div>

              <button 
                @click.stop="copyToClipboard(task.prompt, task.id)" 
                class="btn btn-ghost btn-xs copy-btn"
                :class="{ copied: copiedId === task.id }"
              >
                <Check v-if="copiedId === task.id" :size="12" />
                <Copy v-else :size="12" />
                <span>{{ copiedId === task.id ? t("common.copied") : t("common.copy") }}</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <Transition name="fade">
      <div v-if="showModal && selectedVideo" class="modal-overlay" @click.self="closeModal">
        <div class="modal-container glass-card">
          <button class="modal-close" @click="closeModal">
            <X :size="24" />
          </button>
          
          <div class="modal-body">
            <div class="modal-video-box">
              <video 
                v-if="selectedVideo.status === 'SUCCESS'"
                controls 
                autoplay 
                :src="selectedVideo.result_url" 
                class="main-video"
              ></video>
              
              <div v-else-if="selectedVideo.status === 'FAILED'" class="error-display-state">
                <div class="error-icon-wrapper">
                  <CircleAlert :size="64" />
                </div>
                <h3 class="error-title-modal">{{ t("history.generationFailed") }}</h3>
                <div class="error-content-box">
                  <p class="error-text-full">
                    {{ selectedVideo.failure_reason || t("history.unknownError") }}
                  </p>
                </div>
              </div>
            </div>
            
            <div class="modal-details">
              <div class="modal-head">
                <div class="detail-badges">
                  <span class="badge primary">{{ selectedVideo.ratio }}</span>
                  <span class="badge">{{ selectedVideo.duration }}s</span>
                  <span class="meta-date">{{ formatDate(selectedVideo.created_at) }}</span>
                </div>
                <button
                  v-if="selectedVideo.status === 'SUCCESS'"
                  @click="downloadVideo(selectedVideo.result_url, selectedVideo.id)"
                  class="btn btn-primary btn-sm full-width"
                >
                  <Download :size="16" /> {{ t("dashboard.download") }}
                </button>
              </div>
              
              <div class="modal-prompt-box">
                <label>{{ t("dashboard.promptDetails") }}</label>
                <p>{{ selectedVideo.prompt }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.history-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2.5rem;
}
.header {
  text-align: center;
  margin-bottom: 4rem;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.header-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: var(--primary-300);
  border: 1px solid var(--primary-200);
  border-radius: 100px;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--primary-100);
  margin-bottom: 1rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.page-title {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}
.subtitle {
  color: var(--color-text-secondary);
  font-size: 1.125rem;
  margin-bottom: 2rem;
}
.toggle-pill {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.5rem 1.25rem;
  border-radius: 100px;
  cursor: pointer;
  transition: all 0.2s;
}
.toggle-text {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-main);
}
.switch {
  position: relative;
  width: 36px;
  height: 18px;
}
.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}
.slider {
  position: absolute;
  cursor: pointer;
  inset: 0;
  background-color: var(--color-border);
  transition: 0.3s;
  border-radius: 20px;
}
.slider:before {
  position: absolute;
  content: "";
  height: 14px;
  width: 14px;
  left: 2px;
  bottom: 2px;
  background-color: #fff;
  transition: 0.3s;
  border-radius: 50%;
}
input:checked + .slider {
  background-color: var(--color-primary);
}
input:checked + .slider:before {
  transform: translate(18px);
}
.loading-container {
  display: flex;
  justify-content: center;
  padding: 8rem 0;
}
.empty-state-view {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 8rem 2rem;
  text-align: center;
}
.empty-illustration {
  position: relative;
  width: 120px;
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 2rem;
}
.circle-glow {
  position: absolute;
  inset: 0;
  background: var(--color-primary-glow);
  border-radius: 50%;
  filter: blur(40px);
  opacity: 0.3;
  animation: pulse 4s infinite ease-in-out;
}
.empty-icon {
  color: var(--color-primary);
  opacity: 0.8;
  position: relative;
  z-index: 1;
}
.empty-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-text-main);
  margin-bottom: 0.75rem;
}
.empty-text {
  font-size: 1rem;
  color: var(--color-text-secondary);
  max-width: 400px;
  line-height: 1.6;
  margin-bottom: 2.5rem;
}
@keyframes pulse {
  0% { transform: scale(1); opacity: 0.3; }
  50% { transform: scale(1.2); opacity: 0.5; }
  100% { transform: scale(1); opacity: 0.3; }
}
.video-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 2rem;
  align-items: start;
}
.video-card {
  background: #fff;
  border: 1px solid var(--bg-300);
  border-radius: var(--radius-lg);
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  flex-direction: column;
}
.video-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 30px #0000001a;
  border-color: var(--primary-200);
}
.card-media {
  background: linear-gradient(135deg, #1e293b, #0f172a);
  width: 100%;
  aspect-ratio: 16 / 9;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  overflow: hidden;
  border-bottom: 1px solid var(--bg-200);
}
.media-container {
  width: 100%;
  height: 100%;
  position: relative;
}
.video-preview {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.media-overlay {
  position: absolute;
  inset: 0;
  background: #0006;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
}
.video-card:hover .media-overlay {
  opacity: 1;
}
.play-circle {
  width: 54px;
  height: 54px;
  background: #fff3;
  backdrop-filter: blur(8px);
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transform: scale(0.9);
  transition: transform 0.3s;
}
.video-card:hover .play-circle {
  transform: scale(1);
}
.media-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  background: var(--color-surface);
}
.status-indicator {
  font-size: 0.7rem;
  font-weight: 700;
  padding: 0.25rem 0.75rem;
  border-radius: 100px;
  text-transform: uppercase;
  z-index: 2;
}
.status-indicator.PROCESSING {
  background: var(--color-primary-glow);
  color: var(--color-primary);
}
.status-indicator.SUCCESS {
  background: #28a7451a;
  color: #28a745;
}
.status-indicator.FAILED {
  background: #dc35451a;
  color: #dc3545;
}
.media-placeholder.clickable {
  cursor: pointer;
}
.media-placeholder.clickable:hover {
  background: var(--bg-200);
}
.error-notice {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: #dc3545;
}
.error-hint {
  font-size: 0.75rem;
  opacity: 0.8;
}
.error-display-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  text-align: center;
  height: 100%;
  width: 100%;
}
.error-icon-wrapper {
  color: #ef4444;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: #ef44441a;
  border-radius: 50%;
}
.error-title-modal {
  font-size: 1.5rem;
  font-weight: 700;
  color: #fff;
  margin-bottom: 1.5rem;
}
.error-content-box {
  background: #ffffff0d;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 1.5rem;
  width: 100%;
  max-width: 500px;
  max-height: 300px;
  overflow-y: auto;
  text-align: left;
}
.error-text-full {
  font-family: monospace;
  color: #fca5a5;
  white-space: pre-wrap;
  word-break: break-all;
  font-size: 0.9rem;
  line-height: 1.6;
}
.media-meta {
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 5;
}
.ratio-badge {
  background: #fffc;
  backdrop-filter: blur(4px);
  color: var(--color-text-main);
  font-size: 0.65rem;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 4px;
  border: 1px solid var(--color-border);
}
.card-body {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.card-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-muted);
}
.prompt-content {
  font-size: 0.9rem;
  color: var(--color-text-main);
  line-height: 1.6;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  transition: all 0.3s;
}
.prompt-content.expanded {
  -webkit-line-clamp: unset;
}
.card-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 0.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--color-border);
}
.btn-xs {
  padding: 0.375rem 0.75rem;
  font-size: 0.75rem;
}
.copy-btn.copied {
  color: #10b981;
}
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(12px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.modal-container {
  width: 90vw;
  height: 85vh;
  max-width: 1200px;
  max-height: 900px;
  background: #18181b; 
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
  border-radius: 20px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
}

.modal-close {
  position: absolute;
  top: 1.5rem;
  right: 1.5rem;
  z-index: 100;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #fff;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.modal-close:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: rotate(90deg);
}

.modal-body {
  display: flex;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.modal-video-box {
  flex: 1;
  background: #000;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.main-video {
  width: 100%;
  height: 100%;
  max-height: none;
  object-fit: contain;
}

.modal-details {
  width: 380px;
  flex-shrink: 0;
  padding: 2.5rem;
  display: flex;
  flex-direction: column;
  gap: 2rem;
  background: #18181b;
  border-left: 1px solid rgba(255, 255, 255, 0.05);
  color: #fff;
  overflow-y: auto;
}

.modal-head {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin-bottom: 2rem;
  padding-bottom: 2rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.detail-badges {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.badge {
  background: rgba(255, 255, 255, 0.1);
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 0.75rem;
  font-weight: 600;
  color: #e2e8f0;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.badge.primary {
  background: rgba(99, 102, 241, 0.2);
  color: #818cf8;
  border-color: rgba(99, 102, 241, 0.2);
}

.meta-date {
  font-size: 0.8rem;
  color: #94a3b8;
  margin-left: auto;
}

.modal-prompt-box label {
  display: block;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  color: #64748b;
  margin-bottom: 1rem;
  letter-spacing: 0.1em;
}

.modal-prompt-box p {
  font-size: 0.95rem;
  line-height: 1.7;
  color: #e2e8f0;
  max-height: 300px;
  overflow-y: auto;
  padding-right: 0.5rem;
}

/* Custom Scrollbar for dark modal */
.modal-details::-webkit-scrollbar,
.modal-prompt-box p::-webkit-scrollbar {
  width: 6px;
}
.modal-details::-webkit-scrollbar-thumb,
.modal-prompt-box p::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
}

.full-width {
  width: 100%;
}

.btn-primary {
  background: var(--color-primary);
  color: #fff;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  transition: all 0.2s;
}

.btn-primary:hover {
  background: #4f46e5;
  transform: translateY(-2px);
}

@media (max-width: 900px) {
  .modal-body {
    flex-direction: column;
    overflow-y: auto;
  }
  .modal-container {
    height: auto;
    max-height: 90vh;
  }
  .modal-video-box {
    width: 100%;
    height: auto;
    aspect-ratio: 16/9;
    flex: none;
  }
  .modal-details {
    width: 100%;
    height: auto;
    padding: 1.5rem;
    overflow: visible; 
  }
  .modal-close {
    top: 1rem;
    right: 1rem;
    background: rgba(0, 0, 0, 0.5);
  }
}
.animate-fade-in {
  animation: fadeIn 0.5s ease-out;
}
.animate-fade-up {
  animation: fadeUp 0.6s ease-out forwards;
  opacity: 0;
}
@keyframes fadeIn {
  0% { opacity: 0; }
  to { opacity: 1; }
}
@keyframes fadeUp {
  0% { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
