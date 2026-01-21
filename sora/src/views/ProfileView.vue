<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { 
  Coins, 
  Share2, 
  Phone, 
  Copy, 
  User as UserIcon, 
  ShieldCheck, 
  ChevronRight,
  ExternalLink,
  X,
  RefreshCw,
  AlertCircle
} from 'lucide-vue-next'
import api from '@/utils/api'
import { toast } from '@/utils/toast'

const authStore = useAuthStore()
const { t } = useI18n()
const router = useRouter()
const loading = ref(false)

const showBindModal = ref(false)
const showInviteModal = ref(false)
const showRules = ref(false)
const showPasswordModal = ref(false)
const showUsernameModal = ref(false)
const newPhone = ref('')
const newUsername = ref('')
const smsCode = ref('')
const timer = ref(0)
const captchaValue = ref('')
const captchaKey = ref('')
const captchaImage = ref('')
const errorMsg = ref('')

// Password change refs
const passwordStep = ref(1) // 1: SMS verify, 2: Password change
const oldPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const passwordSmsCode = ref('')
const passwordError = ref('')
const passTimer = ref(0)

onMounted(async () => {
  refreshCaptcha()
})

const getInviteUrl = () => {
  return `${window.location.origin}/register?invite=${authStore.user?.invitation_code}`
}

const formatPhone = (phone: string | undefined) => {
  if (!phone) return '---'
  if (phone.length < 11) return phone
  // Display first 3 and last 4: 123****4567
  return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
}

const copyInviteLink = async () => {
  try {
    await navigator.clipboard.writeText(t('profile.invitationTemplate', { url: getInviteUrl(), code: authStore.user?.invitation_code }))
    toast.success(t('common.copied'))
  } catch (err) {
    console.error('Failed to copy', err)
  }
}

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

