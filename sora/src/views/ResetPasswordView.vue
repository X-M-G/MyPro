<template>
  <div class="login-page">
    <!-- Reset Form Container -->

    <div class="top-nav animate-fade-in">
      <LanguageSwitcher />
    </div>

    <div class="container">
      <div class="glass-card login-card animate-fade-up">
        <div class="card-header">
          <h1 class="title">{{ t('auth.resetPassword.title') }}</h1>
          <p class="subtitle">{{ t('auth.resetPassword.subtitle') || 'Enter your details to reset your password' }}</p>
        </div>
        
        <form @submit.prevent="handleSubmit" class="auth-form">
          <div class="form-group">
            <label class="label">{{ t('auth.resetPassword.phone') }}</label>
            <input 
              v-model="phone" 
              type="tel" 
              class="input modern-input" 
              :placeholder="t('auth.resetPassword.phonePlaceholder')" 
              required 
            />
          </div>

          <div class="form-group">
            <label class="label">{{ t('auth.login.captcha') }}</label>
            <div class="captcha-row">
              <input 
                v-model="captchaValue" 
                type="text" 
                class="input modern-input" 
                :placeholder="t('auth.login.captchaPlaceholder')" 
                required 
              />
              <div class="captcha-box" @click="refreshCaptcha">
                <img :src="captchaImage" alt="captcha" class="captcha-img" />
                <div class="captcha-overlay">
                  <RefreshCw :size="16" />
                </div>
              </div>
            </div>
          </div>

          <div class="form-group">
            <label class="label">{{ t('auth.resetPassword.smsCode') }}</label>
            <div class="sms-row">
              <input 
                v-model="smsCode" 
                type="text" 
                class="input modern-input" 
                :placeholder="t('auth.resetPassword.smsCodePlaceholder')" 
                required 
              />
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

          <div class="form-group">
            <label class="label">{{ t('auth.resetPassword.newPassword') }}</label>
            <input 
              v-model="newPassword" 
              type="password" 
              class="input modern-input" 
              :placeholder="t('auth.resetPassword.newPasswordPlaceholder')" 
              required 
            />
          </div>

          <div class="form-group">
            <label class="label">{{ t('auth.register.confirmPassword') }}</label>
            <input 
              v-model="confirmPassword" 
              type="password" 
              class="input modern-input" 
              :placeholder="t('auth.register.confirmPasswordPlaceholder')" 
              required 
            />
          </div>

          <div v-if="errorMsg" class="error-notice animate-shake">
            <AlertCircle :size="16" />
            <span>{{ errorMsg }}</span>
          </div>

          <button type="submit" class="btn btn-primary full-width btn-shine-parent">
            <span>{{ t('auth.resetPassword.reset') }}</span>
            <div class="btn-shine"></div>
          </button>
          
          <div class="footer-links">
            <router-link to="/login" class="back-link">
              <ArrowLeft :size="16" />
              <span>{{ t('auth.register.signInLink') }}</span>
            </router-link>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import api from '@/utils/api'
import LanguageSwitcher from '@/components/LanguageSwitcher.vue'
import { toast } from '@/utils/toast'
import { AlertCircle, RefreshCw, ArrowLeft } from 'lucide-vue-next'

const phone = ref('')
const smsCode = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const captchaValue = ref('')
const captchaKey = ref('')
const captchaImage = ref('')
const timer = ref(0)
const errorMsg = ref('')

const authStore = useAuthStore()
const { t } = useI18n()
const router = useRouter()

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
    errorMsg.value = t('auth.resetPassword.phonePlaceholder')
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
      scene: 'reset_pwd',
      captcha_key: captchaKey.value,
      captcha_value: captchaValue.value
    })
    
    timer.value = 60
    const interval = setInterval(() => {
      timer.value--
      if (timer.value <= 0) clearInterval(interval)
    }, 1000)
    errorMsg.value = ''
    toast.success(t('auth.login.smsSent'))
  } catch (err: any) {
    const errorKey = err.response?.data?.error || 'ERROR_SMS_SERVICE_UNAVAILABLE'
    errorMsg.value = t(`errors.${errorKey}`) !== `errors.${errorKey}` ? t(`errors.${errorKey}`) : errorKey
    refreshCaptcha()
  } finally {
    isSendingSms.value = false
  }
}

async function handleSubmit() {
  if (!phone.value || !smsCode.value || !newPassword.value || !confirmPassword.value) return
  
  if (newPassword.value !== confirmPassword.value) {
    errorMsg.value = t('errors.ERROR_PASSWORD_MISMATCH')
    return
  }

  try {
    await api.post('/auth/reset-password/', {
      phone: phone.value,
      sms_code: smsCode.value,
      new_password: newPassword.value
    })
    toast.success(t('auth.resetPassword.success'))
    router.push('/login')
  } catch (err: any) {
    const errorKey = err.response?.data?.error || 'Reset failed'
    errorMsg.value = t(`errors.${errorKey}`) !== `errors.${errorKey}` ? t(`errors.${errorKey}`) : errorKey
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-background);
  position: relative;
  overflow: hidden;
}

/* Removed ambient light logic */

.container {
  position: relative;
  z-index: 1;
  width: 100%;
  padding: 1.5rem;
  display: flex;
  justify-content: center;
}

.login-card {
  max-width: 480px;
  width: 100%;
  padding: 3rem;
}

.card-header {
  text-align: center;
  margin-bottom: 2.5rem;
}

.title {
  font-size: 2rem;
  margin-bottom: 0.75rem;
  color: #fff;
}

.subtitle {
  color: var(--color-text-secondary);
  font-size: 0.95rem;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.label {
  display: block;
  font-size: 0.875rem;
  font-weight: 700;
  color: var(--color-text-main);
  margin-bottom: 0.75rem;
}

.captcha-row, .sms-row {
  display: flex;
  gap: 0.75rem;
  background: var(--bg-100);
}

.captcha-box {
  position: relative;
  height: 48px;
  min-width: 120px;
  border-radius: var(--radius-md);
  overflow: hidden;
  cursor: pointer;
  background: white;
}

.captcha-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}



.captcha-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s;
  color: white;
}

.captcha-box:hover .captcha-overlay {
  opacity: 1;
}

.send-btn {
  white-space: nowrap;
  min-width: 120px;
}

.error-notice {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  background: rgba(220, 53, 69, 0.08);
  border: 1px solid rgba(220, 53, 69, 0.2);
  border-radius: var(--radius-md);
  color: #dc3545;
  font-size: 0.875rem;
}

.full-width {
  width: 100%;
  height: 3.5rem;
  font-size: 1.125rem;
}

.footer-links {
  margin-top: 1.5rem;
  text-align: center;
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--color-text-secondary);
  font-weight: 600;
  font-size: 0.875rem;
  transition: color 0.2s;
}

.back-link:hover {
  color: var(--color-primary);
}

.animate-fade-in { animation: fadeIn 0.8s ease-out; }
.animate-fade-up { animation: fadeUp 0.8s ease-out forwards; }

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px); }
  75% { transform: translateX(5px); }
}

.animate-shake { animation: shake 0.3s ease-in-out; }

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

