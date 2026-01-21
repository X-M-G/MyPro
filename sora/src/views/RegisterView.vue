<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import api from '@/utils/api'
import LanguageSwitcher from '@/components/LanguageSwitcher.vue'

const username = ref('')
const password = ref('')
const confirmPassword = ref('')
const phone = ref('')
const smsCode = ref('')
const inviteCode = ref('')
const captchaValue = ref('')
const captchaKey = ref('')
const captchaImage = ref('')

const timer = ref(0)
const authStore = useAuthStore()
const errorMsg = ref('')
const { t } = useI18n()
const route = useRoute()
const router = useRouter()

onMounted(() => {
  // Auto-fill invite code from URL if present
  if (route.query.invite) {
    inviteCode.value = route.query.invite as string
  }
  refreshCaptcha()
})

async function refreshCaptcha() {
  try {
    const res = await api.get('/auth/captcha-refresh/')
    captchaKey.value = res.data.key
    captchaImage.value = res.data.image_url
    captchaValue.value = ''
  } catch (err) {
    console.error('Failed to refresh captcha', err)
  }
}

  const isSendingSms = ref(false)

  async function handleSendSms() {
    if (!phone.value) {
      errorMsg.value = t('common.error') + ': ' + t('auth.register.phonePlaceholder')
      return
    }
    if (!captchaValue.value) {
      errorMsg.value = t('auth.register.captchaPlaceholder')
      return
    }

    try {
      isSendingSms.value = true
      await api.post('/auth/send-sms/', {
        phone: phone.value,
        scene: 'register',
        captcha_key: captchaKey.value,
        captcha_value: captchaValue.value
      })
      
      timer.value = 60
      const interval = setInterval(() => {
        timer.value--
        if (timer.value <= 0) clearInterval(interval)
      }, 1000)
      errorMsg.value = ''
    } catch (err: any) {
      const errorKey = err.response?.data?.error || 'ERROR_SMS_SERVICE_UNAVAILABLE'
      errorMsg.value = t(`errors.${errorKey}`) !== `errors.${errorKey}` ? t(`errors.${errorKey}`) : errorKey
      refreshCaptcha()
    } finally {
      isSendingSms.value = false
    }
  }

  async function handleSubmit() {
    errorMsg.value = ''
    if (!username.value || !password.value || !phone.value || !smsCode.value) {
      errorMsg.value = t('auth.register.errorFillAll')
      return
    }
    
    if (password.value !== confirmPassword.value) {
        errorMsg.value = t('auth.register.errorPasswordMismatch')
        return
    }
    
    try {
      const success = await authStore.register({
        username: username.value,
        password: password.value,
        phone: phone.value,
        sms_code: smsCode.value,
        invite_code: inviteCode.value
      })
      if (success) {
        // Updated: Redirect to Login instead of Dashboard
        router.push('/login')
      } else {
        const errorKey = authStore.error || 'Registration failed'
        errorMsg.value = t(`errors.${errorKey}`) !== `errors.${errorKey}` ? t(`errors.${errorKey}`) : errorKey
      }
    } catch (err: any) {
      const errorKey = err.response?.data?.error || 'Registration failed'
      errorMsg.value = t(`errors.${errorKey}`) !== `errors.${errorKey}` ? t(`errors.${errorKey}`) : errorKey
    }
  }
</script>

