<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import LanguageSwitcher from '@/components/LanguageSwitcher.vue'
import { Video, Sparkles, Rocket, ArrowRight, Headphones } from 'lucide-vue-next'

const { t } = useI18n()
const router = useRouter()
const authStore = useAuthStore()

const showContact = ref(false)

function handleAction() {
  if (authStore.isAuthenticated) {
    router.push('/dashboard')
  } else {
    router.push('/login')
  }
}
</script>

<template>
  <div class="home-page">
    <div class="ambient-bg">
      <div class="ambient-light ambient-light-1"></div>
      <div class="ambient-light ambient-light-2"></div>
      <div class="ambient-light ambient-light-3"></div>
    </div>
    <!-- Navbar -->
    <nav class="navbar glass-nav">
      <div class="logo">
        <Video class="logo-icon" :size="32" />
        <span>SoraGen</span>
      </div>
      <div class="nav-actions">
        <LanguageSwitcher />
        <button v-if="!authStore.isAuthenticated" @click="router.push('/login')" class="btn btn-secondary">
          {{ t('home.hero.loginBtn') }}
        </button>
        <button v-else @click="router.push('/dashboard')" class="btn btn-primary">
           {{ t('home.hero.dashboardBtn') }}
        </button>
      </div>
    </nav>

    <!-- Background Content -->

    <div class="scroll-container">
      <!-- Hero Section -->
      <section class="hero-section">
         <div class="hero-content animate-fade-up">
            <div class="badge">
              <Sparkles :size="14" class="text-primary" />
              <span>{{ t('home.hero.platformBadge') }}</span>
            </div>
            <h1 class="main-title">{{ t('home.hero.title') }}</h1>
            <p class="hero-subtitle">{{ t('home.hero.subtitle') }}</p>
            <div class="hero-actions">
              <button @click="handleAction" class="btn btn-primary btn-lg">
                {{ authStore.isAuthenticated ? t('home.hero.dashboardBtn') : t('home.hero.startBtn') }}
                <ArrowRight :size="20" />
                <div class="btn-shine"></div>
              </button>
            </div>
         </div>
      </section>

      <!-- Content Grid -->
      <div class="content-grid">
        <!-- Introduction Section -->
        <section class="info-card glass-card animate-fade-up" style="animation-delay: 0.1s">
           <div class="card-icon-wrapper">
             <Sparkles class="card-icon" :size="32" />
           </div>
           <h2>{{ t('home.introduction.title') }}</h2>
           <p>{{ t('home.introduction.description') }}</p>
        </section>

        <!-- About Section -->
        <section class="info-card glass-card animate-fade-up" style="animation-delay: 0.2s">
           <div class="card-icon-wrapper">
             <Rocket class="card-icon" :size="32" />
           </div>
           <h2>{{ t('home.about.title') }}</h2>
           <p>{{ t('home.about.description') }}</p>
        </section>
      </div>

      <!-- Services Overview Section -->
      <section class="services-overview animate-fade-up" style="animation-delay: 0.3s">
        <div class="section-header">
          <h2 class="section-title">{{ t('home.services.title') }}</h2>
          <p class="section-subtitle">{{ t('home.services.subtitle') }}</p>
        </div>

        <div class="table-container glass-card mb-4">
          <div class="responsive-table">
            <table class="custom-table">
              <thead>
                <tr>
                  <th>{{ t('home.services.table.model') }}</th>
                  <th>{{ t('home.services.table.features') }}</th>
                  <th>{{ t('home.services.table.duration') }}</th>
                  <th>{{ t('home.services.table.resolution') }}</th>
                  <th>{{ t('home.services.table.cost') }}</th>
                  <th>{{ t('home.services.table.eta') }}</th>
                  <th>{{ t('home.services.table.highlights') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td class="font-bold">{{ t('home.services.table.sora.name') }}</td>
                  <td>{{ t('home.services.table.sora.features') }}</td>
                  <td>{{ t('home.services.table.sora.duration') }}</td>
                  <td>{{ t('home.services.table.sora.resolution') }}</td>
                  <td><span class="cost-badge">{{ t('home.services.table.sora.cost') }}</span></td>
                  <td>{{ t('home.services.table.sora.eta') }}</td>
                  <td class="text-muted">{{ t('home.services.table.sora.highlights') }}</td>
                </tr>
                <tr>
                  <td class="font-bold highlight-model">{{ t('home.services.table.sora2Pro.name') }}</td>
                  <td>{{ t('home.services.table.sora2Pro.features') }}</td>
                  <td>{{ t('home.services.table.sora2Pro.duration') }}</td>
                  <td>{{ t('home.services.table.sora2Pro.resolution') }}</td>
                  <td><span class="cost-badge highlight">{{ t('home.services.table.sora2Pro.cost') }}</span></td>
                  <td>{{ t('home.services.table.sora2Pro.eta') }}</td>
                  <td class="text-muted">{{ t('home.services.table.sora2Pro.highlights') }}</td>
                </tr>
                <tr>
                  <td class="font-bold">{{ t('home.services.table.assistant.name') }}</td>
                  <td>{{ t('home.services.table.assistant.features') }}</td>
                  <td>{{ t('home.services.table.assistant.duration') }}</td>
                  <td>{{ t('home.services.table.assistant.resolution') }}</td>
                  <td><span class="cost-badge">{{ t('home.services.table.assistant.cost') }}</span></td>
                  <td>{{ t('home.services.table.assistant.eta') }}</td>
                  <td class="text-muted">{{ t('home.services.table.assistant.highlights') }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="features-details glass-card">
          <h3 class="details-title">{{ t('home.services.details.title') }}</h3>
          <ul class="details-list">
            <li>
              <span class="list-dot"></span>
              {{ t('home.services.details.videoGen') }}
            </li>
            <li>
              <span class="list-dot highlight"></span>
              {{ t('home.services.details.syncAudio') }}
            </li>
          </ul>
        </div>
      </section>

       <footer class="footer">
          <div class="footer-content">
            <p class="slogan">{{ t('footer.slogan') }}</p>
            
            <div class="contact-section">
              <el-popover
                placement="top"
                :width="300"
                trigger="click"
              >
                <template #reference>
                  <span class="contact-trigger">{{ t('contact.title') }}</span>
                </template>
                <div class="contact-popover">
                  <p style="margin: 5px 0; color: #606266;">{{ t('contact.wechat') }}</p>
                  <p style="margin: 5px 0; color: #606266;">{{ t('contact.email') }}</p>
                </div>
              </el-popover>
            </div>

            <div class="beian-link">
              <a href="https://beian.miit.gov.cn/" target="_blank" rel="noopener noreferrer">
                {{ t('footer.beian') }}
              </a>
            </div>
          </div>
       </footer>
    </div>
  </div>
</template>

<style scoped>
.home-page {
  min-height: 100vh;
  background-color: var(--color-background);
  color: var(--color-text-main);
  font-family: var(--font-body);
  overflow-x: hidden;
  position: relative;
}

/* Navbar */
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  padding: 1.25rem 4rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  z-index: 100;
  transition: all 0.3s ease;
  box-sizing: border-box;
}

.glass-nav {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--color-border);
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 1.5rem;
  font-weight: 800;
  font-family: var(--font-heading);
  color: var(--color-primary);
  cursor: pointer;
}

.logo-icon {
  color: var(--color-primary);
  filter: drop-shadow(0 0 8px var(--color-primary-glow));
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

/* Removed Ambient Lights */

/* Hero Section */
.hero-section {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 90vh;
  padding: 2rem;
  text-align: center;
}

.scroll-container {
  position: relative;
  z-index: 1;
}

.hero-content {
  max-width: 1000px;
}

.badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: white;
  border: 1px solid var(--color-border);
  border-radius: 100px;
  font-size: 0.875rem;
  font-weight: 600;
  margin-bottom: 2rem;
  color: var(--color-text-secondary);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
}

.text-primary { color: var(--color-primary); }

.main-title {
  font-size: clamp(2.5rem, 8vw, 4.5rem);
  font-weight: 800;
  line-height: 1.1;
  margin-bottom: 2rem;
  letter-spacing: -0.02em;
  color: var(--primary-100);
}

.hero-subtitle {
  font-size: 1.5rem;
  color: var(--color-text-secondary);
  margin-bottom: 3.5rem;
  font-weight: 400;
}

/* Content Grid */
.content-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
  gap: 2.5rem;
  max-width: 1200px;
  margin: 0 auto 8rem;
  padding: 0 2.5rem;
}

