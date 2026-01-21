<template>
  <div class="faq-view animate-fade-up">
    <div class="header-section">
      <h1 class="title">{{ t('faq.title') }}</h1>
      <p class="subtitle">{{ t('faq.subtitle') }}</p>
    </div>

    <div v-if="loading" class="loading-state">
      <el-skeleton :rows="10" animated />
    </div>

    <div v-else-if="faqs.length === 0" class="empty-state glass-card">
      <div class="empty-icon"><HelpCircle :size="48" /></div>
      <h3>{{ t('faq.noFaqs') }}</h3>
    </div>

    <div v-else class="faq-accordion">
      <div v-for="faq in faqs" :key="faq.id" class="faq-item glass-card" :class="{ active: activeId === faq.id }">
        <div class="faq-question" @click="toggleFaq(faq.id)">
          <span class="q-text">{{ locale === 'zh' ? faq.question_zh : faq.question_en }}</span>
          <ChevronDown class="chevron" :size="20" />
        </div>
        <div class="faq-answer">
          <div class="answer-inner" v-html="formatAnswer(locale === 'zh' ? faq.answer_zh : faq.answer_en)"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { HelpCircle, ChevronDown } from 'lucide-vue-next'
import api from '@/utils/api'

const { t, locale } = useI18n()
const loading = ref(true)
const faqs = ref<any[]>([])
const activeId = ref<number | null>(null)

const fetchFaqs = async () => {
  loading.value = true
  try {
    const response = await api.get('adym/user/faqs/')
    faqs.value = response.data
  } catch (e) {
    console.error('Failed to fetch FAQs', e)
  } finally {
    loading.value = false
  }
}

const toggleFaq = (id: number) => {
  activeId.value = activeId.value === id ? null : id
}

const formatAnswer = (text: string) => {
  if (!text) return ''
  return text
    .split('\n\n')
    .map(p => `<p>${p.replace(/\n/g, '<br>')}</p>`)
    .join('')
}

onMounted(fetchFaqs)
</script>

<style scoped>
.faq-view {
  padding: 2.5rem;
  max-width: 900px;
  margin: 0 auto;
}

.header-section {
  margin-bottom: 3rem;
  text-align: center;
}

.title {
  font-size: 2.25rem;
  font-weight: 800;
  color: var(--color-text-main);
  margin-bottom: 0.5rem;
  letter-spacing: -0.02em;
}

.subtitle {
  color: var(--color-text-secondary);
  font-size: 1.1rem;
}

.faq-accordion {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.faq-item {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid var(--color-border);
}

.faq-item:hover {
  border-color: var(--color-primary-light);
  transform: translateY(-2px);
  box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.1);
}

.faq-item.active {
  border-color: var(--color-primary);
  background: rgba(var(--color-primary-rgb), 0.02);
}

.faq-question {
  padding: 1.5rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  font-weight: 700;
  color: var(--color-text-main);
  user-select: none;
  font-size: 1.1rem;
}

.q-text {
  flex: 1;
  padding-right: 1.5rem;
}

.chevron {
  transition: transform 0.3s ease;
  color: var(--color-text-muted);
}

.faq-item.active .chevron {
  transform: rotate(180deg);
  color: var(--color-primary);
}

.faq-answer {
  max-height: 0;
  overflow: hidden;
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.faq-item.active .faq-answer {
  max-height: 1000px;
}

.answer-inner {
  padding: 0 2rem 2rem;
  color: var(--color-text-secondary);
  line-height: 1.8;
  font-size: 1rem;
}

.answer-inner :deep(p) {
  margin-bottom: 1.25rem;
}

.answer-inner :deep(p:last-child) {
  margin-bottom: 0;
}

.loading-state {
  padding: 2rem;
}

.empty-state {
  text-align: center;
  padding: 5rem 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
}

.empty-icon {
  color: var(--color-text-muted);
  opacity: 0.5;
}

@media (max-width: 768px) {
  .faq-view {
    padding: 1.5rem;
  }
  .title {
    font-size: 1.75rem;
  }
  .faq-question {
    padding: 1.25rem 1.5rem;
    font-size: 1rem;
  }
  .answer-inner {
    padding: 0 1.5rem 1.5rem;
  }
}
</style>
