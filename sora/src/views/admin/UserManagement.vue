<template>
  <div class="user-executive-view animate-page-fade">
    <!-- Header Section -->
    <div class="page-header">
      <div class="header-info">
        <h2 class="view-title">{{ $t('admin.userRegistry') }}</h2>
        <p class="view-subtitle">{{ $t('admin.userRegistrySub') }}</p>
      </div>
      <el-button class="action-btn gold" type="primary" :icon="Plus" @click="handleCreateUser">
        {{ $t('admin.createUser') }}
      </el-button>
    </div>

    <!-- Filters Section -->
    <div class="filter-panel glass-card">
      <div class="filter-group">
        <el-input
          v-model="searchQuery"
          :placeholder="$t('admin.searchPlaceholder')"
          class="executive-input"
          @keyup.enter="handleFilter"
        >
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
        
        <el-select v-model="sortOrder" class="executive-select" @change="handleFilter">
          <el-option label="Join Date (Newest)" value="-date_joined" />
          <el-option label="Credits (High to Low)" value="credits_desc" />
          <el-option label="Credits (Low to High)" value="credits_asc" />
        </el-select>
        
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
        <el-table-column prop="id" label="ID" width="80" align="center"></el-table-column>
        <el-table-column prop="username" :label="$t('auth.login.username')" width="180">
          <template #default="{ row }">
            <span class="user-name">{{ row.username }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="email" :label="$t('auth.login.email')" min-width="220">
          <template #default="{ row }">
            <span class="user-email">{{ row.email }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="phone_number" :label="$t('profile.phoneInfo')" width="150" align="center">
          <template #default="{ row }">
            <span class="text-gray">{{ row.phone_number || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="credits" :label="$t('admin.credits')" width="120" align="center">
          <template #default="{ row }">
            <div class="credit-badge" :class="{ 'low': row.credits <= 10 }">
              {{ row.credits }}
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="date_joined" :label="$t('admin.dateJoined')" width="180">
          <template #default="{ row }">
            <span class="date-text">{{ new Date(row.date_joined).toLocaleDateString() }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="invited_by" :label="$t('admin.inviter')" width="150" align="center">
          <template #default="{ row }">
            <span v-if="row.invited_by">{{ row.invited_by }}</span>
            <span v-else class="text-gray">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="is_effective" :label="$t('admin.inviteStatus')" width="120" align="center">
          <template #default="{ row }">
            <template v-if="row.invited_by">
                <el-tag v-if="row.is_effective" type="success" size="small" effect="dark">Effective</el-tag>
                <el-tag v-else type="info" size="small">Invalid</el-tag>
            </template>
            <span v-else class="text-gray">-</span>
          </template>
        </el-table-column>
        
        <el-table-column :label="$t('common.actions')" align="right" width="380">
          <template #default="{ row }">
            <div class="action-group">
              <el-button class="mini-btn teal" @click="handleEditCredits(row)">{{ $t('admin.editCredits') }}</el-button>
              <el-button class="mini-btn navy" @click="handleViewDetails(row)">{{ $t('admin.details') }}</el-button>
              <el-button class="mini-btn gold" @click="handlePassword(row)">{{ $t('profile.changePassword') }}</el-button>
              <el-button class="mini-btn danger" @click="handleDelete(row)">{{ $t('common.delete') }}</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-area">
        <el-pagination
          v-model:current-page="listQuery.page"
          v-model:page-size="listQuery.limit"
          :page-sizes="[10, 20, 30, 50]"
          layout="total, sizes, prev, pager, next"
          :total="total"
          @size-change="getList"
          @current-change="getList"
        />
      </div>
    </div>

    <!-- Modals (Executive Redesign) -->
    
    <!-- Edit Credits Dialog -->
    <el-dialog :title="$t('admin.updateCredits')" v-model="dialogVisible" width="450px" custom-class="executive-dialog">
      <div class="dialog-content">
        <div class="target-profile">
          <div class="avatar-small">AD</div>
          <div class="info">
            <span class="name">{{ temp.username }}</span>
            <span class="sub">{{ $t('admin.currentAllocation') }}: {{ temp.credits }}</span>
          </div>
        </div>
        
        <el-form :model="temp" label-position="top">
          <el-form-item :label="$t('admin.amount')">
            <el-input-number v-model="creditForm.amount" :step="10" class="executive-number" />
            <div class="form-tip">{{ $t('admin.negativeToDeduct') }}</div>
          </el-form-item>
          <el-form-item :label="$t('admin.description')">
            <el-input v-model="creditForm.description" :placeholder="$t('admin.allocationRationale')" />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false" class="cancel-btn">{{ $t('common.cancel') }}</el-button>
          <el-button type="primary" @click="updateData" class="confirm-btn gold">{{ $t('common.confirm') }}</el-button>
        </div>
      </template>
    </el-dialog>
    
    <!-- Change Password Dialog -->
    <el-dialog :title="$t('profile.changePassword')" v-model="passwordDialogVisible" width="450px" custom-class="executive-dialog">
      <div class="dialog-content">
        <el-form :model="passwordForm" label-position="top">
          <el-form-item :label="$t('profile.newPassword')">
            <el-input v-model="passwordForm.password" type="password" show-password />
          </el-form-item>
          <el-form-item :label="$t('profile.confirmNewPassword')">
            <el-input v-model="passwordForm.confirmPassword" type="password" show-password />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="passwordDialogVisible = false" class="cancel-btn">{{ $t('common.cancel') }}</el-button>
          <el-button type="primary" @click="submitPasswordChange" class="confirm-btn gold">{{ $t('common.confirm') }}</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- Create User Dialog -->
    <el-dialog :title="$t('admin.createUser')" v-model="createDialogVisible" width="450px" custom-class="executive-dialog">
      <div class="dialog-content">
        <el-form :model="createForm" label-position="top">
          <el-form-item :label="$t('auth.login.username')">
            <el-input v-model="createForm.username" />
          </el-form-item>
          <el-form-item :label="$t('auth.login.password')">
            <el-input v-model="createForm.password" type="password" show-password />
          </el-form-item>
          <el-form-item :label="$t('admin.credits')">
            <el-input-number v-model="createForm.credits" :step="10" class="executive-number" />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="createDialogVisible = false" class="cancel-btn">{{ $t('common.cancel') }}</el-button>
          <el-button type="primary" @click="submitCreateUser" class="confirm-btn gold">{{ $t('common.confirm') }}</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- User Details Modal (Heavy Refinement) -->
    <el-dialog :title="$t('admin.details')" v-model="detailsDialogVisible" width="80%" custom-class="executive-modal" @opened="handleDetailsOpen" @closed="handleDialogClose">
      <div v-if="userDetailsLoading" class="loading-overlay">
        <el-skeleton :rows="10" animated />
      </div>
      <div v-else class="modal-body">
        <div class="profile-summary glass-card">
          <div class="avatar-large">AD</div>
          <div class="p-details">
            <h3 class="p-name">{{ userDetails.user.username }}</h3>
            <span class="p-email">{{ userDetails.user.email }}</span>
          </div>
          <div class="p-stats">
            <div class="stat-item">
              <span class="label">{{ $t('admin.balance') }}</span>
              <span class="value gold-text">{{ userDetails.user.credits }} {{ $t('admin.credits') }}</span>
            </div>
          </div>
        </div>
        
        <el-tabs class="executive-tabs">
          <el-tab-pane :label="$t('admin.strategicIntelligence')">
            <div class="analytics-section">
              <h4 class="section-title">{{ $t('admin.generationVolume') }}</h4>
              <div ref="chartRef" class="mini-chart"></div>
            </div>
          </el-tab-pane>
          
          <el-tab-pane :label="$t('admin.financialLedger')">
            <el-table :data="userDetails.credit_history" class="nested-table">
              <el-table-column prop="timestamp" :label="$t('admin.timestamp')" width="200">
                <template #default="{ row }">{{ new Date(row.timestamp).toLocaleString() }}</template>
              </el-table-column>
              <el-table-column prop="amount" :label="$t('admin.amount')" width="120">
                <template #default="{ row }">
                  <span :class="row.amount > 0 ? 'text-teal' : 'text-danger'">{{ row.amount > 0 ? '+' : '' }}{{ row.amount }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="balance_after" :label="$t('admin.resolvedBalance')" width="150"></el-table-column>
              <el-table-column prop="description" :label="$t('admin.rationale')"></el-table-column>
            </el-table>
          </el-tab-pane>

          <el-tab-pane :label="$t('admin.accessLogs')">
            <div class="tab-header">
              <el-radio-group v-model="visitRange" size="small" class="executive-radio" @change="handleVisitRangeChange">
                <el-radio-button value="1">24h</el-radio-button>
                <el-radio-button value="7">7D</el-radio-button>
                <el-radio-button value="30">30D</el-radio-button>
              </el-radio-group>
            </div>
            <el-table :data="userDetails.visit_history" class="nested-table">
              <el-table-column prop="timestamp" :label="$t('admin.timestamp')" width="200">
                <template #default="{ row }">{{ new Date(row.timestamp).toLocaleString() }}</template>
              </el-table-column>
              <el-table-column prop="ip" :label="$t('admin.entryIp')" width="160"></el-table-column>
              <el-table-column prop="path" :label="$t('admin.endpointPath')" show-overflow-tooltip></el-table-column>
            </el-table>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick } from 'vue'
import api from '@/utils/api'
import { Search, Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useI18n } from 'vue-i18n'
import * as echarts from 'echarts'

const { t } = useI18n()

const list = ref([])
const total = ref(0)
const listLoading = ref(true)
const listQuery = reactive({
  page: 1,
  limit: 10
})
const searchQuery = ref('')
const sortOrder = ref('-date_joined')

// Create User
const createDialogVisible = ref(false)
const createForm = reactive({ username: '', password: '', credits: 60 })

const handleCreateUser = () => {
    createForm.username = ''
    createForm.password = ''
    createForm.credits = 60
    createDialogVisible.value = true
}

const submitCreateUser = async () => {
    if (!createForm.username || !createForm.password) {
        ElMessage.warning('Username and password required')
        return
    }
    try {
        await api.post('adym/users/create/', createForm)
        ElMessage.success(t('common.success'))
        createDialogVisible.value = false
        getList()
    } catch (e: any) {
        ElMessage.error(e.response?.data?.error || t('common.error'))
    }
}

// Credits Edit
const dialogVisible = ref(false)
const temp = ref<any>({})
const creditForm = reactive({
  amount: 0,
  description: 'Executive adjustment'
})

// Details View
const detailsDialogVisible = ref(false)
const userDetailsLoading = ref(false)
const userDetails = ref<any>({ user: {}, credit_history: [], visit_history: [], video_history: [], api_usage_chart: { dates: [], counts: [] } })
const chartRef = ref<HTMLElement | null>(null)
let myChart: any | null = null

const getList = async () => {
  listLoading.value = true
  try {
    const response = await api.get('adym/users/', {
      params: {
        page: listQuery.page,
        page_size: listQuery.limit,
        search: searchQuery.value,
        sort: sortOrder.value
      }
    })
    
    list.value = response.data.results
    total.value = response.data.count
  } catch (error) {
    console.error(error)
    ElMessage.error(t('common.error'))
  } finally {
    listLoading.value = false
  }
}

const handleFilter = () => {
  listQuery.page = 1
  getList()
}

const handleEditCredits = (row: any) => {
  temp.value = Object.assign({}, row)
  creditForm.amount = 0
  creditForm.description = 'Executive adjustment'
  dialogVisible.value = true
}

const updateData = async () => {
  try {
    await api.post(`adym/users/${temp.value.id}/credits/`, creditForm)
    dialogVisible.value = false
    ElMessage.success(t('common.success'))
    getList()
  } catch (error) {
    console.error(error)
    ElMessage.error(t('common.error'))
  }
}

const visitRange = ref('1')

const handleVisitRangeChange = () => {
    if (userDetails.value && userDetails.value.user && userDetails.value.user.id) {
        refreshDetails(userDetails.value.user.id)
    }
}

// Password Change
const passwordDialogVisible = ref(false)
const passwordForm = reactive({
    userId: 0,
    password: '',
    confirmPassword: ''
})

const handlePassword = (row: any) => {
    passwordForm.userId = row.id
    passwordForm.password = ''
    passwordForm.confirmPassword = ''
    passwordDialogVisible.value = true
}

const submitPasswordChange = async () => {
    if (!passwordForm.password || passwordForm.password.length < 6) {
        ElMessage.warning('Password must be at least 6 characters')
        return
    }
    if (passwordForm.password !== passwordForm.confirmPassword) {
        ElMessage.warning(t('auth.register.errorPasswordMismatch'))
        return
    }
    
    try {
        await api.post(`adym/users/${passwordForm.userId}/password/`, {
            password: passwordForm.password
        })
        ElMessage.success(t('common.success'))
        passwordDialogVisible.value = false
    } catch (e) {
        ElMessage.error(t('common.error'))
    }
}

const handleDelete = (row: any) => {
    ElMessageBox.confirm(
        'Are you sure you want to delete this user? This action cannot be undone.',
        'Attention',
        {
            confirmButtonText: t('common.confirm'),
            cancelButtonText: t('common.cancel'),
            type: 'warning',
            customClass: 'executive-message-box'
        }
    )
    .then(async () => {
         try {
            await api.delete(`adym/users/${row.id}/delete/`)
            ElMessage.success(t('common.success'))
            getList()
         } catch (e: any) {
            ElMessage.error(e.response?.data?.error || t('common.error'))
         }
    })
    .catch(() => {})
}

const handleViewDetails = async (row: any) => {
    detailsDialogVisible.value = true
    userDetailsLoading.value = true
    visitRange.value = '1'
    try {
        const response = await api.get(`adym/users/${row.id}/`, {
            params: { visit_days: visitRange.value }
        })
        userDetails.value = response.data
    } catch (error) {
        console.error(error)
        ElMessage.error('Failed to fetch details')
    } finally {
        userDetailsLoading.value = false
    }
}

const handleDetailsOpen = async () => {
    if (userDetailsLoading.value) return 
    startDetailsPolling()
    await nextTick()
    initDetailsChart()
}

const startDetailsPolling = () => {
    stopDetailsPolling()
    detailsTimer = setInterval(() => {
        if (userDetails.value && userDetails.value.user && userDetails.value.user.id) {
            refreshDetails(userDetails.value.user.id)
        }
    }, 5000)
}

const stopDetailsPolling = () => {
    if (detailsTimer) {
        clearInterval(detailsTimer)
        detailsTimer = null
    }
}

const refreshDetails = async (id: number) => {
    try {
        const response = await api.get(`adym/users/${id}/`, {
            params: { visit_days: visitRange.value }
        })
        userDetails.value = response.data
        if (myChart) {
             myChart.setOption({
                 xAxis: { data: userDetails.value.api_usage_chart.dates },
                 series: userDetails.value.api_usage_chart.series.map((s:any) => ({
                    name: s.name,
                    data: s.data
                }))
             })
        }
    } catch (e) {
        console.error("Silent refresh failed", e)
    }
}

let detailsTimer: any = null

const handleDialogClose = () => {
    stopDetailsPolling()
    if (myChart) {
        myChart.dispose()
        myChart = null
    }
}

const initDetailsChart = () => {
    if (!chartRef.value) return
    if (myChart) myChart.dispose()
    
    myChart = echarts.init(chartRef.value)
    
    // Theme Colors
    const teal = '#2A9D8F'
    const orange = '#E76F51'
    
    const option = {
        tooltip: { trigger: 'axis' },
        legend: { bottom: 0, textStyle: { color: '#64748b' } },
        xAxis: { type: 'category', data: userDetails.value.api_usage_chart.dates },
        yAxis: { type: 'value', splitLine: { lineStyle: { type: 'dashed' } } },
        series: userDetails.value.api_usage_chart.series.map((s:any, idx: number) => ({
            name: s.name,
            type: 'line',
            smooth: 0.3,
            showSymbol: false,
            lineStyle: { width: 3, color: idx === 0 ? teal : orange },
            data: s.data
        }))
    }
    
    myChart.setOption(option)
}

onMounted(() => {
  getList()
})
</script>

<style scoped>
.user-executive-view {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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

.action-btn {
  height: 48px;
  padding: 0 24px;
  border-radius: 14px;
  font-weight: 700;
  border: none;
  transition: all 0.3s;
}

.action-btn.gold {
  background: linear-gradient(135deg, var(--admin-accent-gold) 0%, #8e6e3c 100%);
  box-shadow: 0 8px 20px rgba(197, 160, 89, 0.2);
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
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

.executive-select {
  width: 200px;
}

.filter-btn {
  height: 44px;
  padding: 0 20px;
  border-radius: 12px;
  font-weight: 600;
  background: var(--admin-sidebar-bg);
  color: white;
  border: none;
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

.user-name {
  font-weight: 700;
  color: var(--admin-text-primary);
}

.user-email {
  color: var(--admin-text-secondary);
  font-size: 0.9rem;
}

.credit-badge {
  display: inline-block;
  padding: 6px 14px;
  background: rgba(42, 157, 143, 0.1);
  color: var(--admin-accent-teal);
  border-radius: 10px;
  font-weight: 800;
  font-family: var(--font-heading);
}

.credit-badge.low {
  background: rgba(231, 111, 81, 0.1);
  color: var(--admin-accent-orange);
}

.action-group {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.mini-btn {
  height: 32px;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 600;
  border: 1px solid var(--admin-border);
  background: white;
  transition: all 0.2s;
}

.mini-btn:hover { transform: translateY(-1px); }
.mini-btn.teal:hover { border-color: var(--admin-accent-teal); color: var(--admin-accent-teal); }
.mini-btn.navy:hover { border-color: var(--admin-sidebar-bg); color: var(--admin-sidebar-bg); }
.mini-btn.gold:hover { border-color: var(--admin-accent-gold); color: var(--admin-accent-gold); }
.mini-btn.danger:hover { background: #fee2e2; border-color: #ef4444; color: #ef4444; }

.pagination-area {
  padding: 24px 32px;
  background: white;
  display: flex;
  justify-content: flex-end;
}

/* Modal Redesign */
:deep(.executive-dialog), :deep(.executive-modal) {
  border-radius: 24px !important;
  box-shadow: var(--admin-shadow-hover) !important;
  overflow: hidden;
}

:deep(.el-dialog__header) {
  padding: 32px 40px 20px !important;
  border-bottom: 1px solid var(--admin-border);
}

:deep(.el-dialog__title) {
  font-weight: 800;
  color: var(--admin-text-primary);
  font-size: 1.25rem;
}

.dialog-content {
  padding: 24px 0;
}

.target-profile {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 32px;
  padding: 16px;
  background: var(--admin-surface-alt);
  border-radius: 16px;
}

.avatar-small {
  width: 44px;
  height: 44px;
  background: var(--admin-sidebar-bg);
  border-radius: 12px;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
}

.target-profile .name {
  display: block;
  font-weight: 700;
  font-size: 1rem;
}

.target-profile .sub {
  font-size: 0.8rem;
  color: var(--admin-text-secondary);
}

.executive-number {
  width: 100%;
}

:deep(.el-input-number__increase), :deep(.el-input-number__decrease) {
  background: var(--admin-surface-alt);
  border: none;
}

.form-tip {
  font-size: 0.75rem;
  color: var(--admin-text-secondary);
  margin-top: 8px;
}

.dialog-footer {
  display: flex;
  gap: 12px;
}

.cancel-btn {
  flex: 1;
  height: 50px;
  border-radius: 14px;
}

.confirm-btn {
  flex: 2;
  height: 50px;
  border-radius: 14px;
  font-weight: 700;
}

/* User Details Refinement */
.profile-summary {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 32px;
  margin-bottom: 32px;
}

.avatar-large {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, var(--admin-sidebar-bg) 0%, #334155 100%);
  border-radius: 24px;
  color: white;
  font-size: 1.8rem;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
}

.p-details .p-name {
  font-size: 1.6rem;
  margin: 0;
}

.executive-tabs {
  padding: 0 32px 32px;
}

:deep(.el-tabs__item) {
  font-weight: 700;
  font-size: 1rem;
  height: 50px !important;
}

:deep(.el-tabs__active-bar) {
  background-color: var(--admin-accent-gold);
}

.section-title {
  font-size: 1.1rem;
  margin-bottom: 24px;
}

.mini-chart {
  height: 350px;
  width: 100%;
}

.nested-table {
  border: 1px solid var(--admin-border);
  border-radius: 16px;
  overflow: hidden;
}

.text-teal { color: var(--admin-accent-teal); font-weight: 700; }
.text-danger { color: var(--admin-accent-orange); font-weight: 700; }
</style>
