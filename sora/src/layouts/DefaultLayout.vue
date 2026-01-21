<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { 
  Video, 
  Sparkles, 
  History, 
  LogOut, 
  LayoutDashboard,
  Coins,
  Settings,
  ChevronRight,
  Headphones,
  Bell
} from 'lucide-vue-next'
import LanguageSwitcher from '@/components/LanguageSwitcher.vue'
import ToastContainer from '@/components/ToastContainer.vue'
import AnnouncementBanner from '@/components/AnnouncementBanner.vue'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()
const { t } = useI18n()

function handleLogout() {
  authStore.logout()
  router.push('/')
}
</script>

<template>
  <div class="app-layout">
    <!-- Sidebar -->
    <aside v-if="authStore.isAuthenticated" class="sidebar-container">
      <div class="sidebar glass-card">
        <div class="logo-container">
          <div class="logo-icon-wrapper">
            <Video class="logo-icon" :size="24" />
          </div>
          <span class="logo-text">SoraGen</span>
        </div>

        <nav class="nav-menu">
          <router-link to="/dashboard" class="nav-item" active-class="active">
            <div class="icon-wrapper"><LayoutDashboard :size="20" /></div>
            <span>{{ t('nav.generator') }}</span>
            <ChevronRight class="chevron" :size="16" />
          </router-link>
          
          <router-link to="/prompt-assistant" class="nav-item" active-class="active">
            <div class="icon-wrapper"><Sparkles :size="20" /></div>
            <span>{{ t('nav.assistant') }}</span>
            <ChevronRight class="chevron" :size="16" />
          </router-link>
          
          <router-link to="/history" class="nav-item" active-class="active">
            <div class="icon-wrapper"><History :size="20" /></div>
            <span>{{ t('nav.history') }}</span>
            <ChevronRight class="chevron" :size="16" />
          </router-link>

          <router-link to="/faq" class="nav-item" active-class="active">
            <div class="icon-wrapper"><Headphones :size="20" /></div>
            <span>{{ t('nav.faq') }}</span>
            <ChevronRight class="chevron" :size="16" />
          </router-link>

          <router-link to="/announcements" class="nav-item" active-class="active">
            <div class="icon-wrapper"><Bell :size="20" /></div>
            <span>{{ t('nav.announcements') }}</span>
            <ChevronRight class="chevron" :size="16" />
          </router-link>
        </nav>

        <div class="sidebar-footer">
          <LanguageSwitcher class="sidebar-lang" />
          
          <div class="user-profile">
            <router-link to="/profile" class="user-info-link">
              <div class="user-info">
                <div class="avatar-wrapper">
                  <div class="avatar">{{ authStore.user?.username?.charAt(0).toUpperCase() }}</div>
                  <div class="avatar-glow"></div>
                </div>
                <div class="details">
                  <span class="username">{{ authStore.user?.username }}</span>
                  <div class="credits">
                    <Coins :size="14" class="text-primary" />
                    <span>{{ authStore.user?.credits }}</span>
                  </div>
                </div>
              </div>
            </router-link>
            <button @click="handleLogout" class="logout-btn" :title="t('nav.logout')">
              <LogOut :size="18" />
            </button>
          </div>
        </div>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="main-content">
      <AnnouncementBanner />
      <div class="content-wrapper">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
      
      <footer v-if="route.name !== 'home'" class="app-footer">
        <div class="footer-content glass-card">
          <p class="footer-slogan">{{ t('footer.slogan') }}</p>
          
          <div class="footer-contact-section">
            <el-popover
              placement="top"
              :width="300"
              trigger="click"
            >
              <template #reference>
                <span class="footer-contact-trigger">{{ t('contact.title') }}</span>
              </template>
              <div class="contact-popover">
                <p style="margin: 5px 0; color: #606266;">{{ t('contact.wechat') }}</p>
                <p style="margin: 5px 0; color: #606266;">{{ t('contact.email') }}</p>
              </div>
            </el-popover>
          </div>

          <div class="footer-beian">
            <a href="https://beian.miit.gov.cn/" target="_blank" rel="noopener noreferrer">
              {{ t('footer.beian') }}
            </a>
          </div>
        </div>
      </footer>
    </main>
    <ToastContainer />
  </div>
</template>

<style scoped>
.app-layout {
  display: flex;
  height: 100vh;
  width: 100vw;
  background: var(--color-background);
  overflow: hidden;
}

