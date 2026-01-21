<template>
  <div class="admin-login-view">
    <!-- Mesh Background Overlay -->
    <div class="background-mesh"></div>
    
    <div class="login-wrapper animate-slide-up">
      <!-- Brand Logo Area -->
      <div class="brand-section">
        <div class="logo-outer">
          <div class="logo-inner">S</div>
        </div>
        <h1 class="brand-name">{{ $t('admin.systemName') }}</h1>
      </div>

      <!-- Login Card -->
      <div class="login-card glass-card">
        <div class="card-header">
          <h2 class="title">{{ $t('admin.gatekeeperTitle') }}</h2>
          <p class="subtitle">{{ $t('admin.gatekeeperSubtitle') }}</p>
        </div>

        <el-form ref="loginFormRef" :model="loginForm" :rules="loginRules" class="executive-form">
          <el-form-item prop="username">
            <div class="input-label">{{ $t('auth.login.username') }}</div>
            <el-input 
              v-model="loginForm.username" 
              :placeholder="$t('admin.usernamePlaceholder')"
              class="premium-input"
              tabindex="1"
            >
              <template #prefix><el-icon><User /></el-icon></template>
            </el-input>
          </el-form-item>

          <el-form-item prop="password">
            <div class="input-label">{{ $t('auth.login.password') }}</div>
            <el-input 
              v-model="loginForm.password" 
              :placeholder="$t('admin.passwordPlaceholder')"
              :type="passwordType"
              class="premium-input"
              tabindex="2"
              @keyup.enter="handleLogin"
            >
              <template #prefix><el-icon><Lock /></el-icon></template>
              <template #suffix>
                <span class="show-pwd" @click="showPwd">
                  <el-icon><View v-if="passwordType === 'text'" /><Hide v-else /></el-icon>
                </span>
              </template>
            </el-input>
          </el-form-item>

          <button 
            class="submit-btn" 
            :disabled="loading" 
            @click.prevent="handleLogin"
          >
            <span v-if="!loading">{{ $t('auth.login.submit') }}</span>
            <el-icon v-else class="is-loading"><Loading /></el-icon>
          </button>
        </el-form>
      </div>

      <div class="footer-copyright">
        {{ $t('admin.copyright') }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { User, Lock, View, Hide, Loading } from '@element-plus/icons-vue'

const { locale, t } = useI18n()

onMounted(() => {
  // Force admin login to Chinese
  locale.value = 'zh'
})
const loginForm = reactive({
  username: '',
  password: ''
})

const loginRules = {
  username: [{ required: true, trigger: 'blur', message: t('auth.login.hint') }],
  password: [{ required: true, trigger: 'blur', message: t('auth.login.hint') }]
}

const passwordType = ref('password')
const loading = ref(false)
const showPwd = () => {
  passwordType.value = passwordType.value === 'password' ? 'text' : 'password'
}

const router = useRouter()
const authStore = useAuthStore()

const handleLogin = async () => {
  if (!loginForm.username || !loginForm.password) {
    ElMessage.warning(t('auth.login.hint'))
    return
  }

  loading.value = true
  try {
    const success = await authStore.login({
        username: loginForm.username,
        password: loginForm.password
    })
    
    if (success) {
        if (authStore.user && (authStore.user.is_staff || authStore.user.is_superuser)) {
            ElMessage.success(t('admin.loginSuccess'))
            router.push('/adym/dashboard')
        } else {
            ElMessage.error(t('common.error'))
            authStore.logout(false)
        }
    } else {
        ElMessage.error(authStore.error || t('auth.login.failed'))
    }
  } catch (error) {
    ElMessage.error(t('common.error'))
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.admin-login-view {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: var(--admin-sidebar-bg);
  position: relative;
  overflow: hidden;
  padding: 20px;
}

.background-mesh {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    radial-gradient(at 0% 0%, rgba(197, 160, 89, 0.05) 0px, transparent 50%),
    radial-gradient(at 100% 100%, rgba(42, 157, 143, 0.05) 0px, transparent 50%);
  opacity: 0.8;
  pointer-events: none;
}

.login-wrapper {
  width: 100%;
  max-width: 440px;
  display: flex;
  flex-direction: column;
  align-items: center;
  z-index: 10;
}

.brand-section {
  text-align: center;
  margin-bottom: 40px;
}

.logo-outer {
  width: 64px;
  height: 64px;
  background: var(--admin-accent-gold);
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
  box-shadow: 0 10px 25px -5px rgba(197, 160, 89, 0.4);
}

.logo-inner {
  color: white;
  font-size: 32px;
  font-weight: 900;
  font-family: var(--font-heading);
}

.brand-name {
  color: white;
  font-size: 1.5rem;
  font-weight: 800;
  letter-spacing: -0.02em;
}

.login-card {
  width: 100%;
  padding: 48px;
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 40px 100px -20px rgba(0, 0, 0, 0.25);
}

.card-header {
  margin-bottom: 32px;
  text-align: center;
}

.title {
  font-size: 1.6rem;
  font-weight: 800;
  color: var(--admin-text-primary);
  margin-bottom: 8px;
  letter-spacing: -0.03em;
}

.subtitle {
  color: var(--admin-text-secondary);
  font-size: 0.9rem;
  line-height: 1.5;
}

.executive-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.input-label {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--admin-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 8px;
}

:deep(.premium-input .el-input__wrapper) {
  background: white;
  border: 1.5px solid var(--admin-border);
  box-shadow: none !important;
  border-radius: 12px;
  height: 52px;
  transition: all 0.3s;
  padding: 0 16px;
}

:deep(.premium-input .el-input__wrapper.is-focus) {
  border-color: var(--admin-accent-gold);
  background: white;
}

:deep(.premium-input .el-input__inner) {
  font-weight: 600;
  color: var(--admin-text-primary);
}

:deep(.premium-input .el-icon) {
  font-size: 18px;
  color: var(--admin-text-secondary);
}

.show-pwd {
  cursor: pointer;
  color: var(--admin-text-secondary);
  transition: color 0.2s;
}

.show-pwd:hover {
  color: var(--admin-accent-gold);
}

.submit-btn {
  margin-top: 12px;
  height: 56px;
  background: var(--admin-sidebar-bg);
  color: white;
  border: none;
  border-radius: 14px;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.2, 0, 0, 1);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.1);
}

.submit-btn:hover {
  background: #1e293b;
  transform: translateY(-2px);
  box-shadow: 0 20px 30px -10px rgba(15, 23, 42, 0.3);
}

.submit-btn:active {
  transform: translateY(0);
}

.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.footer-copyright {
  margin-top: 40px;
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.4);
  font-weight: 500;
  letter-spacing: 0.02em;
}

.animate-slide-up {
  animation: slideUp 0.8s cubic-bezier(0.2, 0, 0, 1) forwards;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 480px) {
  .login-card {
    padding: 32px 24px;
  }
}
</style>
