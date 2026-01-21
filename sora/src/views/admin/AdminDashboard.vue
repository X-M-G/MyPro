<template>
  <div class="admin-dashboard-view animate-page-fade">
    <div class="dashboard-header">
      <h2 class="welcome-text">{{ $t('admin.executiveInsight') }}</h2>
      <p class="welcome-sub">{{ $t('admin.executiveInsightSub') }}</p>
    </div>

    <div class="glass-card provider-control-card animate-page-fade">
      <div class="control-header">
        <div class="control-info">
          <h3 class="control-title">Sora2 API 线路选择</h3>
          <p class="control-desc">灵活切换 API 提供商，确保高可用性</p>
        </div>
        <div class="control-actions">
          <el-radio-group v-model="selectedProvider" @change="handleProviderChange" :disabled="loadingProvider" class="premium-radio-group">
            <el-radio-button value="marketai">MarketAI (新线路)</el-radio-button>
            <el-radio-button value="grsai">GRSAI (备选线路)</el-radio-button>
          </el-radio-group>
        </div>
      </div>
    </div>


    <el-row :gutter="32" class="stats-row">
      <el-col :span="6">
        <div class="kpi-card-premium">
          <div class="kpi-icon gold"><User /></div>
          <div class="kpi-data">
            <span class="kpi-label">{{ $t('admin.totalUsers') }}</span>
            <div class="kpi-value">{{ stats.kpi.total_users.toLocaleString() }}</div>
          </div>
          <div class="kpi-trend positive">+2.4%</div>
        </div>
      </el-col>
      
      <el-col :span="6">
        <div class="kpi-card-premium">
          <div class="kpi-icon teal"><View /></div>
          <div class="kpi-data">
            <span class="kpi-label">{{ $t('admin.todayPresence') }}</span>
            <div class="kpi-value">{{ stats.kpi.today_visits.toLocaleString() }}</div>
            <div class="kpi-sub">{{ stats.kpi.total_visits.toLocaleString() }} {{ $t('admin.total') }}</div>
          </div>
        </div>
      </el-col>

      <el-col :span="6">
        <div class="kpi-card-premium">
          <div class="kpi-icon orange"><VideoCamera /></div>
          <div class="kpi-data">
            <span class="kpi-label">{{ $t('admin.videoAssets') }}</span>
            <div class="kpi-value">{{ stats.kpi.today_video.toLocaleString() }}</div>
            <div class="kpi-sub">{{ stats.kpi.total_video.toLocaleString() }} {{ $t('admin.total') }}</div>
          </div>
        </div>
      </el-col>

      <el-col :span="6">
        <div class="kpi-card-premium">
          <div class="kpi-icon navy"><EditPen /></div>
          <div class="kpi-data">
            <span class="kpi-label">{{ $t('admin.semanticGeneration') }}</span>
            <div class="kpi-value">{{ stats.kpi.today_prompt.toLocaleString() }}</div>
            <div class="kpi-sub">{{ stats.kpi.total_prompt.toLocaleString() }} {{ $t('admin.total') }}</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="32" class="stats-row secondary">
      <el-col :span="12">
        <div class="kpi-card-premium detailed">
          <div class="kpi-icon light-orange"><VideoCamera /></div>
          <div class="kpi-data flex-row">
            <div class="kpi-main">
              <span class="kpi-label">{{ $t('admin.videoStatsSora') }}</span>
              <div class="kpi-value">{{ stats.kpi.video_detail.sora.TOTAL }}</div>
            </div>
            <div class="kpi-split">
              <div class="split-item success">
                <span class="split-label">{{ $t('admin.success') }}</span>
                <span class="split-value">{{ stats.kpi.video_detail.sora.SUCCESS }}</span>
              </div>
              <div class="divider"></div>
              <div class="split-item failed">
                <span class="split-label">{{ $t('admin.failed') }}</span>
                <span class="split-value">{{ stats.kpi.video_detail.sora.FAILED }}</span>
              </div>
            </div>
          </div>
        </div>
      </el-col>

      <el-col :span="12">
        <div class="kpi-card-premium detailed">
          <div class="kpi-icon gold"><VideoCamera /></div>
          <div class="kpi-data flex-row">
            <div class="kpi-main">
              <span class="kpi-label">{{ $t('admin.videoStatsSoraPro') }}</span>
              <div class="kpi-value">{{ stats.kpi.video_detail['sora2-pro']?.TOTAL || 0 }}</div>
            </div>
            <div class="kpi-split">
              <div class="split-item success">
                <span class="split-label">{{ $t('admin.success') }}</span>
                <span class="split-value">{{ stats.kpi.video_detail['sora2-pro']?.SUCCESS || 0 }}</span>
              </div>
              <div class="divider"></div>
              <div class="split-item failed">
                <span class="split-label">{{ $t('admin.failed') }}</span>
                <span class="split-value">{{ stats.kpi.video_detail['sora2-pro']?.FAILED || 0 }}</span>
              </div>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <div class="main-chart-area glass-card">
      <div class="chart-header">
        <div class="chart-info">
          <h3 class="chart-title">{{ $t('admin.apiTrend') }}</h3>
          <span class="chart-subtitle">{{ $t('admin.apiTrendSub') }}</span>
        </div>
        <el-radio-group v-model="timeRange" size="small" class="executive-radio" @change="handleRangeChange">
          <el-radio-button value="today">{{ $t('admin.intraday') }}</el-radio-button>
          <el-radio-button value="30d">{{ $t('admin.operationalCycle') }}</el-radio-button>
        </el-radio-group>
      </div>
      <div ref="chartRef" class="chart-canvas"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import api from '@/utils/api'
