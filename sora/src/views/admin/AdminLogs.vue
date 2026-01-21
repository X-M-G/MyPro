<template>
  <div class="logs-executive-view animate-page-fade">
    <!-- Header Section -->
    <div class="page-header">
      <div class="header-info">
        <h2 class="view-title">{{ $t('admin.operationalIntelligence') }}</h2>
        <p class="view-subtitle">{{ $t('admin.operationalIntelligenceSub') }}</p>
      </div>
    </div>

    <!-- Filters Section -->
    <div class="filter-panel glass-card">
      <div class="filter-group">
        <el-input
          v-model="searchQuery"
          :placeholder="$t('admin.filterByUsername')"
          class="executive-input"
          @keyup.enter="handleFilter"
        >
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
        
        <el-button class="filter-btn" @click="handleFilter">
          {{ $t('common.search') }}
        </el-button>
      </div>
    </div>

    <!-- Table Section -->
    <div class="table-container glass-card">
      <el-table
        v-loading="listLoading"
        :data="list"
        class="executive-table"
        row-class-name="executive-row"
      >
        <el-table-column prop="id" label="ID" width="80" align="center" />
        <el-table-column prop="user" :label="$t('auth.login.username')" width="140">
          <template #default="{ row }">
            <span class="user-chip">{{ row.user }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="type" :label="$t('admin.type')" width="110" align="center">
          <template #default="{ row }">
            <el-tag :type="getTypeColor(row.type)" class="executive-tag">{{ row.type }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="model" :label="$t('admin.model')" width="110" align="center">
          <template #default="{ row }">
            <span class="user-chip">{{ row.model }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="prompt" :label="$t('admin.prompt')" min-width="300">
          <template #default="{ row }">
            <div class="prompt-cell">
              <span class="prompt-text" :title="row.prompt">{{ row.prompt }}</span>
              <el-button 
                v-if="row.prompt" 
                circle 
                size="small" 
                class="copy-btn" 
                :icon="CopyDocument"
                @click="copyToClipboard(row.prompt)"
              />
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="status" :label="$t('admin.status')" width="110" align="center">
          <template #default="{ row }">
            <div class="status-indicator" :class="row.status.toLowerCase()">
              <span class="dot"></span>
              {{ row.status }}
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="duration" :label="$t('admin.duration')" width="90" align="center">
          <template #default="{ row }">
            <span class="duration-text">{{ row.duration }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="generation_time" :label="$t('admin.generationTime')" width="100" align="center">
          <template #default="{ row }">
            <span class="gen-time-text" :class="{ 'success-time': row.status === 'SUCCESS' && row.generation_time !== '-', 'failed-time': row.status === 'FAILED' && row.generation_time !== '-' }">
              {{ row.generation_time }}
            </span>
          </template>
        </el-table-column>

        <el-table-column prop="created_at" :label="$t('admin.createdAt')" width="180" align="right">
          <template #default="{ row }">
            <span class="date-text">{{ formatDate(row.created_at) }}</span>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-area">
        <el-pagination
          v-model:current-page="listQuery.page"
          v-model:page-size="listQuery.limit"
          layout="total, prev, pager, next"
          :total="total"
          @current-change="getList"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import api from '@/utils/api'
import { Search, CopyDocument } from '@element-plus/icons-vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'

const { t } = useI18n()

const list = ref([])
const total = ref(0)
const listLoading = ref(true)
const searchQuery = ref('')
const listQuery = reactive({
  page: 1,
  limit: 20
})

const getTypeColor = (type: string) => {
  if (type.includes('VIDEO')) return 'primary'
  if (type.includes('PROMPT')) return 'success'
  return 'info'
}

const copyToClipboard = async (text: string) => {
  try {
    await navigator.clipboard.writeText(text)
    ElMessage.success(t('admin.copySuccess'))
  } catch (err) {
    ElMessage.error(t('common.error'))
  }
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  }).replace(/\//g, '-')
}

const getList = async () => {
    listLoading.value = true
    try {
        const response = await api.get('adym/logs/', {
            params: {
                page: listQuery.page,
                username: searchQuery.value
            }
        })
        list.value = response.data.results
        total.value = response.data.count
    } catch (e) {
        ElMessage.error(t('common.error'))
    } finally {
        listLoading.value = false
    }
}

const handleFilter = () => {
    listQuery.page = 1
    getList()
}

onMounted(() => {
    getList()
})
</script>

<style scoped>
.logs-executive-view {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.page-header {
  margin-bottom: 8px;
}

.view-title {
  font-size: 1.8rem;
  font-weight: 800;
  color: var(--admin-text-primary);
  letter-spacing: -0.02em;
}

.view-subtitle {
  color: var(--admin-text-secondary);
  font-size: 0.95rem;
}

.filter-panel {
  padding: 24px;
  border-radius: 20px;
}

.filter-group {
  display: flex;
  gap: 16px;
  align-items: center;
}

.executive-input {
  width: 320px;
}

:deep(.el-input__wrapper) {
  background: white;
  border: 1px solid var(--admin-border);
  box-shadow: none !important;
  border-radius: 12px;
  height: 44px;
}

.filter-btn {
  height: 44px;
  padding: 0 24px;
  border-radius: 12px;
  font-weight: 700;
  background: var(--admin-sidebar-bg);
  color: white;
  border: none;
  cursor: pointer;
  transition: all 0.3s;
}

.filter-btn:hover {
  background: #1e293b;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.table-container {
  padding: 0;
  border-radius: 24px;
  overflow: hidden;
}

.executive-table {
  background: var(--admin-surface-alt);
}

:deep(.el-table__header-wrapper th) {
  background: var(--admin-surface-alt) !important;
  color: var(--admin-text-secondary);
  font-weight: 700;
  text-transform: uppercase;
  font-size: 0.75rem;
  letter-spacing: 0.05em;
  padding: 20px 0;
}

:deep(.executive-row) {
  background: white !important;
}

:deep(.el-table__row:hover td) {
  background: var(--admin-surface-alt) !important;
}

.user-chip {
  font-weight: 700;
  color: var(--admin-sidebar-bg);
  background: rgba(15, 23, 42, 0.05);
  padding: 4px 10px;
  border-radius: 8px;
  font-size: 0.85rem;
  display: inline-block;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.executive-tag {
  border-radius: 8px;
  font-weight: 700;
  border: none;
}

.prompt-cell {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
}

.prompt-text {
  flex: 1;
   white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: var(--admin-text-primary);
  font-size: 0.9rem;
  font-style: italic;
}

.copy-btn {
  flex-shrink: 0;
  border: 1px solid var(--admin-border);
  background: white;
  color: var(--admin-text-secondary);
  transition: all 0.2s;
}

.copy-btn:hover {
  background: var(--admin-surface-alt);
  color: var(--admin-accent-gold);
  border-color: var(--admin-accent-gold);
}

.status-indicator {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-weight: 700;
  font-size: 0.75rem;
  text-transform: uppercase;
}

.status-indicator .dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.success { color: var(--admin-accent-teal); }
.success .dot { background: var(--admin-accent-teal); box-shadow: 0 0 8px var(--admin-accent-teal); }

.failed { color: var(--admin-accent-orange); }
.failed .dot { background: var(--admin-accent-orange); box-shadow: 0 0 8px var(--admin-accent-orange); }

.pending { color: var(--admin-accent-gold); }
.pending .dot { background: var(--admin-accent-gold); box-shadow: 0 0 8px var(--admin-accent-gold); }

.duration-text, .gen-time-text {
  font-family: var(--font-heading);
  font-weight: 600;
  color: var(--admin-text-secondary);
}

.gen-time-text.success-time {
  color: var(--admin-accent-teal);
}

.gen-time-text.failed-time {
  color: var(--admin-accent-orange);
}

.date-text {
  color: var(--admin-text-secondary);
  font-size: 0.85rem;
  font-weight: 500;
  font-family: monospace;
}

.pagination-area {
  padding: 24px 32px;
  background: white;
  display: flex;
  justify-content: flex-end;
}
</style>
