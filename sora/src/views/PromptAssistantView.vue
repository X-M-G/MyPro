<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useVideoStore } from '@/stores/video'
import { useI18n } from 'vue-i18n'
import { 
  Sparkles, Copy, ArrowRight, Wand2, Loader2, AlertTriangle, 
  Check, HelpCircle, ChevronDown, ChevronUp, Clock, Trash2,
  Type, Palette, Globe, Zap, Maximize2, Eye, X
} from 'lucide-vue-next'
import { toast } from '@/utils/toast'

const videoStore = useVideoStore()
const { t } = useI18n()

const concept = ref('')
const style = ref('Cinematic')
const language = ref('Chinese')
const optimizedPrompt = ref('')
const isOptimizing = ref(false)
const errorMsg = ref('')
const isInputExpanded = ref(false)
const isFullScreen = ref(false)
const fullScreenConcept = ref('')
const showTips = ref(false)
const showHistory = ref(true)
const selectedHistoryItem = ref<any>(null)

const openHistoryDetail = (item: any) => {
    selectedHistoryItem.value = item
}

const closeHistoryDetail = () => {
    selectedHistoryItem.value = null
}

import { computed } from 'vue'

const filteredHistory = computed(() => {
  return videoStore.promptHistories.filter(h => h.style !== 'Chat')
})

const toggleFullScreen = () => {
  if (!isFullScreen.value) {
    fullScreenConcept.value = concept.value
    isFullScreen.value = true
  }
}

const applyFullScreen = () => {
  concept.value = fullScreenConcept.value
  isFullScreen.value = false
}

const styles = ['Cinematic', '3D Animation', 'Anime', 'Photorealistic', 'Vintage Film', 'Cyberpunk', 'Watercolor']
const languages = ['English', 'Chinese', 'Spanish', 'Japanese', 'French']
const durations = ['10s', '15s', '25s']
const duration = ref('15s')

const styleDescriptions = {
  'Cinematic': 'Movie-like visual quality with dramatic lighting, depth of field',
  '3D Animation': 'Computer-generated 3D graphics style, similar to Pixar',
  'Anime': 'Japanese animation style with distinctive artistic techniques',
  'Photorealistic': 'Ultra-realistic imagery that looks like actual photographs',
  'Vintage Film': 'Classic film aesthetics with grain and color shifts',
  'Cyberpunk': 'Futuristic sci-fi style with neon lights and dark urbanity',
  'Watercolor': 'Artistic painting style with soft edges and hand-painted look'
}

import { watch } from 'vue'

onMounted(async () => {
  try {
    await videoStore.fetchPromptHistory()
    // Resume active task if any
    await videoStore.checkActivePromptTask()
  } catch (error) {
    console.error('Failed to load history:', error)
  }
})

// Watch active task status
watch(() => videoStore.activePromptTask, (task) => {
    if (task) {
        if (task.status === 'PENDING' || task.status === 'PROCESSING') {
            isOptimizing.value = true
            // If restoring state, ensure we have context
            if (!concept.value && task.raw_prompt) {
                concept.value = task.raw_prompt
                style.value = task.style || style.value
                language.value = task.language || language.value
                duration.value = task.duration || duration.value
            }
        } else if (task.status === 'SUCCESS') {
            isOptimizing.value = false
            optimizedPrompt.value = task.optimized_prompt
        } else if (task.status === 'FAILED') {
            isOptimizing.value = false
            errorMsg.value = task.failure_reason || "Optimization failed"
        }
    }
}, { deep: true })

async function handleOptimize() {
  if (!concept.value) return
  isOptimizing.value = true
  errorMsg.value = ''
  optimizedPrompt.value = ''
  
  try {
     // This now starts the task and sets activePromptTask in store
     // The watcher above will handle the completion
     await videoStore.optimizePrompt(concept.value, style.value, language.value, duration.value)
  } catch (e: any) {
      isOptimizing.value = false // Only Reset if starting failed immediately
      if (e.message) {
          errorMsg.value = e.message
      } else {
          errorMsg.value = "An error occurred"
      }
  }
}

function copyToClipboard() {
    navigator.clipboard.writeText(optimizedPrompt.value)
    toast.success(t('common.copied'))
}

function copyHistoryPrompt(prompt: string) {
    navigator.clipboard.writeText(prompt)
    toast.success(t('common.copied'))
}

