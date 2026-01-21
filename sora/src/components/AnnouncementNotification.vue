<template>
  <!-- Invisible component for logic -->
  <div v-if="false"></div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { ElNotification } from 'element-plus'
import api from '@/utils/api'
import { Bell } from 'lucide-vue-next'
import { h } from 'vue'

const authStore = useAuthStore()

const checkAnnouncements = async () => {
    // Only check if authenticated and not yet checked this session
    if (!authStore.isAuthenticated) return
    
    const token = localStorage.getItem('auth_token')
    if (!token) return

    // We rely on backend logic (once per day) to determine if we show popups.
    // The previous session check is redundant now.

    try {
        const response = await api.get('adym/user/announcements/unread/')
        const unread = response.data

        if (unread && unread.length > 0) {
            // Logic: Show popup IF created_at is within last 3 days
            // regardless of dismissed status (user said "every login")
            const threeDaysAgo = new Date()
            threeDaysAgo.setDate(threeDaysAgo.getDate() - 3)

            const recentAnnouncements = unread.filter((ann: any) => {
                const createdDate = new Date(ann.created_at)
                return createdDate > threeDaysAgo
            })

            // Show up to 2 notifications
            recentAnnouncements.slice(0, 2).forEach((ann: any) => {
                ElNotification({
                    title: ann.title,
                    message: h('div', { class: 'notification-content' }, [
                        h('p', { style: 'margin: 0; line-height: 1.4;' }, ann.content),
                    ]),
                    icon: h(Bell, { size: 24, style: 'color: var(--color-primary)' }),
                    duration: 8000,
                    position: 'top-right',
                    customClass: 'glass-card announcement-notification'
                })
                // No auto-acknowledge here, as closing popup doesn't mean "dismissed forever" for the banner
            })
        }
    } catch (e) {
        console.error('Failed to check announcements', e)
    }
}

onMounted(() => {
    // Wait a bit for layout to settle
    setTimeout(checkAnnouncements, 1000)
})
</script>

<style>
.announcement-notification {
    background: var(--bg-100) !important;
    border: 1px solid var(--bg-300) !important;
    backdrop-filter: blur(12px) !important;
}
</style>
