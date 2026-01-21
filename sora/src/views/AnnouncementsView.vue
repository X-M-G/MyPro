<template>
  <div class="announcements-view animate-fade-up">
    <div class="header-section">
      <h1 class="title">{{ t('announcements.title') }}</h1>
      <p class="subtitle">{{ t('announcements.subtitle') }}</p>
    </div>

    <div v-if="loading" class="loading-state">
      <el-skeleton :rows="5" animated />
    </div>

    <div v-else-if="announcements.length === 0" class="empty-state glass-card">
      <div class="empty-icon"><Bell :size="48" /></div>
      <h3>{{ t('announcements.noAnnouncements') }}</h3>
      <p>{{ t('announcements.backLater') }}</p>
    </div>

    <div v-else class="timeline">
      <div v-for="ann in announcements" :key="ann.id" class="announcement-card glass-card">
        <div class="card-header">
          <h2 class="ann-title">{{ ann.title }}</h2>
          <span class="ann-date">{{ formatDate(ann.created_at) }}</span>
        </div>
        <div class="ann-content">
          {{ ann.content }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { Bell } from 'lucide-vue-next'
import api from '@/utils/api'

const { t } = useI18n()
const loading = ref(true)
const announcements = ref<any[]>([])

const fetchAnnouncements = async () => {
    loading.value = true
    try {
        const response = await api.get('adym/user/announcements/')
        announcements.value = response.data
    } catch (e) {
        console.error('Failed to fetch announcements', e)
    } finally {
        loading.value = false
    }
}

const formatDate = (dateStr: string) => {
    const d = new Date(dateStr)
    return d.toLocaleString([], { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

onMounted(() => {
    fetchAnnouncements()
})
</script>

<style scoped>
.announcements-view {
  padding: 2.5rem;
  max-width: 900px;
  margin: 0 auto;
}

.header-section {
  margin-bottom: 3rem;
}

.title {
  font-size: 2.25rem;
  font-weight: 800;
  color: var(--color-text-main);
  margin-bottom: 0.5rem;
  font-family: var(--font-heading);
}

.subtitle {
  color: var(--color-text-secondary);
}

.timeline {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.announcement-card {
  padding: 2rem;
  border-radius: var(--radius-lg);
  transition: transform 0.3s ease;
}

.announcement-card:hover {
  transform: translateY(-4px);
  border-color: var(--primary-200);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.25rem;
  gap: 1rem;
}

.ann-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-primary);
  margin: 0;
  font-family: var(--font-heading);
}

.ann-date {
  font-size: 0.85rem;
  color: var(--color-text-muted);
  white-space: nowrap;
}

.ann-content {
  line-height: 1.6;
  color: var(--color-text-main);
  white-space: pre-wrap;
}

.empty-state {
  text-align: center;
  padding: 5rem 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.empty-icon {
  color: var(--color-text-muted);
  opacity: 0.5;
}

.empty-state h3 {
  margin: 0;
  font-size: 1.25rem;
}

.empty-state p {
  color: var(--color-text-muted);
}
</style>