function toggleTips() {
    showTips.value = !showTips.value
}

function formatDate(dateString: string) {
    const date = new Date(dateString)
    return date.toLocaleString()
}
</script>

<template>
  <div class="page-container prompt-assistant">
    <!-- Full-screen Concept Editor Overlay -->
    <Teleport to="body">
      <Transition name="fade">
        <div v-if="isFullScreen" class="fullscreen-editor-overlay">
          <div class="editor-container glass-card">
            <header class="editor-header">
              <div class="header-info">
                <Sparkles :size="20" class="text-primary" />
                <h3>{{ t("promptAssistant.inputLabel") }} - {{ t("common.edit") || "Edit" }}</h3>
              </div>
              <div class="header-actions">
                <button class="btn btn-ghost btn-sm" @click="fullScreenConcept = ''">
                  {{ t("common.clear") || "Clear" }}
                </button>
                <button class="btn btn-primary btn-sm" @click="applyFullScreen">
                  {{ t("common.confirm") }}
                </button>
              </div>
            </header>
            <main class="editor-main">
              <textarea
                v-model="fullScreenConcept"
                class="fullscreen-textarea"
                :placeholder="t('promptAssistant.inputPlaceholder')"
                autofocus
              ></textarea>
            </main>
          </div>
        </div>
      </Transition>
    </Teleport>
    <header class="page-header animate-fade-up">
       <div class="header-badge">
         <Wand2 :size="16" class="text-primary" />
         <span>AI</span>
       </div>
       <h1 class="main-title">{{ t('promptAssistant.title') }}</h1>
       <p class="subtitle">{{ t('promptAssistant.subtitle') }}</p>
       <div class="guide-box glass-card">
         <HelpCircle :size="18" class="text-primary" />
         <p>{{ t('promptAssistant.guideLinkText') }}</p>
         <a :href="t('promptAssistant.guideLink')" target="_blank" class="guide-link">
           {{ t('promptAssistant.guideLink') }}
           <ArrowRight :size="14" />
         </a>
       </div>
     </header>

    <div class="main-grid">
      <!-- Input Section -->
      <section class="card-section animate-fade-up" style="animation-delay: 0.1s">
        <div class="glass-card assistant-card">
          <div class="card-header">
            <h2 class="card-title"><Type :size="20" /> {{ t('promptAssistant.inputLabel') }}</h2>
          </div>
          
          <div class="form-body">
            <div class="input-group" :class="{ 'expanded': isInputExpanded }">
              <textarea 
                v-model="concept" 
                class="textarea modern-textarea" 
                :placeholder="t('promptAssistant.inputPlaceholder')"
                :rows="isInputExpanded ? 15 : 5"
              ></textarea>
              <button 
                class="btn-expand" 
                @click="toggleFullScreen"
                :title="t('common.expand')"
              >
                <Maximize2 :size="16" />
              </button>
            </div>

            <div class="config-grid">
              <div class="form-group">
                <label class="label"><Palette :size="16" /> {{ t('promptAssistant.style') }}</label>
                <div class="select-wrapper">
                  <select v-model="style" class="select modern-select">
                    <option v-for="s in styles" :key="s" :value="s">
                      {{ t(`promptAssistant.styles.${s.replace(/\s/g, '').replace(/3D/g, '3d').replace(/^(.)/, c => c.toLowerCase())}`) }}
                    </option>
                  </select>
                </div>
              </div>

              <div class="form-group">
                <label class="label"><Globe :size="16" /> {{ t('promptAssistant.outputLanguageLabel') }}</label>
                <div class="select-wrapper">
                  <select v-model="language" class="select modern-select">
                    <option v-for="l in languages" :key="l" :value="l">
                      {{ l === 'English' ? 'English' : (l === 'Chinese' ? '中文' : l) }}
                    </option>
                  </select>
                </div>
              </div>
            </div>

            <!-- Duration Selection -->
             <div class="config-grid" style="margin-top: 1.5rem;">
               <div class="form-group">
                 <label class="label"><Clock :size="16" /> {{ t('promptAssistant.duration') }}</label>
                 <div class="select-wrapper">
                   <select v-model="duration" class="select modern-select">
                     <option v-for="d in durations" :key="d" :value="d">
                       {{ d }}
                     </option>
                   </select>
                 </div>
               </div>
             </div>

            <div class="action-footer">
              <div class="cost-info">
                <Zap :size="14" class="text-warning" />
                <span>{{ t('promptAssistant.cost') }}: <strong>20</strong> {{ t('dashboard.credits') }}</span>
              </div>
              
              <button 
                @click="handleOptimize" 
                class="btn btn-generate full-width"
                :disabled="isOptimizing || !concept"
              >
                <Loader2 v-if="isOptimizing" class="animate-spin" :size="20" />
                <Sparkles v-else :size="20" />
                <span>{{ isOptimizing ? t('promptAssistant.enhancing') : t('promptAssistant.enhance') }}</span>
                <div class="btn-shine"></div>
              </button>
            </div>

            <div v-if="errorMsg" class="error-toast">
              <AlertTriangle :size="16" />
              <span>{{ errorMsg }}</span>
            </div>
          </div>
        </div>
      </section>

      <!-- Result Section -->
      <section class="card-section animate-fade-up" style="animation-delay: 0.2s">
        <div class="glass-card result-card" :class="{ 'has-content': optimizedPrompt }">
          <div class="card-header">
            <h2 class="card-title"><Sparkles :size="20" /> {{ t('promptAssistant.result') }}</h2>
          </div>
          
          <div v-if="isOptimizing" class="result-loading-state animate-fade-in">
            <Loader2 class="animate-spin text-primary" :size="48" />
            <p>{{ t('promptAssistant.enhancing') }}...</p>
          </div>
          
          <div v-else-if="optimizedPrompt" class="result-content animate-fade-in">
            <div class="prompt-display">
              <p>{{ optimizedPrompt }}</p>
              <div class="display-glow"></div>
            </div>
            
            <div class="result-actions">
              <button @click="copyToClipboard" class="btn btn-secondary">
                <Copy :size="18" /> {{ t('common.copy') }}
              </button>
              <router-link to="/dashboard" class="btn btn-generate">
                {{ t('promptAssistant.useThisPrompt') }} <ArrowRight :size="18" />
                <div class="btn-shine"></div>
              </router-link>
            </div>
          </div>
          
          <div v-else class="empty-placeholder">
            <div class="placeholder-icon">
              <Wand2 :size="48" />
            </div>
            <p>{{ t('promptAssistant.optimizedPromptPlaceholder') }}</p>
          </div>
        </div>
      </section>
    </div>

    <!-- History Section -->
    <section class="history-section animate-fade-up" style="animation-delay: 0.3s">
      <div class="glass-card">
        <div class="card-header history-header">
          <h2 class="card-title"><Clock :size="20" /> {{ t('common.history') || 'History' }}</h2>
          <button @click="showHistory = !showHistory" class="btn btn-ghost btn-sm">
            {{ showHistory ? t('common.hide') : t('common.show') }}
            <ChevronDown :class="{ rotated: !showHistory }" :size="16" />
          </button>
        </div>

        <transition name="slide">
          <div v-if="showHistory" class="history-container">
            <div v-if="videoStore.historyLoading" class="loader-box">
              <Loader2 class="animate-spin" :size="32" />
            </div>

            <div v-else-if="filteredHistory.length === 0" class="empty-history">
              <p>{{ t('promptAssistant.noHistory') }}</p>
            </div>

            <div v-else class="history-grid">
              <div 
                v-for="item in filteredHistory" 
                :key="item.id" 
                class="history-card"
              >
                <div class="history-item-header">
                  <span class="date">{{ formatDate(item.created_at) }}</span>
                  <div class="tags">
                    <span class="tag style-tag">{{ item.style }}</span>
                    <span class="tag lang-tag">{{ item.language }}</span>
                  </div>
                </div>
                
                <div class="history-item-content">
                  <div class="item-section">
                    <label>{{ t('promptAssistant.concept') }}</label>
                    <p>{{ item.raw_prompt }}</p>
                  </div>
                  <div class="item-section">
                    <label>{{ t('promptAssistant.optimized') }}</label>
                    <p class="highlight">{{ item.optimized_prompt }}</p>
                  </div>
                </div>

                <div class="history-item-actions">
                  <button @click="openHistoryDetail(item)" class="action-pill" title="View Detail">
                    <Eye :size="14" />
                  </button>
                  <button @click="copyHistoryPrompt(item.optimized_prompt)" class="action-pill" title="Copy">
                    <Copy :size="14" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </transition>
      </div>
    </section>

    <!-- History Detail Modal -->
    <Transition name="fade">
      <div v-if="selectedHistoryItem" class="modal-overlay" @click.self="closeHistoryDetail">
        <div class="modal-content glass-card animate-scale-up">
          <div class="modal-header">
            <div class="title-info">
              <Clock :size="18" class="text-primary" />
              <h3>{{ t('common.details') }}</h3>
              <span class="modal-date">{{ formatDate(selectedHistoryItem.created_at) }}</span>
            </div>
            <button @click="closeHistoryDetail" class="close-btn">
              <X :size="20" />
            </button>
          </div>
          <div class="modal-body">
            <div class="detail-section">
              <div class="section-label">
                <Type :size="16" />
                <span>{{ t('promptAssistant.concept') }}</span>
              </div>
              <div class="section-content question-content">
                {{ selectedHistoryItem.raw_prompt }}
              </div>
            </div>
            <div class="detail-section">
              <div class="section-label">
                <Sparkles :size="16" />
                <span>{{ t('promptAssistant.optimized') }}</span>
              </div>
              <div class="section-content response-content">
                <div class="prompt-meta" style="margin-bottom: 1rem; display: flex; gap: 1rem;">
                  <span class="tag style-tag">{{ selectedHistoryItem.style }}</span>
                  <span class="tag lang-tag">{{ selectedHistoryItem.language }}</span>
                  <span class="tag duration-tag" v-if="selectedHistoryItem.duration">{{ selectedHistoryItem.duration }}</span>
                </div>
                <p>{{ selectedHistoryItem.optimized_prompt }}</p>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button @click="copyHistoryPrompt(selectedHistoryItem.optimized_prompt)" class="btn btn-secondary">
              <Copy :size="16" /> {{ t('common.copy') || 'Copy' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.prompt-assistant {
  padding-top: 3rem;
}

.page-header {
  text-align: center;
  margin-bottom: 4rem;
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

.main-title {
  margin-bottom: 1rem;
}

.subtitle {
  font-size: 1.25rem;
  max-width: 700px;
  margin: 0 auto 2.5rem;
}

.guide-box {
  display: inline-flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem 1.5rem;
  background: var(--bg-200);
  border: 1px solid var(--bg-300);
  border-radius: 12px;
  margin: 0 auto;
}

.guide-box p {
  color: var(--color-text-main);
  font-weight: 500;
}

.guide-link {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--color-primary);
  text-decoration: none;
  font-weight: 700;
  transition: all 0.2s;
}

.guide-link:hover {
  color: var(--color-primary-hover);
  text-decoration: underline;
}

.main-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 2.5rem;
  margin-bottom: 3rem;
}

.assistant-card, .result-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.card-header {
  padding: 1.5rem 2rem;
  border-bottom: 1px solid var(--color-border);
}

.card-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-text-main);
}