async function handleSendSms() {
  if (!newPhone.value) return
  if (!captchaValue.value) {
    errorMsg.value = t('auth.login.captchaPlaceholder')
    return
  }

  try {
    await api.post('/auth/send-sms/', {
      phone: newPhone.value,
      scene: authStore.user?.phone_number ? 'modify_phone' : 'bind_new',
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
  }
}

async function handleSendPasswordSms() {
  const phone = authStore.user?.phone_number
  if (!phone) {
    passwordError.value = t('profile.bindPhoneFirst')
    return
  }
  if (!captchaValue.value) {
    passwordError.value = t('auth.login.captchaPlaceholder')
    return
  }

  try {
    await api.post('/auth/send-sms/', {
      phone: phone,
      scene: 'change_password',
      captcha_key: captchaKey.value,
      captcha_value: captchaValue.value
    })
    
    passTimer.value = 60
    const interval = setInterval(() => {
      passTimer.value--
      if (passTimer.value <= 0) clearInterval(interval)
    }, 1000)
    passwordError.value = ''
    refreshCaptcha()
    toast.success(t('auth.login.smsSent'))
  } catch (err: any) {
    const errorKey = err.response?.data?.error || 'ERROR_SMS_SERVICE_UNAVAILABLE'
    passwordError.value = t(`errors.${errorKey}`) !== `errors.${errorKey}` ? t(`errors.${errorKey}`) : errorKey
    refreshCaptcha()
  }
}

async function handleBindPhone() {
  if (!newPhone.value || !smsCode.value) return
  try {
    await api.post('/auth/change-phone/', {
      new_phone: newPhone.value,
      sms_code: smsCode.value
    })
    await authStore.fetchUser()
    showBindModal.value = false
    toast.success(t('common.success'))
  } catch (err: any) {
    const errorKey = err.response?.data?.error || 'Binding failed'
    errorMsg.value = t(`errors.${errorKey}`) !== `errors.${errorKey}` ? t(`errors.${errorKey}`) : errorKey
  }
}

async function handleVerifyPasswordSms() {
  if (!passwordSmsCode.value) return
  try {
    await api.post('/auth/verify-password-sms/', {
      sms_code: passwordSmsCode.value
    })
    toast.success(t('common.success'))
    passwordStep.value = 2
    passwordError.value = ''
    refreshCaptcha()
  } catch (err: any) {
    const errorKey = err.response?.data?.error || 'Verification failed'
    passwordError.value = t(`errors.${errorKey}`) !== `errors.${errorKey}` ? t(`errors.${errorKey}`) : errorKey
  }
}

async function handleChangePassword() {
  if (!oldPassword.value || !newPassword.value || !confirmPassword.value) return
  if (newPassword.value !== confirmPassword.value) {
    passwordError.value = t('profile.passwordMismatch')
    return
  }

  try {
    await api.post('/auth/change-password/', {
      old_password: oldPassword.value,
      new_password: newPassword.value
    })
    showPasswordModal.value = false
    passwordStep.value = 1
    oldPassword.value = ''
    newPassword.value = ''
    confirmPassword.value = ''
    passwordSmsCode.value = ''
    passwordError.value = ''
    toast.success(t('common.success'))
    // Force logout after password change
    await authStore.logout()
  } catch (err: any) {
    const errorKey = err.response?.data?.error || 'Password change failed'
    passwordError.value = t(`errors.${errorKey}`) !== `errors.${errorKey}` ? t(`errors.${errorKey}`) : errorKey
  }
}

async function handleUpdateUsername() {
  if (!newUsername.value) return
  try {
    const res = await api.post('/auth/change-username/', {
      username: newUsername.value
    })
    await authStore.fetchUser()
    showUsernameModal.value = false
    newUsername.value = ''
    toast.success(t('common.success'))
  } catch (err: any) {
    const errorKey = err.response?.data?.error || 'Update failed'
    errorMsg.value = t(`errors.${errorKey}`) !== `errors.${errorKey}` ? t(`errors.${errorKey}`) : errorKey
  }
}

function goToCredits() {
  router.push('/credits')
}
</script>

<template>
  <div class="page-container profile-page">
    <!-- Profile Content Container -->

    <!-- Header Section -->
    <header class="profile-header animate-fade-in">
      <div class="profile-avatar-wrapper">
        <div class="profile-avatar-glow"></div>
        <div class="profile-avatar">
          <UserIcon v-if="!authStore.user?.username" :size="48" />
          <span v-else>{{ authStore.user?.username?.charAt(0).toUpperCase() }}</span>
        </div>
        <div class="online-indicator"></div>
      </div>
      <div class="header-info">
        <h1 class="welcome-title">{{ t('profile.title') }}</h1>
      </div>
    </header>

    <div class="profile-grid">
      <!-- High Impact Cards Area -->
      <div class="card-column">
        <!-- Credits/Wallet Card -->
        <!-- <div class="glass-card wallet-card animate-fade-up">
          <div class="wallet-glow"></div>
          <div class="wallet-content">
            <div class="wallet-header">
              <div class="icon-box">
                <Coins :size="24" class="text-white" />
              </div>
              <span class="wallet-label">{{ t('profile.currentBalance') }}</span>
            </div>
            <div class="credits-main">
              <span class="amount">{{ authStore.user?.credits || 0 }}</span>
              <span class="unit">Credits</span>
            </div>
            <button class="btn btn-primary btn-sm view-history" @click="goToCredits">
              {{ t('profile.viewTransactions') }}
              <ChevronRight :size="16" />
            </button>
          </div>
        </div> -->
        <div class="glass-card wallet-card animate-fade-up">
  <div class="wallet-decoration">
    <div class="circle-1"></div>
    <div class="circle-2"></div>
  </div>
  
  <div class="wallet-content">
    <div class="wallet-top">
      <div class="wallet-info">
        <div class="icon-glow-box">
          <Coins :size="20" class="text-white" />
        </div>
        <span class="wallet-label">{{ t('profile.currentBalance') }}</span>
      </div>
      <div class="balance-main">
        <span class="amount-integer">{{ authStore.user?.credits || 0 }}</span>
        <span class="amount-unit">Credits</span>
      </div>
      <div class="recharge-note">{{ t('profile.rechargeNote') }}</div>
    </div>
    <div class="wallet-bottom">
      <button class="action-link-btn" @click="goToCredits">
        <span>{{ t('profile.viewTransactions') }}</span>
        <div class="icon-circle">
          <ChevronRight :size="14" />
        </div>
      </button>
    </div>
  </div>
</div>
        <!-- Invitation / Earn Card -->
        <div class="glass-card invite-card animate-fade-up" style="animation-delay: 0.1s">
          <div class="invite-header">
            <div class="icon-box accent">
              <Share2 :size="24" class="text-white" />
            </div>
            <h2>{{ t('profile.invitationInfo') }}</h2>
          </div>
          <p class="invite-description">{{ t('profile.referralBonus') }}</p>
          
          <div class="invite-controls">
            <div class="code-display">
              <label>{{ t('profile.myInvitationCode') }}</label>
              <div class="code-box">
                <code>{{ authStore.user?.invitation_code || '---' }}</code>
              </div>
            </div>
            <button class="btn btn-ghost btn-md generate-btn" @click="showInviteModal = true">
              <ExternalLink :size="16" />
              {{ t('profile.generateInvitation') }}
            </button>
          </div>
          
          <!-- Rules Section -->
          <div class="rules-section">
            <button class="rules-toggle" @click="showRules = !showRules">
              <span>{{ t('profile.viewRules') }}</span>
              <ChevronRight :size="16" :class="{ 'rotate': showRules }" />
            </button>
            <transition name="slide-fade">
              <div v-if="showRules" class="rules-content">
                <h4 class="rules-title">{{ t('profile.referralRules.title') }}</h4>
                <ul class="rules-list">
                  <li>{{ t('profile.referralRules.rule1') }}</li>
                  <li>{{ t('profile.referralRules.rule2') }}</li>
                  <li>{{ t('profile.referralRules.rule3') }}</li>
                </ul>
              </div>
            </transition>
          </div>
        </div>
      </div>

      <!-- Settings / Security Section -->
      <div class="settings-column">
        <div class="settings-group animate-fade-up" style="animation-delay: 0.2s">
          <h3 class="group-title">{{ t('profile.securityStatus') }}</h3>
          <div class="settings-stack glass-card">
            <!-- Username Change Item -->
            <div class="settings-item" @click="showUsernameModal = true; newUsername = authStore.user?.username || ''">
              <div class="item-visual">
                <div class="icon-pill purple">
                  <UserIcon :size="20" />
                </div>
                <div class="item-text">
                  <span class="item-label">{{ t('profile.changeUsername') }}</span>
                  <span class="item-value">{{ authStore.user?.username }}</span>
                </div>
              </div>
              <div class="item-action">
                <ChevronRight :size="18" class="chevron" />
              </div>
            </div>

            <div class="item-divider"></div>

            <!-- Phone Binding Item -->
            <div class="settings-item" @click="showBindModal = true">
              <div class="item-visual">
                <div class="icon-pill blue">
                  <Phone :size="20" />
                </div>
                <div class="item-text">
                  <span class="item-label">{{ t('profile.phoneInfo') }}</span>
                  <span class="item-value">{{ formatPhone(authStore.user?.phone_number) }}</span>
                </div>
              </div>
              <div class="item-action">
                <span class="status-marker" :class="{ 'linked': authStore.user?.phone_number }">
                  {{ authStore.user?.phone_number ? t('profile.isBound') : t('profile.notBound') }}
                </span>
                <ChevronRight :size="18" class="chevron" />
              </div>
            </div>

            <div class="item-divider"></div>

            <!-- Change Password Item -->
            <div class="settings-item" @click="showPasswordModal = true; refreshCaptcha()">
              <div class="item-visual">
                <div class="icon-pill orange">
                  <ShieldCheck :size="20" />
                </div>
                <div class="item-text">
                  <span class="item-label">{{ t('profile.changePassword') }}</span>
                  <span class="item-value">{{ t('profile.passwordSecurityDesc') }}</span>
                </div>
              </div>
              <div class="item-action">
                <ChevronRight :size="18" class="chevron" />
              </div>
            </div>

            <div class="item-divider"></div>

            <!-- Account Security (Placeholder) -->
            <div class="settings-item disabled">
              <div class="item-visual">
                <div class="icon-pill green">
                  <ShieldCheck :size="20" />
                </div>
                <div class="item-text">
                  <span class="item-label">{{ t('profile.accountSecurity') }}</span>
                  <span class="item-value">{{ t('profile.accountSecurityDesc') }}</span>
                </div>
              </div>
              <div class="item-action">
                <span class="status-marker linked">{{ t('profile.securityNormal') }}</span>
                <ChevronRight :size="18" class="chevron" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modals -->
    <!-- Phone Bind Modal -->
    <transition name="fade">
      <div v-if="showBindModal" class="modal-overlay" @click.self="showBindModal = false">
        <div class="modal-container glass-card">
           <div class="modal-header">
             <h2>{{ authStore.user?.phone_number ? t('profile.changePhone') : t('profile.bindPhone') }}</h2>
             <button class="close-btn" @click="showBindModal = false"><X :size="20" /></button>
           </div>
           
           <div class="modal-body">
             <div class="form-group">
               <label class="label">{{ t('profile.phoneInfo') }}</label>
               <input v-model="newPhone" type="tel" class="input modern-input" :placeholder="t('profile.phoneInfo')" />
             </div>

             <div class="form-group">
               <label class="label">{{ t('auth.login.captcha') }}</label>
               <div class="captcha-row">
                 <input v-model="captchaValue" type="text" class="input modern-input" :placeholder="t('auth.login.captchaPlaceholder')" />
                 <div class="captcha-box" @click="refreshCaptcha">
                   <img :src="captchaImage" alt="captcha" class="captcha-img" />
                   <div class="captcha-overlay"><RefreshCw :size="16" /></div>
                 </div>
               </div>
             </div>

             <div class="form-group">
               <label class="label">{{ t('profile.smsCode') }}</label>
               <div class="sms-row">
                 <input v-model="smsCode" type="text" class="input modern-input" :placeholder="t('profile.smsCodePlaceholder')" />
                 <button class="btn btn-secondary send-btn" :disabled="timer > 0" @click="handleSendSms">
                    {{ timer > 0 ? t('auth.login.sendSmsWait', { s: timer }) : t('auth.login.sendSms') }}
                 </button>
               </div>
             </div>

             <div v-if="errorMsg" class="error-notice">
               <AlertCircle :size="16" />
               <span>{{ errorMsg }}</span>
             </div>
           </div>

           <div class="modal-footer">
             <button class="btn btn-ghost" @click="showBindModal = false">{{ t('common.cancel') }}</button>
             <button class="btn btn-primary" @click="handleBindPhone">{{ t('common.confirm') }}</button>
           </div>
        </div>
      </div>
    </transition>

    <!-- Invitation Modal -->
    <transition name="fade">
      <div v-if="showInviteModal" class="modal-overlay" @click.self="showInviteModal = false">
        <div class="modal-container glass-card">
           <div class="modal-header">
             <h2>{{ t('profile.generateInvitation') }}</h2>
             <button class="close-btn" @click="showInviteModal = false"><X :size="20" /></button>
           </div>
           
           <div class="modal-body">
             <div class="form-group">
                <label class="label">{{ t('profile.invitationMessage') }}</label>
                <div class="preview-box">
                  <textarea 
                    class="modern-textarea" 
                    rows="6" 
                    readonly 
                    :value="t('profile.invitationTemplate', { url: getInviteUrl(), code: authStore.user?.invitation_code })"
                  ></textarea>
                </div>
             </div>
           </div>

           <div class="modal-footer">
             <button class="btn btn-ghost" @click="showInviteModal = false">{{ t('common.cancel') }}</button>
             <button class="btn btn-primary" @click="copyInviteLink">
               <Copy :size="16" />
               {{ t('profile.copyInvitation') }}
             </button>
           </div>
        </div>
      </div>
    </transition>

    <!-- Password Change Modal -->
    <transition name="fade">
      <div v-if="showPasswordModal" class="modal-overlay" @click.self="showPasswordModal = false">
        <div class="modal-container glass-card">
           <div class="modal-header">
             <div class="header-with-steps">
               <h2>{{ t('profile.changePassword') }}</h2>
               <div class="step-nav">
                  <div class="step-dot" :class="{ 'active': passwordStep === 1 }"></div>
                  <div class="step-line"></div>
                  <div class="step-dot" :class="{ 'active': passwordStep === 2 }"></div>
               </div>
             </div>
             <button class="close-btn" @click="showPasswordModal = false"><X :size="20" /></button>
           </div>
           
           <div class="modal-body">
             <!-- Step 1: SMS Verify -->
             <div v-if="passwordStep === 1" class="step-content">
               <div class="form-group">
                 <label class="label">{{ t('profile.phoneInfo') }}</label>
                 <div class="phone-display">{{ formatPhone(authStore.user?.phone_number) }}</div>
               </div>

               <div class="form-group">
                 <label class="label">{{ t('auth.login.captcha') }}</label>
                 <div class="captcha-row">
                   <input v-model="captchaValue" type="text" class="input modern-input" :placeholder="t('auth.login.captchaPlaceholder')" />
                   <div class="captcha-box" @click="refreshCaptcha">
                     <img :src="captchaImage" alt="captcha" class="captcha-img" />
                     <div class="captcha-overlay"><RefreshCw :size="16" /></div>
                   </div>
                 </div>
               </div>

               <div class="form-group">
                 <label class="label">{{ t('profile.smsCode') }}</label>
                 <div class="sms-row">
                   <input v-model="passwordSmsCode" type="text" class="input modern-input" :placeholder="t('profile.smsCodePlaceholder')" />
                   <button class="btn btn-secondary send-btn" :disabled="passTimer > 0" @click="handleSendPasswordSms">
                      {{ passTimer > 0 ? t('auth.login.sendSmsWait', { s: passTimer }) : t('auth.login.sendSms') }}
                   </button>
                 </div>
               </div>
             </div>

             <!-- Step 2: Input Passwords -->
             <div v-if="passwordStep === 2" class="step-content">
               <div class="form-group">
                 <label class="label">{{ t('profile.oldPassword') }}</label>
                 <input v-model="oldPassword" type="password" class="input modern-input" :placeholder="t('profile.oldPasswordPlaceholder')" />
               </div>

               <div class="form-group">
                 <label class="label">{{ t('profile.newPassword') }}</label>
                 <input v-model="newPassword" type="password" class="input modern-input" :placeholder="t('profile.newPasswordPlaceholder')" />
               </div>

               <div class="form-group">
                 <label class="label">{{ t('profile.confirmNewPassword') }}</label>
                 <input v-model="confirmPassword" type="password" class="input modern-input" :placeholder="t('profile.confirmNewPasswordPlaceholder')" />
               </div>
             </div>

             <div v-if="passwordError" class="error-notice">
               <AlertCircle :size="16" />
               <span>{{ passwordError }}</span>
             </div>
           </div>

           <div class="modal-footer">
             <button v-if="passwordStep === 2" class="btn btn-ghost" @click="passwordStep = 1">{{ t('common.back') }}</button>
             <button v-else class="btn btn-ghost" @click="showPasswordModal = false">{{ t('common.cancel') }}</button>
             
             <button v-if="passwordStep === 1" class="btn btn-primary" :disabled="!passwordSmsCode" @click="handleVerifyPasswordSms">
               {{ t('common.confirm') }}
             </button>
             <button v-else class="btn btn-primary" @click="handleChangePassword">
               {{ t('common.confirm') }}
             </button>
           </div>
        </div>
      </div>
    </transition>

    <!-- Username Change Modal -->
    <transition name="fade">
      <div v-if="showUsernameModal" class="modal-overlay" @click.self="showUsernameModal = false">
        <div class="modal-container glass-card">
           <div class="modal-header">
             <h2>{{ t('profile.changeUsername') }}</h2>
             <button class="close-btn" @click="showUsernameModal = false"><X :size="20" /></button>
           </div>
           
           <div class="modal-body">
             <div class="form-group">
               <label class="label">{{ t('profile.newUsername') }}</label>
               <input v-model="newUsername" type="text" class="input modern-input" :placeholder="t('profile.newUsernamePlaceholder')" />
             </div>

             <div v-if="errorMsg" class="error-notice">
               <AlertCircle :size="16" />
               <span>{{ errorMsg }}</span>
             </div>
           </div>

           <div class="modal-footer">
             <button class="btn btn-ghost" @click="showUsernameModal = false">{{ t('common.cancel') }}</button>
             <button class="btn btn-primary" @click="handleUpdateUsername">{{ t('common.confirm') }}</button>
           </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<style scoped>
.profile-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 3rem 2rem;
  position: relative;
}

/* Ambient Background Lights */
.ambient-light {
  position: absolute;
  border-radius: 50%;
  filter: blur(100px);
  z-index: 0;
  opacity: 0.3;
}

.light-1 { width: 400px; height: 400px; background: var(--color-primary); top: -100px; right: -50px; }
.light-2 { width: 300px; height: 300px; background: var(--color-accent); bottom: 100px; left: -50px; }

/* Header Section */
.profile-header {
  display: flex;
  align-items: center;
  gap: 2.5rem;
  margin-bottom: 4rem;
  position: relative;
  z-index: 10;
}

.profile-avatar-wrapper {
  position: relative;
}

.profile-avatar-glow {
  position: absolute;
  inset: -10px;
  background: var(--color-primary);
  filter: blur(20px);
  border-radius: 50%;
  opacity: 0.3;
}

.profile-avatar {
  width: 110px;
  height: 110px;
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-accent) 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 3rem;
  font-weight: 800;
  border: 4px solid var(--color-bg-dark);
  position: relative;
  z-index: 1;
}