<template>
  <div class="login-page">
    <div class="ambient-bg">
      <div class="ambient-light ambient-light-1"></div>
      <div class="ambient-light ambient-light-2"></div>
      <div class="ambient-light ambient-light-3"></div>
    </div>
    <div class="top-nav">
      <LanguageSwitcher />
    </div>
    <div class="register-container animate-fade-up">
      <div class="glass-card login-card">
        <h1 class="title">{{ t('auth.register.title') }}</h1>
        <p class="subtitle">{{ t('auth.register.subtitle') }}</p>
        
        <form @submit.prevent="handleSubmit">
          <div class="form-group">
            <label class="label">{{ t('auth.register.username') }}</label>
            <input v-model="username" type="text" class="input" :placeholder="t('auth.register.usernamePlaceholder')" autocomplete="username" required />
          </div>

          <div class="form-group">
            <label class="label">{{ t('auth.register.phone') }}</label>
            <input v-model="phone" type="tel" class="input" :placeholder="t('auth.register.phonePlaceholder')" autocomplete="tel" required />
          </div>

          <div class="form-group">
            <label class="label">{{ t('auth.register.captcha') }}</label>
            <div class="captcha-wrapper">
              <input v-model="captchaValue" type="text" class="input" :placeholder="t('auth.register.captchaPlaceholder')" required />
              <img :src="captchaImage" alt="captcha" class="captcha-img" @click="refreshCaptcha" />
            </div>
          </div>

          <div class="form-group">
            <label class="label">{{ t('auth.register.smsCode') }}</label>
            <div class="sms-wrapper">
              <input v-model="smsCode" type="text" class="input" :placeholder="t('auth.register.smsCodePlaceholder')" required />
              <button 
                type="button" 
                class="btn btn-secondary send-btn" 
                :disabled="timer > 0 || isSendingSms" 
                @click="handleSendSms"
              >
                 <span v-if="isSendingSms" class="spinner-sm"></span>
                 <span v-else>{{ timer > 0 ? t('auth.register.sendSmsWait', { s: timer }) : t('auth.register.sendSms') }}</span>
              </button>
            </div>
          </div>
          
          <div class="form-group">
            <label class="label">{{ t('auth.register.password') }}</label>
            <input v-model="password" type="password" class="input" :placeholder="t('auth.register.passwordPlaceholder')" autocomplete="new-password" required />
          </div>

          <div class="form-group">
            <label class="label">{{ t('auth.register.confirmPassword') }}</label>
            <input v-model="confirmPassword" type="password" class="input" :placeholder="t('auth.register.confirmPasswordPlaceholder')" autocomplete="new-password" required />
          </div>

          <div class="form-group">
            <label class="label">{{ t('auth.register.inviteCode') }}</label>
            <input v-model="inviteCode" type="text" class="input" :placeholder="t('auth.register.inviteCodePlaceholder')" />
          </div>

          <div v-if="errorMsg" class="error-msg">
            {{ errorMsg }}
          </div>

          <button type="submit" class="btn btn-primary full-width" :disabled="authStore.loading">
            {{ authStore.loading ? t('auth.register.creatingAccount') : t('auth.register.signUp') }}
            <div class="btn-shine"></div>
          </button>
          
          <div class="auth-footer">
            <div class="divider">
              <span>{{ t('auth.register.alreadyHaveAccount').replace('?', '') }}</span>
            </div>
            <router-link to="/login" class="btn btn-outline full-width mt-4">
              {{ t('auth.register.signInLink') }}
            </router-link>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Base Layout */
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--color-background);
  overflow: hidden;
  position: relative;
  font-family: var(--font-body);
}

.top-nav {
  position: absolute;
  top: 2rem;
  right: 2rem;
  z-index: 100;
}

/* Auth Card */
.register-container {
  position: relative;
  z-index: 10;
  padding: 2.5rem 20px;
  width: 100%;
  display: flex;
  justify-content: center;
}

.login-card {
  max-width: 480px;
  width: 100%;
  padding: 3.5rem;
}

.title {
  text-align: center;
  font-size: 2.5rem;
  margin-bottom: 0.75rem;
  font-weight: 800;
}

.subtitle {
  text-align: center;
  color: var(--color-text-secondary);
  margin-bottom: 2.5rem;
  font-size: 1rem;
}

/* Form Styles */
.form-group {
  margin-bottom: 1.5rem;
}

.sms-wrapper, .captcha-wrapper {
  display: flex;
  gap: 0.875rem;
}

.send-btn {
  white-space: nowrap;
  min-width: 130px;
}

.captcha-img {
  height: 52px;
  border-radius: var(--radius-md);
  cursor: pointer;
  background: #fff;
  border: 1px solid var(--color-border);
}

.error-msg {
  background: rgba(220, 53, 69, 0.08);
  border: 1px solid rgba(220, 53, 69, 0.2);
  color: #dc3545;
  padding: 12px 16px;
  border-radius: var(--radius-md);
  font-size: 0.9rem;
  margin-top: 1rem;
  text-align: center;
}

.full-width {
  width: 100%;
  margin-top: 1.5rem;
}

/* Footer Links */
.auth-footer {
  margin-top: 2.5rem;
  text-align: center;
}

.divider {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  color: var(--color-text-muted);
  font-size: 0.875rem;
  margin-bottom: 1rem;
}

.divider::before, .divider::after {
  content: "";
  flex: 1;
  height: 1px;
  background: var(--color-border);
}

.mt-3 { margin-top: 1rem; }

:deep(.language-switcher .current-lang) {
  background: white;
  border-color: var(--color-border);
  color: var(--color-text-main);
}


.spinner-sm {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(0, 0, 0, 0.1);
  border-top-color: var(--color-text-main);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  display: inline-block;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
