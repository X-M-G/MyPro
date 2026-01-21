<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useVideoStore } from '@/stores/video'
import { 
  CloudUpload, 
  Download, 
  CircleAlert, 
  ChevronDown, 
  Video as VideoIcon, 
  Maximize2, 
  X, 
  Sparkles, 
  Type, 
  Loader2,
  Clock
} from 'lucide-vue-next'

const { t } = useI18n()
const videoStore = useVideoStore()

const prompt = ref('')
const aspectRatio = ref('9:16')
const model = ref('sora2')
const duration = ref(15)
const referenceImage = ref<string | null>(null)
const previewImage = ref<string | null>(null)
const isGenerating = ref(false)
const error = ref('')
const showHistory = ref(false)
const showModal = ref(false)
const selectedVideo = ref<any>(null)

const availableDurations = computed(() => {
  return model.value === 'sora2-pro' ? [15, 25] : [10, 15]
})

watch(model, (newModel) => {
  if (newModel === 'sora2-pro') {
    duration.value = 25
  } else {
    duration.value = 15
  }
})

const currentTask = computed(() => videoStore.tasks[0] || null)
const historyTasks = computed(() => videoStore.tasks.slice(1))

const handleImageUpload = (event: Event) => {
  const input = event.target as HTMLInputElement
  if (input.files && input.files[0]) {
    const file = input.files[0]
    if (!file.type.startsWith('image/')) {
      error.value = t('errors.ERROR_INVALID_IMAGE_TYPE') || "Please upload a valid image file (JPG/PNG)."
      return
    }
    if (file.size > 5 * 1024 * 1024) {
      error.value = t('errors.ERROR_IMAGE_TOO_LARGE') || "Image size should be less than 5MB."
      return
    }
    const reader = new FileReader()
    reader.onload = (e) => {
      const result = e.target?.result as string
      referenceImage.value = result
      previewImage.value = result
      error.value = ""
    }
    reader.readAsDataURL(file)
  }
}

const removeImage = () => {
  referenceImage.value = null
  previewImage.value = null
  const input = document.getElementById('ref-upload') as HTMLInputElement
  if (input) input.value = ''
}

const handleGenerate = async () => {
  if (!prompt.value) return
  isGenerating.value = true
  error.value = ""
  
  const success = await videoStore.generateVideo(
    prompt.value, 
    aspectRatio.value, 
    duration.value, 
    referenceImage.value, 
    model.value
  )
  
  if (success) {
    prompt.value = ""
    removeImage()
  } else {
    error.value = videoStore.error || "Generation failed. Please check your credits or try again later."
  }
  isGenerating.value = false
}

const toggleHistory = () => {
  showHistory.value = !showHistory.value
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return ""
  const date = new Date(dateStr)
  const pad = (n: number) => n.toString().padStart(2, '0')
  return `${date.getFullYear()}.${pad(date.getMonth() + 1)}.${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}`
}

const openModal = (video: any) => {
  if (video.status === 'SUCCESS') {
    selectedVideo.value = video
    showModal.value = true
  }
}

const closeModal = () => {
  showModal.value = false
  selectedVideo.value = null
}

const downloadVideo = (url: string, id: string) => {
  if (!url) return
  try {
    const a = document.createElement('a')
    a.href = url
    a.download = `sora_video_${id}_${Date.now()}.mp4`
    a.target = "_blank"
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
  } catch (e) {
    console.error("Download failed:", e)
    window.open(url, '_blank')
  }
}

onMounted(() => {
  videoStore.fetchHistory()
})
</script>