.online-indicator {
  position: absolute;
  bottom: 8px;
  right: 8px;
  width: 18px;
  height: 18px;
  background: #10b981;
  border-radius: 50%;
  border: 3px solid var(--color-bg-dark);
  box-shadow: 0 0 10px rgba(16, 185, 129, 0.5);
  z-index: 2;
}

.welcome-title {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
}

.user-badge {
  display: inline-flex;
  padding: 0.375rem 1rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--color-border);
  border-radius: 100px;
}

.user-id {
  font-size: 0.875rem;
  font-weight: 700;
  color: var(--color-text-secondary);
  letter-spacing: 0.05em;
}

/* Grid Layout */
.profile-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2.5rem;
  position: relative;
  z-index: 10;
}

.card-column {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

/* Wallet Card */
/* .wallet-card {
  padding: 0;
  background: var(--primary-100);
  border: none;
  min-height: 240px;
  overflow: hidden;
}

.wallet-glow {
  position: absolute;
  top: -50px;
  right: -50px;
  width: 200px;
  height: 200px;
  background: rgba(255, 255, 255, 0.15);
  filter: blur(50px);
  border-radius: 50%;
}

.wallet-content {
  padding: 2.5rem;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.wallet-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
}

.icon-box {
  width: 48px;
  height: 48px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(10px);
}

.icon-box.accent { background: rgba(var(--color-accent-rgb), 0.2); }

.wallet-label {
  font-weight: 700;
  color: white;
  font-size: 1.125rem;
}

.credits-main {
  display: flex;
  align-items: baseline;
  gap: 0.75rem;
  margin-bottom: 2.5rem;
}

.credits-main .amount {
  font-size: 4rem;
  font-weight: 800;
  color: white;
  line-height: 1;
}

.credits-main .unit {
  font-size: 1.25rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.7);
}

.view-history {
  margin-top: auto;
  align-self: flex-start;
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.1);
  color: white;
}

.view-history:hover {
  background: rgba(255, 255, 255, 0.2);
} */

/* --- 积分钱包卡片：高对比度增强版 --- */
.wallet-card {

/* Rules Section Styles */
.rules-section {
  margin-top: 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding-top: 1rem;
}

.rules-toggle {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: none;
  border: none;
  color: var(--color-text-secondary);
  font-size: 0.875rem;
  cursor: pointer;
  padding: 0;
  transition: color 0.2s;
}

.rules-toggle:hover {
  color: var(--color-primary);
}

.rules-toggle .rotate {
  transform: rotate(90deg);
}

.rules-content {
  margin-top: 1rem;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
  padding: 1rem;
}

.rules-title {
  font-size: 0.875rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: var(--color-text-primary);
}

.rules-list {
  list-style: none;
  padding: 0;
  margin: 0;
  font-size: 0.8125rem;
  color: var(--color-text-secondary);
}

.rules-list li {
  margin-bottom: 0.5rem;
  padding-left: 0;
}

.rules-list li:last-child {
  margin-bottom: 0;
}

.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.3s ease-out;
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  transform: translateY(-10px);
  opacity: 0;
}
  position: relative;
  padding: 0;
  /* 使用深色渐变背景，确保白色文字绝对清晰 */
  background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important; 
  border: 1px solid rgba(255, 255, 255, 0.25) !important;
  box-shadow: 0 15px 35px rgba(79, 70, 229, 0.3);
  overflow: hidden;
  height: 220px;
  display: flex;
  flex-direction: column;
}

