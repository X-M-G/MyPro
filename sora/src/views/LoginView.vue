<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import api from '@/utils/api'
import LanguageSwitcher from '@/components/LanguageSwitcher.vue'

const loginType = ref('password') // 'password' or 'sms'
const username = ref('')
const password = ref('')
const phone = ref('')
const smsCode = ref('')
const captchaValue = ref('')
const captchaKey = ref('')
const captchaImage = ref('')
const timer = ref(0)
const errorMsg = ref('')

const authStore = useAuthStore()
const router = useRouter()
const { t } = useI18n()

onMounted(() => {
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
      errorMsg.value = t('auth.login.phonePlaceholder')
      return
    }
    if (!captchaValue.value) {
      errorMsg.value = t('auth.login.captchaPlaceholder')
      return
    }

    try {
      isSendingSms.value = true
      await api.post('/auth/send-sms/', {
        phone: phone.value,
        scene: 'login',
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
  let params: any = { login_type: loginType.value }
  
  if (loginType.value === 'password') {
    if (!username.value || !password.value) return
    params.username = username.value
    params.password = password.value
  } else {
    if (!phone.value || !smsCode.value) return
    params.phone = phone.value
    params.sms_code = smsCode.value
  }

  const success = await authStore.login(params)
  if (success) {
    router.push('/dashboard')
  } else {
    const errorKey = authStore.error || 'Login failed'
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
    <div class="login-container animate-fade-up">
      <div class="glass-card login-card">
        <div class="header">
          <h1 class="title">{{ t('auth.login.title') }}</h1>
          <p class="subtitle">{{ t('auth.login.subtitle') }} <span class="highlight">{{ t('auth.login.subtitleHighlight') }}</span></p>
        </div>

        <div class="login-tabs">
          <button 
            type="button" 
            class="tab-btn" 
            :class="{ active: loginType === 'password' }"
            @click="loginType = 'password'"
          >
            {{ t('auth.login.loginWithPassword') }}
          </button>
          <button 
            type="button" 
            class="tab-btn" 
            :class="{ active: loginType === 'sms' }"
            @click="loginType = 'sms'"
          >
            {{ t('auth.login.loginWithSms') }}
          </button>
        </div>
        
        <form @submit.prevent="handleSubmit" class="login-form">
          <template v-if="loginType === 'password'">
            <div class="form-group">
              <label class="label">{{ t('auth.login.username') }}</label>
              <div class="input-wrapper">
                <input 
                  v-model="username" 
                  type="text" 
                  class="input" 
                  :placeholder="t('auth.login.usernamePlaceholder')" 
                  autocomplete="username"
                  required 
                />
              </div>
            </div>
            
            <div class="form-group">
              <label class="label">{{ t('auth.login.password') }}</label>
              <div class="input-wrapper">
                <input 
                  v-model="password" 
                  type="password" 
                  class="input" 
                  :placeholder="t('auth.login.passwordPlaceholder')" 
                  autocomplete="current-password"
                  required 
                />
              </div>
            </div>
          </template>

          <template v-else>
            <div class="form-group">
              <label class="label">{{ t('auth.login.phone') }}</label>
              <div class="input-wrapper">
                <input 
                  v-model="phone" 
                  type="tel" 
                  class="input" 
                  :placeholder="t('auth.login.phonePlaceholder')" 
                  required 
                />
                <div class="input-glow"></div>
              </div>
            </div>

            <div class="form-group">
              <label class="label">{{ t('auth.login.captcha') }}</label>
              <div class="captcha-wrapper">
                <div class="input-wrapper">
                  <input v-model="captchaValue" type="text" class="input" :placeholder="t('auth.login.captchaPlaceholder')" required />
                  <div class="input-glow"></div>
                </div>
                <img :src="captchaImage" alt="captcha" class="captcha-img" @click="refreshCaptcha" />
              </div>
            </div>

            <div class="form-group">
              <label class="label">{{ t('auth.login.smsCode') }}</label>
              <div class="sms-wrapper">
                <div class="input-wrapper">
                  <input v-model="smsCode" type="text" class="input" :placeholder="t('auth.login.smsCodePlaceholder')" required />
                  <div class="input-glow"></div>
                </div>
                <button 
                  type="button" 
                  class="btn btn-secondary send-btn" 
                  :disabled="timer > 0 || isSendingSms" 
                  @click="handleSendSms"
                >
                   <span v-if="isSendingSms" class="spinner-sm"></span>
                   <span v-else>{{ timer > 0 ? t('auth.login.sendSmsWait', { s: timer }) : t('auth.login.sendSms') }}</span>
                </button>
              </div>
            </div>
          </template>

          <div v-if="errorMsg" class="error-msg">
            <span class="icon">⚠️</span> {{ errorMsg }}
          </div>

          <button type="submit" class="btn btn-primary full-width" :disabled="authStore.loading">
            <span class="btn-text">{{ authStore.loading ? t('auth.login.signingIn') : t('auth.login.signIn') }}</span>
            <div class="btn-shine"></div>
          </button>
          
          <div class="auth-footer">
             <div class="divider">
               <span>{{ t('auth.register.alreadyHaveAccount').replace('?', '') }}</span>
             </div>
             <router-link to="/register" class="btn btn-outline full-width mt-3">
                {{ t('auth.register.signUp') }}
             </router-link>
             <div class="secondary-links mt-4">
               <router-link to="/reset-password" class="forgot-link">
                 {{ t('auth.login.forgotPassword') }}
               </router-link>
             </div>
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
.login-container {
  position: relative;
  z-index: 10;
  padding: 2.5rem 20px;
  width: 100%;
  display: flex;
  justify-content: center;
}

.login-card {
  max-width: 460px;
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
  margin-bottom: 3rem;
  font-size: 1rem;
}

.highlight {
  color: var(--color-primary-hover);
  font-weight: 600;
}

/* Tabs */
.login-tabs {
  display: flex;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 4px;
  margin-bottom: 2.5rem;
}

.tab-btn {
  flex: 1;
  padding: 12px;
  background: transparent;
  border: none;
  color: var(--color-text-muted);
  font-weight: 600;
  cursor: pointer;
  border-radius: 10px;
  transition: all 0.3s ease;
  font-family: var(--font-heading);
}

.tab-btn.active {
  background: var(--primary-100);
  color: #fff;
  box-shadow: 0 4px 12px rgba(0, 119, 194, 0.2);
}

/* Form Styles */
.form-group {
  margin-bottom: 1.75rem;
}

.input-wrapper {
  position: relative;
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
  margin-top: 1.5rem;
  display: flex;
  align-items: center;
  gap: 10px;
  animation: shake 0.5s cubic-bezier(.36,.07,.19,.97) both;
}

@keyframes shake {
  10%, 90% { transform: translate3d(-1px, 0, 0); }
  20%, 80% { transform: translate3d(2px, 0, 0); }
  30%, 50%, 70% { transform: translate3d(-4px, 0, 0); }
  40%, 60% { transform: translate3d(4px, 0, 0); }
}

.full-width {
  width: 100%;
  margin-top: 1.5rem;
  padding: 1rem;
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
.mt-4 { margin-top: 1.25rem; }

.secondary-links {
  display: flex;
  justify-content: center;
}

.forgot-link {
  color: var(--color-text-muted);
  font-size: 0.875rem;
  text-decoration: none;
  transition: all 0.2s;
}

.forgot-link:hover {
  color: var(--color-primary-hover);
}

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