<template>
  <div class="page-container dashboard">
    <div class="main-layout animate-fade-in">
      <section class="panel-section animate-fade-up" style="animation-delay: 0.1s">
        <div class="glass-card form-card">
          <div class="card-header">
            <div class="header-badge">
              <Sparkles :size="16" class="text-primary" />
              <span>{{ t("dashboard.title") }}</span>
            </div>
            <h2 class="card-title">{{ t("dashboard.title") }}</h2>
            <p class="subtitle">{{ t("dashboard.subtitle") }}</p>
          </div>
          <div class="card-body">
            <div class="form-item">
              <label class="label">
                <Type :size="16" /> {{ t("dashboard.promptLabel") }}
              </label>
              <div class="input-wrapper">
                <textarea
                  v-model="prompt"
                  class="textarea modern-textarea"
                  :placeholder="t('dashboard.promptPlaceholder')"
                  rows="5"
                ></textarea>
                <div class="input-glow"></div>
                <span class="char-count" :class="{ 'has-text': prompt.length > 0 }">
                  {{ prompt.length }} {{ t("dashboard.chars") }}
                </span>
              </div>
            </div>
            
            <div class="form-item">
              <label class="label">
                <CloudUpload :size="16" /> {{ t("dashboard.referenceImage") }} 
                <span class="tag-optional">{{ t("dashboard.optional") }}</span>
              </label>
              
              <div v-if="previewImage" class="preview-zone glass-card">
                <img :src="previewImage" class="preview-image" alt="Reference" />
                <button @click="removeImage" class="btn-remove" title="Remove Image">
                  <X :size="14" /> {{ t("dashboard.remove") }}
                </button>
              </div>
              
              <div v-else class="upload-zone glass-card">
                <input
                  type="file"
                  id="ref-upload"
                  class="hidden-input"
                  accept="image/*"
                  @change="handleImageUpload"
                />
                <label for="ref-upload" class="upload-label">
                  <div class="icon-circle">
                    <CloudUpload :size="24" />
                  </div>
                  <div class="upload-text">
                    <span class="main-text">{{ t("dashboard.clickToUpload") }}</span>
                    <span class="sub-text">{{ t("dashboard.uploadSupport") }}</span>
                  </div>
                </label>
              </div>
            </div>

            <div class="settings-grid">
              <div class="form-group">
                <label class="label">{{ t("dashboard.model") || "AI Model" }}</label>
                <div class="select-wrapper">
                  <select v-model="model" class="select modern-select">
                    <option value="sora2">Sora 2</option>
                    <option value="sora2-pro">Sora2 Pro</option>
                  </select>
                </div>
              </div>
              
              <div class="form-group">
                <label class="label">{{ t("dashboard.aspectRatio") }}</label>
                <div class="select-wrapper">
                  <select v-model="aspectRatio" class="select modern-select">
                    <option value="16:9">16:9 {{ t("dashboard.landscape") }}</option>
                    <option value="9:16">9:16 {{ t("dashboard.portrait") }}</option>
                  </select>
                </div>
              </div>

              <div class="form-group">
                <label class="label">{{ t("dashboard.duration") }}</label>
                <div class="select-wrapper">
                  <select v-model="duration" class="select modern-select">
                    <option v-for="d in availableDurations" :key="d" :value="d">
                      {{ d }} {{ t("dashboard.seconds") }}
                    </option>
                  </select>
                </div>
              </div>
            </div>

            <div class="action-footer">
              <div class="cost-info">
                <div class="coin">C</div>
                <span>
                  {{ t("dashboard.cost") }}: <strong>{{ model === "sora2-pro" ? 300 : 30 }}</strong> {{ t("dashboard.credits") }}
                </span>
              </div>
              <button
                @click="handleGenerate"
                class="btn btn-generate full-width"
                :disabled="isGenerating || !prompt"
              >
                <Loader2 v-if="isGenerating" class="animate-spin" :size="20" />
                <Sparkles v-else :size="20" />
                <span>{{ isGenerating ? t("dashboard.generating") : t("dashboard.generateVideo") }}</span>
                <div class="btn-shine"></div>
              </button>
              
              <div v-if="error" class="error-toast">
                <CircleAlert :size="16" />
                <span>{{ error }}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section class="panel-section animate-fade-up" style="animation-delay: 0.2s">
        <div class="panel-nav">
          <h3 class="panel-title">{{ t("dashboard.currentTask") }}</h3>
          <div v-if="currentTask" class="status-indicator" :class="currentTask.status">
            {{ currentTask.status }}
          </div>
        </div>

        <Transition name="fade" mode="out-in">
          <div v-if="currentTask && currentTask.status === 'PROCESSING'" class="preview-display processing glass-card">
            <div class="processing-glow"></div>
            <div class="loading-state">
              <div class="spin-box">
                <Loader2 class="animate-spin" :size="48" />
              </div>
              <h4>{{ t("dashboard.generatingMagic") }}</h4>
              <p>{{ t("dashboard.creatingFrames", { ratio: currentTask.ratio }) }}</p>
              <div class="progress-container">
                <div class="progress-bar" :style="{ width: currentTask.progress + '%' }"></div>
              </div>
              <span class="progress-label">{{ currentTask.progress }}%</span>
            </div>
          </div>

          <div v-else-if="currentTask && currentTask.status === 'SUCCESS' && currentTask.result_url" class="preview-display success glass-card">
            <div class="video-container">
              <video
                controls
                autoplay
                loop
                muted
                :src="currentTask.result_url"
                class="main-video"
              ></video>
            </div>
            <div class="video-info">
              <p class="prompt-text">{{ currentTask.prompt }}</p>
              <div class="video-meta">
                <span class="meta-item">
                  <Clock :size="14" /> {{ formatDate(currentTask.created_at) }}
                </span>
                <div class="meta-actions">
                  <span class="badge">{{ currentTask.ratio || "16:9" }}</span>
                  <button @click="downloadVideo(currentTask.result_url, currentTask.id)" class="btn btn-ghost btn-sm">
                    <Download :size="16" /> {{ t("dashboard.download") }}
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div v-else-if="currentTask && currentTask.status === 'FAILED'" class="preview-display failed glass-card">
            <div class="error-icon-box">
              <CircleAlert :size="64" />
            </div>
            <h3>{{ t("dashboard.generationFailed") }}</h3>
            <p>{{ currentTask.failure_reason }}</p>
          </div>

          <div v-else class="preview-display empty glass-card">
            <div class="placeholder-icon">
              <VideoIcon :size="48" />
            </div>
            <h3>{{ t("dashboard.readyToCreate") }}</h3>
            <p>{{ t("dashboard.masterpiece") }}</p>
          </div>
        </Transition>
      </section>
    </div>

    <section v-if="historyTasks.length > 0" class="history-section animate-fade-up" style="animation-delay: 0.3s">
      <div class="section-header">
        <h3 class="section-title">{{ t("dashboard.recentCreations") }}</h3>
        <button @click="toggleHistory" class="btn btn-ghost btn-sm">
          {{ showHistory ? t("dashboard.hideHistory") : t("dashboard.showHistory") }} ({{ historyTasks.length }})
          <ChevronDown :class="{ rotated: showHistory }" :size="16" />
        </button>
      </div>
      
      <Transition name="slide">
        <div v-if="showHistory" class="history-grid">
          <div v-for="task in historyTasks" :key="task.id" class="history-card glass-card">
            <div class="thumb-wrapper" @click="openModal(task)">
              <div v-if="task.status === 'PROCESSING'" class="thumb-status">
                <Loader2 class="animate-spin" :size="24" />
              </div>
              <video
                v-if="task.result_url && task.status === 'SUCCESS'"
                :src="task.result_url"
                class="thumb-video"
                muted
                loop
                @mouseenter="(e) => (e.target as HTMLVideoElement).play()"
                @mouseleave="(e) => (e.target as HTMLVideoElement).pause()"
              ></video>
              <div v-if="task.status === 'SUCCESS'" class="thumb-overlay">
                <Maximize2 :size="24" />
              </div>
              <div v-if="task.status === 'FAILED'" class="thumb-status failed">
                <CircleAlert :size="24" />
              </div>
              <span class="thumb-badge">{{ task.ratio }}</span>
            </div>
            <div class="history-body">
              <p class="history-prompt" :title="task.prompt">{{ task.prompt }}</p>
              <div class="history-footer">
                <span class="history-date">{{ formatDate(task.created_at) }}</span>
                <span class="status-pip" :class="task.status"></span>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </section>

    <Transition name="fade">
      <div v-if="showModal && selectedVideo" class="modal-overlay" @click.self="closeModal">
        <div class="modal-container glass-card">
          <button class="modal-close" @click="closeModal">
            <X :size="24" />
          </button>
          <div class="modal-body">
            <div class="modal-video-box">
              <video
                controls
                autoplay
                :src="selectedVideo.result_url"
                class="modal-video"
              ></video>
            </div>
            <div class="modal-details">
              <div class="modal-head">
                <div class="detail-badges">
                  <span class="badge primary">{{ selectedVideo.ratio }}</span>
                  <span class="badge">{{ selectedVideo.duration }}s</span>
                  <span class="meta-date">{{ formatDate(selectedVideo.created_at) }}</span>
                </div>
                <button
                  @click="downloadVideo(selectedVideo.result_url, selectedVideo.id)"
                  class="btn btn-primary btn-sm"
                >
                  <Download :size="16" /> {{ t("dashboard.download") }}
                </button>
              </div>
              <div class="modal-prompt">
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
.dashboard {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2.5rem;
  font-family: inherit;
  color: var(--color-text-main);
  min-height: 100vh;
}
.glass-card {
  background: #fff;
  border: 1px solid var(--bg-300);
  border-radius: var(--radius-lg);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  position: relative;
  overflow: hidden;
  z-index: 1;
}
.btn-primary {
  background: var(--color-primary);
  color: #fff;
  border: none;
  box-shadow: 0 4px 15px var(--color-primary-glow);
}
.btn-primary:hover:not(:disabled) {
  background: #4f46e5;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px var(--color-primary-glow);
}
.btn-primary:disabled {
  background: var(--color-text-muted);
  color: #a0aec0;
  cursor: not-allowed;
  box-shadow: none;
}
.btn-primary .btn-shine {
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
  transform: rotate(45deg);
  transition: all 0.5s ease;
  opacity: 0;
}
.btn-primary:hover .btn-shine {
  opacity: 1;
  transform: translate(20%, 20%) rotate(45deg);
}
.btn-ghost {
  background: transparent;
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
}
.btn-ghost:hover {
  background: #ffffff0d;
  color: var(--color-text-main);
  border-color: #ffffff26;
}
.btn-sm {
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  border-radius: 8px;
}
.full-width {
  width: 100%;
}
.main-layout {
  display: grid;
  grid-template-columns: 1fr 1.2fr;
  gap: 2.5rem;
  align-items: start;
}
@media (max-width: 1100px) {
  .main-layout {
    grid-template-columns: 1fr;
  }
}
.animate-fade-in {
  animation: fadeIn 0.5s ease-out forwards;
}
.animate-fade-up {
  animation: fadeUp 0.6s ease-out forwards;
  opacity: 0;
  transform: translateY(20px);
}
@keyframes fadeIn {
  0% { opacity: 0; }
  to { opacity: 1; }
}
@keyframes fadeUp {
  0% { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
.form-card {
  display: flex;
  flex-direction: column;
}
.card-header {
  padding: 2rem 2.5rem;
  border-bottom: 1px solid var(--color-border);
}
.header-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.375rem 0.875rem;
  background: #6366f11a;
  border-radius: 100px;
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--color-primary);
  margin-bottom: 1rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.card-title {
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
  color: var(--color-text-main);
}
.subtitle {
  font-size: 0.9rem;
  color: var(--color-text-secondary);
}
.card-body {
  padding: 2.5rem;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}
.form-item {
  margin-bottom: 0px;
}
.label {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  font-size: 0.875rem;
  font-weight: 700;
  color: var(--color-text-main);
  margin-bottom: 0.875rem;
}
.input-wrapper {
  position: relative;
}
.textarea {
  width: 100%;
  padding: 1rem;
  border: 1px solid var(--color-border);
  border-radius: 10px;
  font-size: 0.95rem;
  line-height: 1.6;
  background: var(--color-bg-light);
  color: var(--color-text-main);
  resize: vertical;
  transition: all 0.2s;
  outline: none;
}
.textarea:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-glow);
}
.input-glow {
  position: absolute;
  inset: -1px;
  border-radius: 10px;
  background: linear-gradient(45deg, var(--color-primary), transparent);
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
  z-index: -1;
}
.textarea:focus + .input-glow {
  opacity: 0.3;
}
.modern-textarea {
  min-height: 140px;
}
.char-count {
  position: absolute;
  bottom: 10px;
  right: 12px;
  font-size: 0.75rem;
  color: var(--color-text-muted);
}
.char-count.has-text {
  color: var(--color-text-secondary);
}
.tag-optional {
  font-size: 0.7rem;
  color: var(--color-text-muted);
  font-weight: 400;
  margin-left: auto;
}
.upload-zone {
  padding: 2rem;
  border: 2px dashed var(--color-border);
  cursor: pointer;
  transition: all 0.2s;
}
.upload-zone:hover {
  border-color: var(--color-primary);
  background: #6366f105;
}
.upload-label {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  cursor: pointer;
}
.icon-circle {
  width: 48px;
  height: 48px;
  background: var(--bg-200);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--primary-100);
  border: 1px solid var(--bg-300);
}
.upload-text {
  display: flex;
  flex-direction: column;
}
.main-text {
  font-weight: 700;
  font-size: 0.95rem;
  color: var(--color-text-main);
}
.sub-text {
  color: var(--color-text-muted);
  font-size: 0.8rem;
}
.hidden-input {
  display: none;
}
.preview-zone {
  position: relative;
  border-radius: var(--radius-md);
  overflow: hidden;
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-bg-light);
}
.preview-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  display: block;
}
.btn-remove {
  position: absolute;
  top: 10px;
  right: 10px;
  background: #fff;
  border: 1px solid var(--bg-300);
  color: var(--text-100);
  font-size: 0.75rem;
  font-weight: 600;
  padding: 6px 12px;
  border-radius: 100px;
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
}
.btn-remove:hover {
  background: #000c;
}
.settings-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}
.select-wrapper {
  position: relative;
}
.select {
  width: 100%;
  padding: 0.8rem 1rem;
  border: 1px solid var(--color-border);
  border-radius: 10px;
  appearance: none;
  background: #fff;
  color: var(--color-text-main);
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s;
  outline: none;
}
.select:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-glow);
}
.select-wrapper:after {
  content: "▼";
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--color-text-muted);
  font-size: 0.7rem;
  pointer-events: none;
}
.action-footer {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  margin-top: 1rem;
}
.cost-info {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--color-text-secondary);
}
.coin {
  width: 22px;
  height: 22px;
  background: #fbbf24;
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 900;
  box-shadow: 0 0 10px #fbbf244d;
}
.error-toast {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  background: #dc354514;
  border: 1px solid rgba(220, 53, 69, 0.2);
  border-radius: var(--radius-md);
  color: #dc3545;
  font-size: 0.9rem;
}
.panel-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.25rem;
}
.panel-title {
  font-size: 0.75rem;
  font-weight: 800;
  text-transform: uppercase;
  color: var(--color-text-muted);
  letter-spacing: 0.1em;
}
.status-indicator {
  font-size: 0.7rem;
  font-weight: 700;
  padding: 0.25rem 0.75rem;
  border-radius: 100px;
  text-transform: uppercase;
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
.preview-display {
  min-height: 520px;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}
.preview-display.empty,
.preview-display.failed {
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 3rem;
}
.placeholder-icon {
  width: 80px;
  height: 80px;
  background: var(--color-surface);
  border-radius: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-muted);
  margin-bottom: 2rem;
  border: 1px solid var(--color-border);
}
.loading-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 2;
  width: 100%;
  padding: 2rem;
}
.processing-glow {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, var(--color-primary-glow) 0%, transparent 100%);
  animation: pulse 3s infinite ease-in-out;
  z-index: 1;
}
.spin-box {
  margin-bottom: 2rem;
  color: var(--color-primary);
  filter: drop-shadow(0 0 10px var(--color-primary-glow));
}
.loading-state h4 {
  font-size: 1.25rem;
  color: var(--color-text-main);
  margin-bottom: 0.75rem;
}
.loading-state p {
  font-size: 0.9rem;
  color: var(--color-text-secondary);
  margin-bottom: 1.5rem;
}
.progress-container {
  width: 60%;
  height: 6px;
  background: var(--color-border);
  border-radius: 100px;
  margin: 1.5rem 0 0.5rem;
  position: relative;
  overflow: hidden;
}
.progress-bar {
  height: 100%;
  background: var(--color-primary);
  box-shadow: 0 0 10px var(--color-primary-glow);
  transition: width 0.4s ease;
}
.progress-label {
  font-size: 0.875rem;
  font-weight: 700;
  color: var(--color-primary);
  margin-top: 1rem;
}
.video-container {
  flex: 1;
  background: #000;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}
.main-video {
  width: 100%;
  height: 100%;
  object-fit: contain;
}
.video-info {
  padding: 2rem;
}
.prompt-text {
  font-size: 0.95rem;
  color: var(--color-text-main);
  line-height: 1.6;
  margin-bottom: 1.5rem;
}
.video-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.meta-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8rem;
  color: var(--color-text-muted);
}
.meta-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}
.error-icon-box {
  color: #ef4444;
  margin-bottom: 1.5rem;
  filter: drop-shadow(0 0 10px rgba(239, 68, 68, 0.4));
}
.history-section {
  margin-top: 5rem;
}
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}
.section-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-text-main);
}
.btn-ghost .lucide {
  transition: transform 0.2s;
}
.btn-ghost .lucide.rotated {
  transform: rotate(180deg);
}
.history-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 2rem;
}
.history-card {
  padding: 0;
  transition: all 0.3s;
}
.history-card:hover {
  transform: translateY(-8px);
  border-color: var(--color-primary);
  box-shadow: 0 10px 20px #0000001a;
}
.thumb-wrapper {
  aspect-ratio: 16 / 9;
  background: #000;
  position: relative;
  cursor: pointer;
  overflow: hidden;
  border-bottom: 1px solid var(--color-border);
}
.thumb-video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.thumb-overlay {
  position: absolute;
  inset: 0;
  background: #0006;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
  color: #fff;
}
.thumb-wrapper:hover .thumb-overlay {
  opacity: 1;
}
.thumb-status {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-primary);
  background: #000000b3;
}
.thumb-status.failed {
  color: #ef4444;
}
.thumb-badge {
  position: absolute;
  top: 10px;
  right: 10px;
  background: #0009;
  backdrop-filter: blur(4px);
  color: #fff;
  font-size: 0.65rem;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 4px;
}
.history-body {
  padding: 1.25rem;
}
.history-prompt {
  font-size: 0.85rem;
  color: var(--color-text-main);
  margin-bottom: 1rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.history-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.history-date {
  font-size: 0.75rem;
  color: var(--color-text-muted);
}
.status-pip {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}
.status-pip.SUCCESS {
  background: #10b981;
  box-shadow: 0 0 5px #10b981;
}
.status-pip.PROCESSING {
  background: var(--color-primary);
  box-shadow: 0 0 5px var(--color-primary);
}
.status-pip.FAILED {
  background: #ef4444;
  box-shadow: 0 0 5px #ef4444;
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

.modal-video {
  width: 100%;
  height: 100%;
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

.modal-prompt label {
  display: block;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  color: #64748b;
  margin-bottom: 1rem;
  letter-spacing: 0.1em;
}

.modal-prompt p {
  font-size: 0.95rem;
  line-height: 1.7;
  color: #e2e8f0;
  max-height: 300px;
  overflow-y: auto;
  padding-right: 0.5rem;
}

/* Custom Scrollbar for dark modal */
.modal-details::-webkit-scrollbar,
.modal-prompt p::-webkit-scrollbar {
  width: 6px;
}
.modal-details::-webkit-scrollbar-thumb,
.modal-prompt p::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
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
@keyframes modal-pop {
  0% { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}
@keyframes shimmer {
  0% { transform: translate(-100%); }
  to { transform: translate(100%); }
}
.spin {
  animation: spin 1s linear infinite;
}
</style>