/* 背景装饰圆圈 */
.wallet-decoration .circle-1 {
  position: absolute;
  top: -20px;
  right: -20px;
  width: 150px;
  height: 150px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  filter: blur(30px);
}

.wallet-content {
  position: relative;
  z-index: 2;
  height: 100%;
  padding: 1.5rem 2rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.wallet-top {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.wallet-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.icon-glow-box {
  width: 36px;
  height: 36px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(4px);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.wallet-label {
  font-size: 1rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.95); /* 提高对比度 */
  letter-spacing: 0.5px;
}

.balance-main {
  display: flex;
  align-items: baseline;
  gap: 0.6rem;
}

.amount-integer {
  font-size: 3.8rem;
  font-weight: 800;
  color: #ffffff;
  line-height: 1.1;
  /* 关键：增加阴影，防止在亮色背景下看不清 */
  text-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
  font-family: 'Space Grotesk', sans-serif;
}

.amount-unit {
  font-size: 1.2rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.85);
}

.recharge-note {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
  margin-top: -0.2rem;
}

.wallet-bottom {
  border-top: 1px solid rgba(255, 255, 255, 0.2);
  padding-top: 1rem;
}

.action-link-btn {
  background: none;
  border: none;
  padding: 0;
  display: flex;
  align-items: center;
  gap: 0.6rem;
  color: #ffffff;
  font-weight: 700;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.icon-circle {
  width: 26px;
  height: 26px;
  background: #ffffff;
  color: #4f46e5;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.action-link-btn:hover .icon-circle {
  transform: translateX(8px);
  box-shadow: 0 0 15px rgba(255, 255, 255, 0.5);
}

/* Invite Card */
.invite-card {
  padding: 2.5rem;
  display: flex;
  flex-direction: column;
}

.invite-header {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  margin-bottom: 1.5rem;
}

.invite-header h2 {
  font-size: 1.5rem;
  font-weight: 800;
}

.invite-description {
  color: var(--color-text-secondary);
  font-size: 1rem;
  line-height: 1.6;
  margin-bottom: 2.5rem;
}

.invite-controls {
  margin-top: auto;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.code-display label {
  display: block;
  font-size: 0.75rem;
  font-weight: 800;
  text-transform: uppercase;
  color: var(--color-text-muted);
  margin-bottom: 0.75rem;
  letter-spacing: 0.05em;
}

.code-box {
  background: var(--color-background);
  border: 1px solid var(--color-border);
  padding: 1rem 1.5rem;
  border-radius: 12px;
  display: flex;
  justify-content: center;
}

.code-box code {
  font-size: 1.75rem;
  font-weight: 800;
  letter-spacing: 0.1em;
  color: var(--color-primary);
  font-family: 'Space Grotesk', sans-serif;
}

/* Settings Column */
.group-title {
  font-size: 1.25rem;
  font-weight: 800;
  margin-bottom: 1.5rem;
}

.settings-stack {
  padding: 0;
  overflow: hidden;
}

.settings-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.75rem 2rem;
  transition: all 0.3s;
  cursor: pointer;
}

.settings-item:hover:not(.disabled) {
  background: var(--bg-200);
}

.settings-item.disabled {
  cursor: default;
  opacity: 0.6;
}

.item-visual {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.icon-pill {
  width: 44px;
  height: 44px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-pill.blue { background: rgba(59, 130, 246, 0.1); color: #3b82f6; }
.icon-pill.orange { background: rgba(249, 115, 22, 0.1); color: #f97316; }
.icon-pill.green { background: rgba(16, 185, 129, 0.1); color: #10b981; }

.item-label {
  display: block;
  font-weight: 700;
  font-size: 1.05rem;
  margin-bottom: 0.25rem;
}

.item-value {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}

.item-action {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.status-marker {
  font-size: 0.7rem;
  font-weight: 800;
  padding: 0.375rem 0.875rem;
  border-radius: 100px;
  text-transform: uppercase;
  background: var(--bg-200);
  color: var(--text-200);
}

.status-marker.linked {
  background: rgba(40, 167, 69, 0.1);
  color: #28a745;
}

.item-divider {
  height: 1px;
  background: var(--color-border);
  margin: 0 2rem;
}

.chevron { color: var(--color-text-muted); }

/* Modals */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(8px);
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.modal-container {
  width: 100%;
  max-width: 480px;
  padding: 0;
  overflow: hidden;
  animation: modalUp 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes modalUp {
  from { opacity: 0; transform: translateY(40px) scale(0.95); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

.modal-header {
  padding: 2rem;
  border-bottom: 1px solid var(--color-border);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-with-steps {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.step-nav {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.step-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-border);
  transition: all 0.3s;
}

.step-dot.active {
  background: var(--color-primary);
  box-shadow: 0 0 10px var(--color-primary);
}

.step-line { width: 24px; height: 1px; background: var(--color-border); }

.close-btn {
  background: var(--color-surface-hover);
  border: none;
  color: var(--color-text-secondary);
  width: 36px; height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}

.close-btn:hover { background: var(--color-border); color: var(--color-text-main); }

.modal-body {
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.modal-footer {
  padding: 2rem;
  border-top: 1px solid var(--bg-300);
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  background: var(--bg-200);
}

.captcha-row, .sms-row {
  display: flex;
  gap: 0.75rem;
}

.captcha-box {
  width: 120px;
  height: 48px;
  background: white;
  border-radius: var(--radius-md);
  overflow: hidden;
  position: relative;
  cursor: pointer;
}

.captcha-img { width: 100%; height: 100%; object-fit: contain; }

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

.captcha-box:hover .captcha-overlay { opacity: 1; }

.phone-display {
  background: var(--color-background);
  padding: 1rem;
  border-radius: 12px;
  border: 1px dashed var(--color-border);
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 700;
  text-align: center;
  font-size: 1.25rem;
  letter-spacing: 0.1em;
}

.modern-textarea {
  width: 100%;
  background: white;
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 1rem;
  color: var(--color-text-main);
  font-size: 0.9rem;
  line-height: 1.6;
  resize: none;
  font-family: inherit;
  outline: none;
}

.error-notice {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  background: rgba(220, 53, 69, 0.08);
  border-radius: 12px;
  color: #dc3545;
  font-size: 0.875rem;
}

/* Animations */
.animate-fade-in { animation: fadeIn 0.6s ease-out; }
.animate-fade-up { animation: fadeUp 0.6s ease-out forwards; opacity: 0; }

@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes fadeUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }

@media (max-width: 900px) {
  .profile-grid { grid-template-columns: 1fr; }
  .profile-header { flex-direction: column; text-align: center; gap: 1.5rem; }
}

.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>

