<template>
  <transition name="el-zoom-in-top">
    <div v-if="visibleAnnouncement && !isClosedForSession" class="announcement-card glass-card">
      <div class="card-header">
        <div class="header-left">
          <Megaphone :size="18" class="icon" />
          <span class="title">{{ visibleAnnouncement.title }}</span>
        </div>
        <button @click="handleSessionClose" class="close-icon-btn" :title="t('common.close')">
          <X :size="16" />
        </button>
      </div>
      
      <div class="card-body">
        <p class="content">{{ visibleAnnouncement.content }}</p>
      </div>
      
      <div class="card-footer">
        <el-button size="small" @click="handleSessionClose">
          {{ t('common.close') }}
        </el-button>
        <el-button size="small" type="primary" plain @click="handlePermanentDismiss">
          {{ t('announcements.dontShowAgain') }}
        </el-button>
      </div>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Megaphone, X } from 'lucide-vue-next'
import api from '@/utils/api'
import { useAuthStore } from '@/stores/auth'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const authStore = useAuthStore()
const visibleAnnouncement = ref<any>(null)
const isClosedForSession = ref(false)

const checkBanner = async () => {
    if (!authStore.isAuthenticated) return

    try {
        const response = await api.get('adym/user/announcements/unread/')
        const allAnnouncements = response.data
        
        // Find the first one that is NOT dismissed
        const active = allAnnouncements.find((a: any) => !a.is_dismissed)
        
        if (active) {
            // Check if user already closed this ID in this session
            const sessionKey = `ann_closed_${active.id}`
            if (sessionStorage.getItem(sessionKey)) {
                isClosedForSession.value = true
            }
            visibleAnnouncement.value = active
        }
    } catch (e) {
        // silent error
    }
}

const handleSessionClose = () => {
    if (!visibleAnnouncement.value) return
    const id = visibleAnnouncement.value.id
    sessionStorage.setItem(`ann_closed_${id}`, 'true')
    isClosedForSession.value = true
}

const handlePermanentDismiss = async () => {
    if (!visibleAnnouncement.value) return
    
    const id = visibleAnnouncement.value.id
    // Hide immediately
    visibleAnnouncement.value = null
    
    // Call backend to mark as dismissed forever
    try {
        await api.post('adym/user/announcements/acknowledge/', { id })
    } catch (e) {
       console.error(e)
    }
}

onMounted(() => {
    setTimeout(checkBanner, 1500)
})
</script>

<style scoped>
.announcement-card {
  position: fixed;
  top: 80px; /* Below the header */
  right: 24px;
  width: 320px;
  z-index: 2000;
  padding: 16px;
  border: 1px solid var(--bg-300);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--color-primary);
}

.title {
  font-weight: 600;
  font-size: 0.95rem;
  color: var(--text-100);
}

.close-icon-btn {
  background: transparent;
  border: none;
  color: var(--text-300);
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  display: flex;
  transition: all 0.2s;
}

.close-icon-btn:hover {
  background: var(--bg-300);
  color: var(--text-100);
}

.card-body {
  max-height: 120px;
  overflow-y: auto;
}

.content {
  font-size: 0.85rem;
  color: var(--text-200);
  line-height: 1.5;
  margin: 0;
}

.card-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 4px;
}

/* Glass effect refinement if needed, though glass-card is likely global */
.glass-card {
  background: rgba(var(--bg-100-rgb), 0.8) !important;
  backdrop-filter: blur(16px) !important;
}

@media (max-width: 480px) {
  .announcement-card {
    left: 24px;
    right: 24px;
    width: auto;
    top: auto;
    bottom: 24px;
  }
}
</style>