import * as echarts from 'echarts'
import { User, View, VideoCamera, EditPen } from '@element-plus/icons-vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'


const { t } = useI18n()
const timeRange = ref('30d')
const selectedProvider = ref('marketai')
const loadingProvider = ref(false)
const chartRef = ref<HTMLElement | null>(null)

const stats = ref({
  kpi: {
      total_users: 0,
      today_visits: 0,
      total_visits: 0,
      today_video: 0,
      total_video: 0,
      today_prompt: 0,
      total_prompt: 0,
      video_detail: {
        sora: { SUCCESS: 0, FAILED: 0, TOTAL: 0 },
        'sora2-pro': { SUCCESS: 0, FAILED: 0, TOTAL: 0 }
      }
  },
  chart_data: {
      dates: [],
      series: []
  }
})

let chartInstance: ReturnType<typeof echarts.init> | null = null
let resizeObserver: ResizeObserver | null = null

const fetchStats = async () => {
  try {
    const response = await api.get('adym/dashboard/stats/', {
      params: { range: timeRange.value }
    })
    
    stats.value = response.data
    // 如果实例已存在，直接更新数据，否则等待容器就绪初始化
    if (chartInstance && chartRef.value?.clientWidth) {
      updateChart(response.data.chart_data)
    } else {
      await nextTick()
      initChart(response.data.chart_data)
    }
  } catch (error) {
    console.error('Failed to fetch stats:', error)
  }
}

const handleRangeChange = () => {
    fetchStats()
}

const fetchProvider = async () => {
  try {
    const response = await api.get('adym/settings/sora-provider/')
    selectedProvider.value = response.data.provider
  } catch (error) {
    console.error('Failed to fetch provider:', error)
  }
}

const handleProviderChange = async (val: string) => {
  loadingProvider.value = true
  try {
    await api.post('adym/settings/sora-provider/update/', { provider: val })
    ElMessage.success({
      message: `已切换至 ${val === 'marketai' ? 'MarketAI' : 'GRSAI'} 线路`,
      plain: true
    })
  } catch (error) {
    console.error('Failed to update provider:', error)
    ElMessage.error('切换线路失败')
    await fetchProvider()
  } finally {
    loadingProvider.value = false
  }
}

