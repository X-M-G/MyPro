<template>
  <el-container class="layout-container admin-theme animate-fade-in">
    <!-- Sidebar -->
    <el-aside width="var(--sidebar-width)" class="aside">
      <div class="logo-area">
        <div class="logo-box">
          <div class="logo-inner">S</div>
        </div>
        <div class="logo-info">
          <h2 class="logo-title">{{ $t('admin.systemTitle') }}</h2>
          <span class="logo-subtitle">{{ $t('admin.systemSubtitle') }}</span>
        </div>
      </div>

      <el-scrollbar>
        <el-menu
          :default-active="activePath"
          class="admin-menu"
          router
        >
          <el-menu-item index="/adym/dashboard">
            <el-icon><Odometer /></el-icon>
            <span>{{ $t('admin.dashboard') }}</span>
          </el-menu-item>
          <el-menu-item index="/adym/users">
            <el-icon><User /></el-icon>
            <span>{{ $t('admin.users') }}</span>
          </el-menu-item>
          <el-menu-item index="/adym/logs">
            <el-icon><Document /></el-icon>
            <span>{{ $t('admin.logs') }}</span>
          </el-menu-item>
          <el-menu-item index="/adym/announcements">
            <el-icon><Bell /></el-icon>
            <span>{{ $t('admin.announcements') }}</span>
          </el-menu-item>
          <el-menu-item index="/adym/faqs">
            <el-icon><Service /></el-icon>
            <span>{{ $t('admin.faqs') }}</span>
          </el-menu-item>
        </el-menu>
      </el-scrollbar>
      
      <div class="aside-footer">
        <div class="pro-badge">
          <span class="dot"></span>
          {{ $t('admin.enterpriseEdition') }}
        </div>
      </div>
    </el-aside>
    
    <el-container class="main-stage">
      <!-- Header -->
      <el-header class="admin-header">
        <div class="header-breadcrumb">
          <div class="breadcrumb-root">{{ $t('admin.management') }}</div>
          <el-icon class="breadcrumb-arrow"><ArrowRight /></el-icon>
          <div class="breadcrumb-current">{{ pageTitle }}</div>
        </div>
        
        <div class="header-tools">
          <el-tooltip :content="$t('admin.terminateSession')" placement="bottom">
            <button class="subtle-tool-btn" @click="handleUserCommand('logout')">
              <SwitchButton :size="18" />
            </button>
          </el-tooltip>
        </div>
      </el-header>
      
      <!-- Content Area -->
      <el-main class="admin-main">
        <router-view v-slot="{ Component }">
          <transition name="page-fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { 
  Odometer, User, ArrowDown, ArrowRight, Service, 
  Document, Bell, HomeFilled, SwitchButton 
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const { locale, t } = useI18n()

onMounted(() => {
  // Force admin to Chinese
  locale.value = 'zh'
})

const activePath = computed(() => route.path)

const pageTitle = computed(() => {
  if (route.path.includes('dashboard')) return t('admin.dashboard')
  if (route.path.includes('users')) return t('admin.users')
  if (route.path.includes('logs')) return t('admin.logs')
  if (route.path.includes('announcements')) return t('admin.announcements')
  if (route.path.includes('faqs')) return t('admin.faqs')
  return t('admin.portfolio')
})

const handleUserCommand = (command: string) => {
  if (command === 'logout') {
    localStorage.removeItem('auth_token')
    router.push('/login')
  } else if (command === 'home') {
    router.push('/')
  }
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
  background-color: var(--admin-surface);
  overflow: hidden;
  display: flex;
}

/* Sidebar Styles */
.aside {
  background-color: var(--admin-sidebar-bg);
  box-shadow: 10px 0 30px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  z-index: 100;
  transition: all 0.4s cubic-bezier(0.23, 1, 0.32, 1);
  border-right: 1px solid rgba(255, 255, 255, 0.05);
}

.logo-area {
  height: 100px;
  display: flex;
  align-items: center;
  padding: 0 24px;
  gap: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.logo-box {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, var(--admin-accent-gold) 0%, #8e6e3c 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 16px rgba(197, 160, 89, 0.2);
}

.logo-inner {
  font-size: 1.2rem;
  font-weight: 800;
  color: white;
  font-family: var(--font-heading);
}

.logo-title {
  font-size: 1.15rem;
  font-weight: 700;
  color: white;
  letter-spacing: -0.01em;
  margin: 0;
}

.logo-subtitle {
  font-size: 0.7rem;
  color: rgba(255, 255, 255, 0.4);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  font-weight: 600;
}

.admin-menu {
  border-right: none;
  background-color: transparent !important;
  padding: 24px 16px;
}

:deep(.el-menu-item) {
  height: 54px;
  line-height: 54px;
  border-radius: 12px;
  margin-bottom: 8px;
  color: rgba(255, 255, 255, 0.5) !important;
  font-size: 0.95rem;
  transition: all 0.3s cubic-bezier(0.23, 1, 0.32, 1);
}

:deep(.el-menu-item:hover) {
  background-color: rgba(255, 255, 255, 0.03) !important;
  color: white !important;
  transform: translateX(4px);
}

:deep(.el-menu-item.is-active) {
  background: var(--admin-active-bg) !important;
  color: var(--admin-active-text) !important;
  font-weight: 700;
}

:deep(.el-menu-item .el-icon) {
  font-size: 20px;
  margin-right: 12px;
}

.aside-footer {
  padding: 32px 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.subtle-tool-btn {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 1px solid var(--admin-border);
  color: var(--admin-text-secondary);
  cursor: pointer;
  transition: all 0.2s;
  margin-left: 12px;
}

.subtle-tool-btn:hover {
  background: var(--admin-surface-alt);
  color: var(--admin-accent-orange);
  border-color: var(--admin-accent-orange);
}

.pro-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.6);
  font-weight: 600;
}