/* Sidebar Styling */
.sidebar-container {
  width: var(--sidebar-width);
  padding: 1rem;
  position: sticky;
  top: 0;
  height: 100vh;
  z-index: 10;
  box-sizing: border-box;
}

.sidebar {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 1.5rem;
  gap: 1.5rem;
  background: var(--bg-100);
  border: 1px solid var(--bg-300);
  box-sizing: border-box;
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 3.5rem;
  padding-left: 0.5rem;
}

.logo-icon-wrapper {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, var(--color-primary) 0%, #4338ca 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 15px var(--color-primary-glow);
}

.logo-icon {
  color: white;
}

.logo-text {
  font-size: 1.25rem;
  font-weight: 800;
  color: var(--color-primary);
  font-family: var(--font-heading);
}

.nav-menu {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.25rem;
  border-radius: var(--radius-md);
  color: var(--color-text-secondary);
  font-weight: 600;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  text-decoration: none;
  font-family: var(--font-heading);
  position: relative;
  overflow: hidden;
}

.nav-item:hover {
  background: var(--bg-200);
  color: var(--primary-100);
}

.nav-item.active {
  background: var(--primary-100);
  color: white;
  box-shadow: 0 4px 12px rgba(0, 119, 194, 0.2);
  border: 1px solid rgba(0, 112, 192, 0.1);
}

.nav-item.active .icon-wrapper {
  color: white;
}

.nav-item.active .chevron {
  opacity: 1;
  transform: translateX(0);
}

.chevron {
  margin-left: auto;
  opacity: 0;
  transform: translateX(-10px);
  transition: all 0.3s ease;
}

.icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

/* User Profile */
.sidebar-footer {
  margin-top: auto;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.sidebar-lang {
  width: 100%;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  border-top: 1px solid var(--color-border);
}

.user-info-link {
  flex: 1;
  text-decoration: none;
  color: inherit;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  border-radius: 12px;
  background: var(--bg-200);
  border: 1px solid var(--bg-300);
  transition: all 0.2s;
  overflow: hidden; /* Keep this from original .user-info */
}

.user-info:hover {
  border-color: var(--primary-200);
  background: white;
}

.avatar-wrapper {
  position: relative;
}

.avatar {
  width: 40px;
  height: 40px;
  background: var(--primary-100);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1.125rem;
}

/* Removed avatar glow for simpler style */

.details {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.username {
  font-weight: 700;
  font-size: 0.95rem;
  color: var(--color-text-main);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-family: var(--font-heading);
}

.credits {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.85rem;
  color: var(--color-text-secondary);
  font-weight: 600;
}

.text-primary { color: var(--color-primary); }

.logout-btn {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  background: var(--bg-200);
  border: 1px solid var(--bg-300);
  color: var(--text-200);
  cursor: pointer;
  transition: all 0.2s;
}

.logout-btn:hover {
  background: #fee2e2;
  color: var(--color-error);
  border-color: #fecaca;
}

/* Main Content area */
.main-content {
  flex: 1;
  overflow-y: auto;
  position: relative;
  display: flex;
  flex-direction: column;
  background-color: var(--color-background);
}

.content-wrapper {
  flex: 1;
  padding-bottom: 4rem;
}

.app-footer {
  padding: 0 2.5rem 2.5rem;
  margin-top: auto;
}

.footer-content {
  padding: 1.5rem;
  text-align: center;
  border-radius: var(--radius-md);
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 2rem;
  flex-wrap: wrap;
}

.footer-slogan {
  font-size: 0.9rem;
  font-weight: 600;
  margin: 0;
  color: var(--color-text-main);
  font-family: var(--font-heading);
}

.footer-contact-trigger {
  cursor: pointer;
  color: var(--color-text-muted);
  font-size: 0.8rem;
  transition: color 0.2s;
  font-weight: 600;
}

.footer-contact-trigger:hover {
  color: var(--color-primary);
}

.footer-contact-section {
  display: flex;
  align-items: center;
}

.footer-beian a {
  font-size: 0.75rem;
  color: var(--color-text-muted);
  text-decoration: none;
  transition: color 0.2s;
}

.footer-beian a:hover {
  color: var(--color-primary);
}

/* Transition */
.fade-enter-active,
.fade-leave-active {
  transition: all 0.3s ease;
}

.fade-enter-from { opacity: 0; transform: translateY(10px); }
.fade-leave-to { opacity: 0; transform: translateY(-10px); }

@media (max-width: 1024px) {
  .sidebar-container {
    display: none; /* Add a mobile drawer here in real projects */
  }
}
</style>