// 提取配置生成逻辑
const getOption = (chartData: any) => {
  const colors = [
      { start: 'rgba(42, 157, 143, 0.4)', end: 'rgba(42, 157, 143, 0.01)', line: '#2A9D8F' }, 
      { start: 'rgba(231, 111, 81, 0.4)', end: 'rgba(231, 111, 81, 0.01)', line: '#E76F51' }, 
      { start: 'rgba(30, 41, 59, 0.4)', end: 'rgba(30, 41, 59, 0.01)', line: '#1E293B' }
  ]

  return {
    tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'cross' },
        backgroundColor: 'rgba(255, 255, 255, 0.95)',
        borderColor: '#eee',
        borderWidth: 1,
        textStyle: { color: '#1e293b', fontSize: 12 }
    },
    legend: {
        data: chartData.series.map((s: any) => s.name),
        bottom: 20,
        textStyle: { color: '#64748b', fontWeight: 600 }
    },
    grid: { left: '4%', right: '4%', top: '10%', bottom: '15%', containLabel: true },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: chartData.dates,
      axisLine: { lineStyle: { color: '#e2e8f0' } },
      axisLabel: { color: '#94a3b8', fontSize: 11, fontWeight: 500 }
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: '#f1f5f9', type: 'dashed' } },
      axisLabel: { color: '#94a3b8' }
    },
    series: chartData.series.map((s: any, index: number) => {
        const color = colors[index % colors.length]
        return {
            name: s.name,
            type: 'line',
            smooth: 0.4,
            symbol: 'circle',
            symbolSize: 8,
            showSymbol: false,
            lineStyle: { width: 4, color: color.line },
            itemStyle: { color: color.line, borderColor: '#fff', borderWidth: 3 },
            areaStyle: {
                opacity: 0.9,
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                    { offset: 0, color: color.start },
                    { offset: 1, color: color.end }
                ])
            },
            data: s.data
        }
    })
  }
}

const updateChart = (chartData: any) => {
  if (chartInstance) {
    chartInstance.setOption(getOption(chartData))
  }
}

const initChart = (chartData: any) => {
  const chartDom = chartRef.value
  if (!chartDom || chartDom.clientWidth === 0) return

  if (chartInstance) chartInstance.dispose()
  
  chartInstance = echarts.init(chartDom)
  chartInstance.setOption(getOption(chartData))
}

onMounted(() => {
  fetchStats()
  fetchProvider()

  // 使用 ResizeObserver 监听容器大小
  // 这能完美解决页面淡入动画导致的 0 尺寸问题
  if (chartRef.value) {
    resizeObserver = new ResizeObserver((entries) => {
      for (let entry of entries) {
        const { width, height } = entry.contentRect
        if (width > 0 && height > 0) {
          if (!chartInstance) {
            // 只有当容器有大小时才进行初始化
            initChart(stats.value.chart_data)
          } else {
            chartInstance.resize()
          }
        }
      }
    })
    resizeObserver.observe(chartRef.value)
  }
})

onUnmounted(() => {
  if (resizeObserver) {
    resizeObserver.disconnect()
    resizeObserver = null
  }
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
})
</script>

<style scoped>
.admin-dashboard-view {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.provider-control-card {
  padding: 24px 32px;
  border-radius: 20px;
}

.control-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.control-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--admin-text-primary);
  margin-bottom: 4px;
}

.control-desc {
  font-size: 0.85rem;
  color: var(--admin-text-secondary);
}

:deep(.premium-radio-group .el-radio-button__inner) {
  padding: 12px 24px;
  font-weight: 600;
  background: var(--admin-surface-alt);
  border-color: var(--admin-border);
  color: var(--admin-text-secondary);
  transition: all 0.3s ease;
}

:deep(.premium-radio-group .el-radio-button__original-radio:checked + .el-radio-button__inner) {
  background: var(--admin-sidebar-bg);
  border-color: var(--admin-sidebar-bg);
  color: white;
  box-shadow: 0 4px 12px rgba(30, 41, 59, 0.2);
}


