<template>
  <div class="faq-executive-view animate-page-fade">
    <div class="page-header">
      <div class="header-info">
        <h2 class="view-title">{{ t('admin.faqs') }}</h2>
        <p class="view-subtitle">集中管理平台 F.A.Q. 库，支持中英双语实时同步</p>
      </div>
      <el-button class="action-btn gold" type="primary" :icon="Plus" @click="handleAdd">
        新增知识条目
      </el-button>
    </div>

    <!-- Table Section -->
    <div class="table-container glass-card">
      <el-table 
        v-loading="loading"
        :data="faqs" 
        class="executive-table"
        row-class-name="executive-row"
      >
        <el-table-column prop="order" label="排序权重" width="100" align="center">
          <template #default="{ row }">
            <span class="order-badge">{{ row.order }}</span>
          </template>
        </el-table-column>
        
        <el-table-column label="问答内容 (ZH/EN)" min-width="400">
          <template #default="{ row }">
            <div class="content-cell">
              <div class="q-row">
                <el-tag size="small" effect="plain" class="lang-tag">ZH</el-tag>
                <span class="q-text">{{ row.question_zh }}</span>
              </div>
              <div class="q-row mt-1">
                <el-tag size="small" type="info" effect="plain" class="lang-tag">EN</el-tag>
                <span class="q-text en-text">{{ row.question_en }}</span>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="状态" width="120" align="center">
          <template #default="{ row }">
            <div class="status-wrapper">
              <span class="status-dot" :class="{ active: row.is_active }"></span>
              <span class="status-text">{{ row.is_active ? '已发布' : '草稿' }}</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="更新时间" width="180" align="center">
          <template #default="{ row }">
            <span class="time-text">{{ formatDate(row.updated_at) }}</span>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="160" align="right" fixed="right">
          <template #default="{ row }">
            <div class="action-btns">
              <el-tooltip content="编辑条目" placement="top">
                <button class="mini-tool-btn edit" @click="handleEdit(row)">
                  <el-icon><Edit /></el-icon>
                </button>
              </el-tooltip>
              
              <el-popconfirm title="确定要永久删除此条目吗？" @confirm="handleDelete(row.id)">
                <template #reference>
                  <span>
                    <el-tooltip content="删除条目" placement="top">
                      <button class="mini-tool-btn delete">
                        <el-icon><Delete /></el-icon>
                      </button>
                    </el-tooltip>
                  </span>
                </template>
              </el-popconfirm>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- FAQ Dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="editingFaq ? '编辑知识条目' : '创建新知识条目'"
      width="600px"
      custom-class="executive-dialog"
      destroy-on-close
    >
      <div class="dialog-content">
        <div class="section-divider">基础信息</div>
        <el-form :model="form" label-position="top" class="executive-form">
          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="排序权重 (越小越靠前)">
                <el-input-number v-model="form.order" :min="0" class="w-full executive-number" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="发布状态">
                <el-radio-group v-model="form.is_active" class="executive-radio-group">
                  <el-radio-button :label="true">立即发布</el-radio-button>
                  <el-radio-button :label="false">暂存草稿</el-radio-button>
                </el-radio-group>
              </el-form-item>
            </el-col>
          </el-row>

          <div class="section-divider">中文内容 (ZH)</div>
          <el-form-item label="问题文本">
            <el-input v-model="form.question_zh" placeholder="请输入中文问题摘要..." class="executive-input" />
          </el-form-item>
          <el-form-item label="详细解答">
            <el-input 
              v-model="form.answer_zh" 
              type="textarea" 
              :rows="4" 
              placeholder="请输入详细的中文解答..."
              class="executive-textarea"
            />
          </el-form-item>

          <div class="section-divider">英文内容 (EN)</div>
          <el-form-item label="Question Summary">
            <el-input v-model="form.question_en" placeholder="Enter English question summary..." class="executive-input" />
          </el-form-item>
          <el-form-item label="Detailed Response">
            <el-input 
              v-model="form.answer_en" 
              type="textarea" 
              :rows="4" 
              placeholder="Enter detailed English response..."
              class="executive-textarea"
            />
          </el-form-item>
        </el-form>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false" class="cancel-btn">取消</el-button>
          <el-button type="primary" @click="handleSave" :loading="saving" class="confirm-btn gold">
            提交并保存
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Plus, Edit, Delete } from '@element-plus/icons-vue'
import api from '@/utils/api'
import { ElMessage } from 'element-plus'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const faqs = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const editingFaq = ref<any>(null)
const saving = ref(false)