.info-card {
  padding: 3.5rem;
}

.card-icon-wrapper {
  width: 64px;
  height: 64px;
  background: var(--primary-300);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1.5rem;
  color: var(--primary-100);
}

.card-icon {
  color: var(--color-primary);
}

.info-card h2 {
  font-size: 1.75rem;
  margin-bottom: 1.25rem;
}

.info-card p {
  color: var(--color-text-secondary);
  font-size: 1.1rem;
}

/* Buttons */
.btn-lg {
  padding: 1.125rem 3rem;
  font-size: 1.125rem;
}

/* Footer */
.footer {
  padding: 4rem 2rem;
  background: var(--color-surface);
  text-align: center;
  border-top: 1px solid var(--color-border);
}

.footer-content {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 2rem;
  flex-wrap: wrap;
}

.slogan {
  color: var(--color-text-main);
  font-size: 1rem;
  font-weight: 600;
  margin: 0;
  font-family: var(--font-heading);
}

.contact-trigger {
  cursor: pointer;
  color: var(--color-text-muted);
  font-size: 0.95rem;
  transition: color 0.2s;
}

.contact-trigger:hover {
  color: var(--color-primary);
}

.contact-section {
  display: flex;
  align-items: center;
}

.beian-link a {
  color: var(--color-text-muted);
  font-size: 0.85rem;
  text-decoration: none;
  transition: color 0.2s;
}

