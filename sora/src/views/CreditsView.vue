<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useI18n } from 'vue-i18n'
import { Wallet, Filter, ChevronLeft, ChevronRight, ArrowUpRight, ArrowDownLeft } from 'lucide-vue-next'

const authStore = useAuthStore()
const { t } = useI18n()
const transactions = ref<any[]>([])
const loading = ref(false)

// Pagination & Filtering
const currentPage = ref(1)
const totalItems = ref(0)
const itemsPerPage = 10
const filterDays = ref('all') // '7', '30', 'all'

const timeFilters = [
    { label: t('profile.filters.allTime'), value: 'all' },
    { label: t('profile.filters.last7Days'), value: '7' },
    { label: t('profile.filters.last30Days'), value: '30' }
]

async function loadHistory() {
  loading.value = true
  const days = filterDays.value === 'all' ? null : (filterDays.value as any)
  const data = await authStore.fetchCreditHistory(currentPage.value, days)
  
  if (data.results) {
      transactions.value = data.results
      totalItems.value = data.count
  } else {
      transactions.value = []
      totalItems.value = 0
  }
  loading.value = false
}

function handlePageChange(newPage: number) {
    if (newPage < 1 || newPage > Math.ceil(totalItems.value / itemsPerPage)) return
    currentPage.value = newPage
    loadHistory()
}

watch(filterDays, () => {
    currentPage.value = 1
    loadHistory()
})

onMounted(async () => {
  await loadHistory()
})
</script>

<template>
  <div class="page-container credits-view">
    <div class="header-section animate-fade-in">
      <div class="header-content">
        <div class="header-badge">
          <Wallet :size="16" class="text-primary" />
          <span>Credit Ledger</span>
        </div>
        <h1 class="page-title">{{ t('profile.creditsPageTitle') }}</h1>
        <p class="subtitle">{{ t('profile.creditsPageSubtitle') }}</p>
      </div>
      
      <div class="filter-wrapper glass-card">
        <Filter :size="18" class="filter-icon" />
        <select v-model="filterDays" class="select-field">
          <option v-for="opt in timeFilters" :key="opt.value" :value="opt.value">
            {{ opt.label }}
          </option>
        </select>
      </div>
    </div>

    <div class="glass-card ledger-card animate-fade-up">
      <div v-if="loading" class="loading-state">
        <Loader2 class="animate-spin text-primary" :size="32" />
      </div>

      <div v-else-if="transactions.length > 0" class="ledger-wrapper">
        <div class="table-container">
          <table class="ledger-table">
            <thead>
              <tr>
                <th class="col-type text-center">{{ t('profile.type') }}</th>
                <th class="col-desc">{{ t('profile.description') }}</th>
                <th class="col-date">{{ t('profile.date') }}</th>
                <th class="col-amount text-center">{{ t('profile.amount') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="tx in transactions" :key="tx.id" class="ledger-row">
                <td class="text-center">
                  <div class="tx-badge" :class="tx.amount > 0 ? 'positive' : 'negative'">
                    <ArrowDownLeft v-if="tx.amount > 0" :size="14" />
                    <ArrowUpRight v-else :size="14" />
                  </div>
                </td>
                <td>
                  <span class="tx-description">{{ tx.description }}</span>
                </td>
                <td class="tx-timestamp">
                  {{ new Date(tx.timestamp).toLocaleString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }) }}
                </td>
                <td class="text-center">
                  <span class="tx-value" :class="tx.amount > 0 ? 'gain' : 'loss'">
                    {{ tx.amount > 0 ? '+' : '' }}{{ tx.amount }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <!-- Pagination -->
        <div class="ledger-footer">
          <span class="ledger-info">
            {{ t('profile.showing') }} <strong>{{ (currentPage - 1) * itemsPerPage + 1 }}</strong> - 
            <strong>{{ Math.min(currentPage * itemsPerPage, totalItems) }}</strong> {{ t('profile.of') }} <strong>{{ totalItems }}</strong>
          </span>
          <div class="pagination-btns">
            <button 
              class="btn btn-ghost btn-sm btn-icon" 
              :disabled="currentPage === 1"
              @click="handlePageChange(currentPage - 1)"
            >
              <ChevronLeft :size="18" />
            </button>
            <span class="page-num">{{ currentPage }}</span>
            <button 
              class="btn btn-ghost btn-sm btn-icon" 
              :disabled="currentPage * itemsPerPage >= totalItems"
              @click="handlePageChange(currentPage + 1)"
            >
              <ChevronRight :size="18" />
            </button>
          </div>
        </div>
      </div>

      <div v-else class="empty-state">
        <div class="empty-icon glass-card">
          <Wallet :size="48" class="text-muted" />
        </div>
        <p>{{ t('profile.noTransactions') }}</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.credits-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2.5rem;
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 3rem;
}