const form = ref({
  question_zh: '',
  question_en: '',
  answer_zh: '',
  answer_en: '',
  order: 0,
  is_active: true
})

const fetchFaqs = async () => {
  loading.value = true
  try {
    const response = await api.get('adym/faqs/')
    faqs.value = response.data
  } catch (e) {
    ElMessage.error('无法同步知识库数据')
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  editingFaq.value = null
  form.value = {
    question_zh: '',
    question_en: '',
    answer_zh: '',
    answer_en: '',
    order: 0,
    is_active: true
  }
  dialogVisible.value = true
}

const handleEdit = (faq: any) => {
  editingFaq.value = faq
  form.value = { ...faq }
  dialogVisible.value = true
}

const handleSave = async () => {
  if (!form.value.question_zh || !form.value.answer_zh) {
    return ElMessage.warning('请至少完善中文内容')
  }
  
  saving.value = true
  try {
    if (editingFaq.value) {
      await api.patch(`adym/faqs/${editingFaq.value.id}/`, form.value)
      ElMessage.success('条目更新已生效')
    } else {
      await api.post('adym/faqs/', form.value)
      ElMessage.success('新条目已成功入库')
    }
    dialogVisible.value = false
    fetchFaqs()
  } catch (e) {
    ElMessage.error('条目存档失败，请检查网络')
  } finally {
    saving.value = false
  }
}

const handleDelete = async (id: number) => {
  try {
    await api.delete(`adym/faqs/${id}/`)
    ElMessage.success('条目已从物理库移除')
    fetchFaqs()
  } catch (e) {
    ElMessage.error('移除操作失败')
  }
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  return d.toLocaleString('zh-CN', { 
    year: 'numeric', month: '2-digit', day: '2-digit', 
    hour: '2-digit', minute: '2-digit' 
  })
}

onMounted(fetchFaqs)
</script>

<style scoped>
.faq-executive-view {
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

.order-badge {
  display: inline-block;
  padding: 4px 12px;
  background: rgba(197, 160, 89, 0.1);
  color: var(--admin-accent-gold);
  border-radius: 8px;
  font-weight: 800;
  font-family: var(--font-heading);
}

.content-cell {
  padding: 8px 0;
}

.q-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.q-text {
  font-weight: 700;
  color: var(--admin-text-primary);
}

.en-text {
  color: var(--admin-text-secondary);
  font-weight: 500;
  font-size: 0.9rem;
}

.status-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #cbd5e1;
}

.status-dot.active {
  background: var(--admin-accent-teal);
  box-shadow: 0 0 8px rgba(42, 157, 143, 0.4);
}

.status-text {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--admin-text-primary);
}

.time-text {
  font-size: 0.85rem;
  color: var(--admin-text-secondary);
}

.action-btns {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.mini-tool-btn {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border: 1px solid var(--admin-border);
  color: var(--admin-text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.mini-tool-btn:hover {
  transform: translateY(-1px);
  border-color: var(--admin-accent-teal);
  color: var(--admin-accent-teal);
}

.mini-tool-btn.delete:hover {
  border-color: var(--admin-accent-orange);
  color: var(--admin-accent-orange);
  background: #fff1f2;
}

/* Dialog Redesign */
:deep(.executive-dialog) {
  border-radius: 24px !important;
  box-shadow: var(--admin-shadow-hover) !important;
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

.section-divider {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--admin-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin: 32px 0 16px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.section-divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--admin-border);
}

:deep(.el-form-item__label) {
  color: var(--admin-text-primary) !important;
  font-weight: 700 !important;
}

.executive-input :deep(.el-input__wrapper), 
.executive-textarea :deep(.el-textarea__inner) {
  background: var(--admin-surface-alt);
  border-color: var(--admin-border);
  border-radius: 12px;
}

.executive-number {
  width: 100%;
}

.executive-radio-group :deep(.el-radio-button__inner) {
  background: var(--admin-surface-alt);
  border-color: var(--admin-border);
}

.executive-radio-group :deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
  background: var(--admin-sidebar-bg);
  color: white;
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

.confirm-btn.gold {
  background: linear-gradient(135deg, var(--admin-accent-gold) 0%, #8e6e3c 100%);
  border: none;
  color: white;
}

.w-full { width: 100%; }
.mt-1 { margin-top: 4px; }
</style>