.beian-link a:hover {
  color: var(--color-primary);
}

/* Services Overview */
.services-overview {
  max-width: 1200px;
  margin: 0 auto 8rem;
  padding: 0 2.5rem;
}

.section-header {
  text-align: center;
  margin-bottom: 3rem;
}

.section-title {
  font-size: 2.5rem;
  font-weight: 800;
  margin-bottom: 1rem;
  color: var(--primary-100);
}

.section-subtitle {
  font-size: 1.2rem;
  color: var(--color-text-secondary);
  max-width: 800px;
  margin: 0 auto;
}

.table-container {
  padding: 1px;
  overflow: hidden;
}

.responsive-table {
  overflow-x: auto;
}

.custom-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  font-size: 0.95rem;
}

.custom-table th {
  padding: 1.25rem 1rem;
  background: rgba(var(--color-primary-rgb), 0.05);
  color: var(--color-text-main);
  font-weight: 700;
  border-bottom: 1px solid var(--color-border);
  white-space: nowrap;
}

.custom-table td {
  padding: 1.25rem 1rem;
  color: var(--color-text-secondary);
  border-bottom: 1px solid var(--color-border);
}

.custom-table tr:last-child td {
  border-bottom: none;
}

.font-bold {
  font-weight: 700;
  color: var(--color-text-main);
}

.highlight-model {
  color: var(--color-primary);
}

.cost-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 6px;
  font-weight: 600;
}

.cost-badge.highlight {
  background: rgba(var(--color-primary-rgb), 0.1);
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.text-muted {
  font-size: 0.85rem;
  opacity: 0.8;
}

.features-details {
  padding: 2.5rem;
}

.details-title {
  font-size: 1.5rem;
  margin-bottom: 1.5rem;
  color: var(--color-text-main);
}

.details-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.details-list li {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  color: var(--color-text-secondary);
  line-height: 1.6;
}

.list-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-text-muted);
  margin-top: 0.6rem;
  flex-shrink: 0;
}

.list-dot.highlight {
  background: var(--color-primary);
  box-shadow: 0 0 8px var(--color-primary-glow);
}

/* Responsive */
@media (max-width: 1024px) {
  .main-title { font-size: 4rem; }
  .navbar { padding: 1.25rem 2rem; }
  .section-title { font-size: 2rem; }
}

@media (max-width: 768px) {
  .main-title { font-size: 3rem; }
  .hero-subtitle { font-size: 1.25rem; }
  .navbar { padding: 1rem; }
  .info-card { padding: 2.5rem; }
  .services-overview { padding: 0 1.5rem; }
  .section-title { font-size: 1.75rem; }
  .custom-table { font-size: 0.85rem; }
  .custom-table th, .custom-table td { padding: 1rem 0.75rem; }
}
</style>