.form-body {
  padding: 2rem;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.modern-textarea {
  min-height: 180px;
  resize: vertical;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border: 1px solid #bae6fd;
  color: #0369a1;
}

.modern-textarea:focus {
  background: linear-gradient(135deg, #e0f2fe 0%, #f0f9ff 100%);
  border-color: #7dd3fc;
  box-shadow: 0 0 0 4px rgba(186, 230, 253, 0.4);
  outline: none;
}

.input-group {
  position: relative;
}

.modern-textarea {
  min-height: 180px;
  transition: min-height 0.3s ease;
}

.input-group.expanded .modern-textarea {
  min-height: 480px;
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
  color: #0369a1;
  transition: all 0.2s;
  z-index: 10;
}

.btn-expand:hover {
  background: rgba(255, 255, 255, 0.8);
  border-color: #7dd3fc;
}

.config-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

.modern-select {
  cursor: pointer;
}

.action-footer {
  margin-top: auto;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.cost-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.95rem;
  color: var(--color-text-secondary);
  justify-content: center;
}

.cost-info strong {
  color: var(--color-text-main);
}

.error-toast {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  background: rgba(220, 53, 69, 0.08);
  border: 1px solid rgba(220, 53, 69, 0.2);
  border-radius: var(--radius-md);
  color: #dc3545;
  font-size: 0.9rem;
}

/* Result Card Enhancement */
.result-loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  gap: 1.5rem;
  color: var(--color-text-muted);
}

.result-loading-state p {
  font-size: 1.1rem;
  font-weight: 500;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.result-card.has-content {
  border-color: var(--primary-200);
  background: var(--bg-100);
  box-shadow: 0 10px 30px rgba(0, 119, 194, 0.1);
}

.result-content {
  padding: 2.5rem;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.prompt-display {
  flex: 1;
  padding: 2rem;
  background: var(--bg-100);
  border: 1px dashed var(--bg-300);
  border-radius: 12px;
  font-size: 1.125rem;
  line-height: 1.8;
  color: var(--color-text-main);
  position: relative;
  min-height: 200px;
  overflow: hidden;
}

.display-glow {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: radial-gradient(circle at 50% 50%, var(--color-primary-glow) 0%, transparent 80%);
  opacity: 0.1;
  pointer-events: none;
}

.result-actions {
  display: flex;
  gap: 1rem;
}

.result-actions .btn {
  flex: 1;
}

.empty-placeholder {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1.5rem;
  color: var(--color-text-muted);
  padding: 4rem;
}

.placeholder-icon {
  width: 80px;
  height: 80px;
  background: var(--color-surface);
  border-radius: 50%;
  border: 2px dashed var(--color-border);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-border);
}

/* History Section */
.history-section {
  margin-top: 1rem;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.history-header .rotated {
  transform: rotate(-90deg);
}

.history-container {
  padding: 2rem;
  max-height: 600px;
  overflow-y: auto;
}

.history-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.5rem;
}

.history-card {
  background: var(--bg-100);
  border: 1px solid var(--bg-300);
  border-radius: var(--radius-md);
  padding: 1.5rem;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  position: relative;
}

.history-card:hover {
  background: var(--bg-200);
  border-color: var(--primary-200);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.history-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.date {
  font-size: 0.75rem;
  color: var(--color-text-muted);
}

.tags {
  display: flex;
  gap: 0.5rem;
}

.tag {
  font-size: 0.7rem;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-weight: 600;
  text-transform: uppercase;
}

.style-tag { background: var(--color-primary); color: white; }
.lang-tag { background: var(--color-surface-hover); color: var(--color-text-secondary); }

.item-section label {
  display: block;
  font-size: 0.7rem;
  text-transform: uppercase;
  color: var(--color-text-muted);
  font-weight: 700;
  margin-bottom: 0.25rem;
}

.item-section p {
  font-size: 0.9rem;
  color: var(--color-text-secondary);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.item-section p.highlight {
  color: var(--color-text-main);
}

.history-item-actions {
  display: flex;
  gap: 0.75rem;
}

.action-pill {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: 1px solid var(--color-border);
  background: transparent;
  color: var(--color-text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}

.action-pill:hover {
  background: var(--color-primary-glow);
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.action-pill.primary {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: white;
}

@media (max-width: 1200px) {
  .main-grid {
    grid-template-columns: 1fr;
  }
}
.fullscreen-editor-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(20px);
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.editor-container {
  width: 95vw;
  height: 90vh;
  max-width: 1400px;
  background: var(--bg-100);
  display: flex;
  flex-direction: column;
  box-shadow: 0 30px 60px rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.editor-header {
  padding: 1.5rem 2rem;
  border-bottom: 1px solid var(--color-border);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--bg-100);
}

.header-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.header-info h3 {
  font-size: 1.25rem;
  font-weight: 700;
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.editor-main {
  flex: 1;
  padding: 1.5rem;
  background: var(--bg-100);
  overflow: hidden;
}

.fullscreen-textarea {
  width: 100%;
  height: 100%;
  padding: 2rem;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border: 1px solid #bae6fd;
  border-radius: 12px;
  font-size: 1.15rem;
  line-height: 1.8;
  color: #0369a1;
  resize: none;
  outline: none;
  font-family: inherit;
  transition: all 0.3s ease;
}

.fullscreen-textarea:focus {
  background: linear-gradient(135deg, #e0f2fe 0%, #f0f9ff 100%);
  border-color: #7dd3fc;
  box-shadow: 0 0 0 4px rgba(186, 230, 253, 0.4);
}

@media (max-width: 768px) {
  .editor-container {
    height: 95vh;
    width: 98vw;
  }
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
  z-index: 3000;
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

.response-content p {
  white-space: pre-wrap;
  word-wrap: break-word;
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

.duration-tag {
  background: var(--bg-300);
  color: var(--color-text-main);
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
