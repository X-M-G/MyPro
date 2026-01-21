<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { Globe } from 'lucide-vue-next'
import { ref } from 'vue'

const { locale } = useI18n()
const showDropdown = ref(false)

const languages = [
  { code: 'en', name: 'English', flag: '🇺🇸' },
  { code: 'zh', name: '中文', flag: '🇨🇳' }
]

function changeLanguage(lang: string) {
  locale.value = lang
  localStorage.setItem('app-language', lang)
  showDropdown.value = false
}

function getCurrentLanguage() {
  return languages.find(l => l.code === locale.value) || languages[0]
}
</script>

<template>
  <div class="language-switcher" @click="showDropdown = !showDropdown">
    <div class="current-lang">
      <Globe :size="18" />
      <span>{{ getCurrentLanguage().flag }} {{ getCurrentLanguage().name }}</span>
    </div>
    
    <transition name="dropdown">
      <div v-if="showDropdown" class="dropdown-menu" @click.stop>
        <div 
          v-for="lang in languages" 
          :key="lang.code"
          class="dropdown-item"
          :class="{ active: locale === lang.code }"
          @click="changeLanguage(lang.code)"
        >
          <span class="flag">{{ lang.flag }}</span>
          <span class="lang-name">{{ lang.name }}</span>
        </div>
      </div>
    </transition>
  </div>
</template>

<style scoped>
.language-switcher {
  position: relative;
  cursor: pointer;
  user-select: none;
}

.current-lang {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 1rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.9rem;
  color: #475569;
  transition: all 0.2s;
}

.current-lang:hover {
  background: #f1f5f9;
  border-color: #cbd5e1;
}

.dropdown-menu {
  position: absolute;
  top: calc(100% + 0.5rem);
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  z-index: 100;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  font-size: 0.9rem;
  color: #475569;
  transition: all 0.2s;
  cursor: pointer;
}

.dropdown-item:hover {
  background: #f8fafc;
}

.dropdown-item.active {
  background: #eef2ff;
  color: #4f46e5;
  font-weight: 600;
}

.flag {
  font-size: 1.2rem;
}

.lang-name {
  flex: 1;
}

/* Dropdown animation */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.2s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
