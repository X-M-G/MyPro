<template>
  <div class="page-container about-page">
    <div class="glass-card about-card animate-fade-up">
      <div class="logo-circle">
        <Sparkles :size="32" class="text-primary" />
      </div>
      <h1 class="page-title">About Sora AI</h1>
      <p class="about-text">
        Experience the future of video generation with Sora AI. Our platform leverages state-of-the-art 
        artificial intelligence to transform your creative visions into high-quality videos, 
        making professional-grade content creation accessible to everyone.
      </p>
      <div class="stats-row">
        <div class="stat-item">
          <span class="stat-val">Sora</span>
          <span class="stat-label">Model</span>
        </div>
        <div class="stat-sep"></div>
        <div class="stat-item">
          <span class="stat-val">4K</span>
          <span class="stat-label">Resolution</span>
        </div>
        <div class="stat-sep"></div>
        <div class="stat-item">
          <span class="stat-val">AI</span>
          <span class="stat-label">Powered</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Sparkles } from 'lucide-vue-next'
</script>

<style scoped>
.about-page {
  min-height: 80vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

/* Removed ambient light */

.about-card {
  max-width: 600px;
  text-align: center;
  padding: 4rem 3rem;
}

.logo-circle {
  width: 80px;
  height: 80px;
  background: var(--primary-300);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 2rem;
  border: 1px solid var(--primary-200);
}

.page-title {
  font-size: 2.25rem;
  margin-bottom: 1.5rem;
}

.about-text {
  font-size: 1.125rem;
  line-height: 1.7;
  color: var(--color-text-secondary);
  margin-bottom: 3rem;
}

.stats-row {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 2rem;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.stat-val {
  font-size: 1.25rem;
  font-weight: 800;
  color: var(--color-text-main);
}

.stat-label {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--color-text-muted);
}

.stat-sep {
  width: 1px;
  height: 40px;
  background: var(--color-border);
}

.animate-fade-up { animation: fadeUp 0.8s ease-out forwards; }
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>

