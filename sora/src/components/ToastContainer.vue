<script setup lang="ts">
import { toastState, toast } from '@/utils/toast'
import { 
  CheckCircle2, 
  AlertCircle, 
  Info, 
  AlertTriangle,
  X
} from 'lucide-vue-next'

const getIcon = (type: string) => {
  switch (type) {
    case 'success': return CheckCircle2
    case 'error': return AlertCircle
    case 'warning': return AlertTriangle
    default: return Info
  }
}
</script>

<template>
  <div class="toast-container">
    <TransitionGroup name="toast">
      <div 
        v-for="item in toastState.toasts" 
        :key="item.id" 
        class="toast-item"
        :class="item.type"
      >
        <div class="toast-icon">
          <component :is="getIcon(item.type)" :size="20" />
        </div>
        <div class="toast-content">
          {{ item.message }}
        </div>
        <button class="toast-close" @click="toast.remove(item.id)">
          <X :size="16" />
        </button>
      </div>
    </TransitionGroup>
  </div>
</template>

<style scoped>
.toast-container {
  position: fixed;
  top: 2rem;
  right: 2rem;
  z-index: 20000;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  pointer-events: none;
}

.toast-item {
  pointer-events: auto;
  min-width: 300px;
  max-width: 450px;
  padding: 1rem 1.25rem;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  color: #fff;
  overflow: hidden;
  position: relative;
}

.toast-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
}

.toast-item.success::before { background: var(--color-success, #10b981); }
.toast-item.error::before { background: var(--color-error, #f43f5e); }
.toast-item.warning::before { background: var(--color-warning, #f59e0b); }
.toast-item.info::before { background: var(--color-primary, #6366f1); }

.toast-icon {
  flex-shrink: 0;
  display: flex;
  align-items: center;
}

.toast-item.success { color: #10b981; border-color: rgba(16, 185, 129, 0.2); }
.toast-item.error { color: #f43f5e; border-color: rgba(244, 63, 94, 0.2); }
.toast-item.warning { color: #f59e0b; border-color: rgba(245, 158, 11, 0.2); }

.toast-item.success .toast-icon { color: #10b981; }
.toast-item.error .toast-icon { color: #f43f5e; }
.toast-item.warning .toast-icon { color: #f59e0b; }
.toast-item.info .toast-icon { color: #6366f1; }

.toast-content {
  flex-grow: 1;
  font-size: 0.95rem;
  font-weight: 500;
  line-height: 1.4;
}

.toast-close {
  flex-shrink: 0;
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s;
  display: flex;
  align-items: center;
}

.toast-close:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}

/* Transitions */
.toast-enter-active,
.toast-leave-active {
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(50px) scale(0.9);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(30px) scale(0.95);
}

.toast-move {
  transition: transform 0.4s ease;
}
</style>