.header-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: var(--primary-300);
  border: 1px solid var(--primary-200);
  border-radius: 100px;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--primary-100);
  margin-bottom: 1rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}



.page-title {
  font-size: 2.25rem;
  margin-bottom: 0.75rem;
}

.subtitle {
  color: var(--color-text-secondary);
  font-size: 1rem;
}

.filter-wrapper {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 1rem;
  background: rgba(255, 255, 255, 0.03);
}

.filter-icon {
  color: var(--color-text-muted);
}

.select-field {
  background: transparent;
  border: none;
  color: var(--color-text-main);
  font-weight: 700;
  font-size: 0.875rem;
  cursor: pointer;
  outline: none;
}

.select-field option {
  background: white;
  color: var(--color-text-main);
}

/* Ledger Card */
.ledger-card {
  padding: 0;
  overflow: hidden;
}

.loading-state {
  padding: 8rem 0;
  display: flex;
  justify-content: center;
}

.table-container {
  overflow-x: auto;
}

.ledger-table {
  width: 100%;
  border-collapse: collapse;
}

.ledger-table th {
  padding: 1rem 1.5rem;
  background: var(--color-surface-hover);
  border-bottom: 1px solid var(--color-border);
  color: var(--color-text-muted);
  font-weight: 800;
  text-transform: uppercase;
  font-size: 0.7rem;
  letter-spacing: 0.1em;
  text-align: left;
}

.ledger-row {
  transition: background 0.2s;
}

.ledger-row:hover {
  background: var(--color-surface-hover);
}

.ledger-table td {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid var(--color-border);
  font-size: 0.95rem;
}

.tx-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 8px;
}

.tx-badge.positive {
  background: rgba(40, 167, 69, 0.1);
  color: #28a745;
}

.tx-badge.negative {
  background: var(--color-surface-hover);
  color: var(--color-text-secondary);
}

.tx-description {
  font-weight: 600;
  color: var(--color-text-main);
}

.tx-timestamp {
  color: var(--color-text-secondary);
  font-size: 0.875rem;
}

.tx-value {
  font-weight: 800;
  font-family: inherit;
  font-size: 1.125rem;
}

.tx-value.gain {
  color: #28a745;
}

.tx-value.loss {
  color: var(--color-text-main);
}

.ledger-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  background: var(--color-surface);
  border-top: 1px solid var(--color-border);
}

.ledger-info {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}

.ledger-info strong {
  color: var(--color-text-main);
}

.pagination-btns {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.page-num {
  font-weight: 800;
  color: var(--color-primary);
  font-size: 1rem;
}

.empty-state {
  text-align: center;
  padding: 8rem 0;
}

.empty-icon {
  width: 96px;
  height: 96px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1.5rem;
  border-radius: 24px;
}

.text-center { text-align: center !important; }

.animate-fade-in { animation: fadeIn 0.5s ease-out; }
.animate-fade-up { animation: fadeUp 0.6s ease-out forwards; opacity: 0; }

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 768px) {
  .header-section {
    flex-direction: column;
    align-items: flex-start;
    gap: 2rem;
  }
}
</style>