.dashboard-header {
  margin-bottom: 8px;
}

.welcome-text {
  font-size: 1.8rem;
  color: var(--admin-text-primary);
  font-weight: 800;
  letter-spacing: -0.02em;
}

.welcome-sub {
  color: var(--admin-text-secondary);
  font-size: 0.95rem;
  margin-top: 4px;
}

.stats-row {
  margin-bottom: 8px;
}

.kpi-card-premium {
  padding: 24px;
  background: white;
  border-radius: 20px;
  border: 1px solid var(--admin-border);
  display: flex;
  align-items: center;
  gap: 20px;
  position: relative;
  transition: all 0.4s cubic-bezier(0.23, 1, 0.32, 1);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);
}

.kpi-card-premium:hover {
  transform: translateY(-5px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.05);
  border-color: var(--admin-accent-gold);
}

.kpi-icon {
  width: 54px;
  height: 54px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  flex-shrink: 0;
}

.kpi-icon.gold { background: rgba(197, 160, 89, 0.1); color: var(--admin-accent-gold); }
.kpi-icon.teal { background: rgba(42, 157, 143, 0.1); color: var(--admin-accent-teal); }
.kpi-icon.orange { background: rgba(231, 111, 81, 0.1); color: var(--admin-accent-orange); }
.kpi-icon.light-orange { background: rgba(244, 162, 97, 0.1); color: #F4A261; }
.kpi-icon.navy { background: rgba(30, 41, 59, 0.1); color: var(--admin-sidebar-bg); }

.kpi-data {
  flex: 1;
}

.kpi-label {
  display: block;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-weight: 700;
  color: var(--admin-text-secondary);
  margin-bottom: 4px;
}

.kpi-value {
  font-size: 1.6rem;
  font-weight: 800;
  color: var(--admin-text-primary);
  line-height: 1.1;
  font-family: var(--font-heading);
}

.kpi-sub {
  font-size: 0.75rem;
  color: var(--admin-text-secondary);
  margin-top: 4px;
  font-weight: 500;
}

.kpi-data.flex-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.kpi-split {
  display: flex;
  gap: 16px;
  align-items: center;
  background: var(--admin-surface-alt);
  padding: 8px 16px;
  border-radius: 12px;
}

.split-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.split-label {
  font-size: 0.65rem;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--admin-text-secondary);
}

.split-value {
  font-size: 1rem;
  font-weight: 800;
}

.split-item.success .split-value { color: var(--admin-accent-teal); }
.split-item.failed .split-value { color: var(--admin-accent-orange); }

.divider {
  width: 1px;
  height: 24px;
  background: var(--admin-border);
}

.stats-row.secondary {
  margin-top: -8px;
}

.kpi-trend {
  position: absolute;
  top: 16px;
  right: 16px;
  font-size: 0.7rem;
  font-weight: 700;
  padding: 4px 8px;
  border-radius: 8px;
}

.kpi-trend.positive {
  background: rgba(42, 157, 143, 0.1);
  color: var(--admin-accent-teal);
}

.main-chart-area {
  padding: 32px;
  border-radius: 24px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 40px;
}

.chart-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--admin-text-primary);
  margin-bottom: 4px;
}

.chart-subtitle {
  font-size: 0.85rem;
  color: var(--admin-text-secondary);
}

.chart-canvas {
  width: 100%;
  height: 440px;
}

:deep(.executive-radio .el-radio-button__inner) {
  background: var(--admin-surface-alt);
  border: 1px solid var(--admin-border);
  color: var(--admin-text-secondary);
  font-weight: 600;
  padding: 10px 20px;
}

:deep(.executive-radio .el-radio-button__original-radio:checked + .el-radio-button__inner) {
  background: var(--admin-sidebar-bg);
  border-color: var(--admin-sidebar-bg);
  color: white;
  box-shadow: none;
}
</style>