.pro-badge .dot {
  width: 6px;
  height: 6px;
  background: var(--admin-accent-teal);
  border-radius: 50%;
  box-shadow: 0 0 8px var(--admin-accent-teal);
}

/* Header Styles */
.admin-header {
  height: 80px;
  background: var(--admin-surface-alt);
  border-bottom: 1px solid var(--admin-border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 40px;
  z-index: 90;
}

.header-breadcrumb {
  display: flex;
  align-items: center;
  gap: 12px;
}

.breadcrumb-root {
  color: var(--admin-text-secondary);
  font-size: 0.9rem;
  font-weight: 500;
}

.breadcrumb-arrow {
  font-size: 14px;
  color: rgba(0, 0, 0, 0.15);
}

.breadcrumb-current {
  color: var(--admin-text-primary);
  font-weight: 700;
  font-size: 1rem;
  letter-spacing: -0.01em;
}

.header-tools {
  display: flex;
  align-items: center;
  gap: 12px;
}

.tool-btn {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 14px;
  background: white;
  border: 1px solid var(--admin-border);
  color: var(--admin-text-secondary);
  cursor: pointer;
  transition: all 0.3s;
}

.tool-btn:hover {
  border-color: var(--admin-accent-teal);
  color: var(--admin-accent-teal);
  box-shadow: 0 4px 12px rgba(42, 157, 143, 0.1);
  transform: translateY(-2px);
}

.tool-divider {
  width: 1px;
  height: 24px;
  background: var(--admin-border);
  margin: 0 8px;
}

.lang-btn {
  width: auto;
  padding: 0 16px;
  gap: 8px;
}

.btn-text {
  font-size: 0.85rem;
  font-weight: 800;
  letter-spacing: 0.05em;
}

.profile-chip {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 6px 16px 6px 8px;
  background: white;
  border: 1px solid var(--admin-border);
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.3s;
}

.profile-chip:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.05);
  transform: translateY(-2px);
  border-color: var(--admin-accent-gold);
}

.profile-avatar {
  width: 38px;
  height: 38px;
  background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
  border-radius: 50%;
  color: white;
  font-size: 0.8rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 4px solid var(--admin-surface-alt);
}

.profile-info {
  display: flex;
  flex-direction: column;
}

.p-name {
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--admin-text-primary);
  line-height: 1.2;
}

.p-role {
  font-size: 0.65rem;
  color: var(--admin-text-secondary);
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.p-arrow {
  color: var(--admin-text-secondary);
}

/* Page Content */
.admin-main {
  background: var(--admin-surface);
  padding: 40px;
  overflow-y: auto;
}

/* Page Transitions */
.page-fade-enter-active,
.page-fade-leave-active {
  transition: all 0.4s cubic-bezier(0.23, 1, 0.32, 1);
}

.page-fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.page-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* Styled Popovers & Menus */
:deep(.executive-popover) {
  border-radius: 20px !important;
  border: 1px solid var(--admin-border) !important;
  box-shadow: var(--admin-shadow-hover) !important;
  padding: 0 !important;
  overflow: hidden;
}

.support-panel {
  padding: 24px;
}

.panel-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--admin-text-primary);
  margin-bottom: 20px;
}

.panel-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.panel-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px;
  border-radius: 12px;
  background: var(--admin-surface-alt);
  transition: all 0.2s;
}

.panel-item:hover {
  background: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.item-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.item-icon.teal { background: rgba(42, 157, 143, 0.1); color: var(--admin-accent-teal); }
.item-icon.gold { background: rgba(197, 160, 89, 0.1); color: var(--admin-accent-gold); }

.item-info {
  display: flex;
  flex-direction: column;
}

.item-info .label {
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--admin-text-secondary);
  text-transform: uppercase;
}

.item-info .value {
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--admin-text-primary);
}

:deep(.executive-dropdown) {
  border-radius: 16px !important;
  padding: 8px !important;
  border: 1px solid var(--admin-border) !important;
  box-shadow: var(--admin-shadow-hover) !important;
  margin-top: 10px !important;
}

:deep(.el-dropdown-menu__item) {
  padding: 10px 20px !important;
  border-radius: 10px !important;
  font-weight: 600 !important;
  font-size: 0.9rem !important;
}

:deep(.danger-item) {
  color: var(--color-error) !important;
}
</style>
