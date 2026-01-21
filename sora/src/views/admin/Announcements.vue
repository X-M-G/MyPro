<template>
  <div class="announcements-container">
    <div class="header">
        <h3>{{ $t('admin.announcements') }}</h3>
        <el-button type="primary" :icon="Plus" @click="handleCreate">
            {{ $t('admin.create') }}
        </el-button>
    </div>

    <el-table :data="list" border style="width: 100%; margin-top: 20px;">
        <el-table-column prop="id" label="ID" width="80" align="center" />
        <el-table-column prop="title" :label="$t('admin.title')" />
        <el-table-column prop="is_active" :label="$t('admin.active')" width="100" align="center">
            <template #default="{ row }">
                <el-switch v-model="row.is_active" @change="handleStatusChange(row)" />
            </template>
        </el-table-column>
        <el-table-column prop="created_at" :label="$t('admin.createdAt')" width="180">
            <template #default="{ row }">
                {{ new Date(row.created_at).toLocaleDateString() }}
            </template>
        </el-table-column>
        <el-table-column :label="$t('common.actions')" width="180" align="center">
            <template #default="{ row }">
                <el-button size="small" @click="handleEdit(row)">{{ $t('common.edit') }}</el-button>
                <el-button size="small" type="danger" @click="handleDelete(row)">{{ $t('common.delete') }}</el-button>
            </template>
        </el-table-column>
    </el-table>

    <!-- Dialog -->
    <el-dialog :title="dialogStatus === 'create' ? $t('admin.createAnnouncement') : $t('admin.editAnnouncement')" v-model="dialogVisible" width="500px">
        <el-form :model="temp" label-position="top">
            <el-form-item :label="$t('admin.title')">
                <el-input v-model="temp.title" />
            </el-form-item>
            <el-form-item :label="$t('admin.content')">
                <el-input v-model="temp.content" type="textarea" :rows="4" />
            </el-form-item>
            <el-form-item :label="$t('admin.active')">
                <el-switch v-model="temp.is_active" />
            </el-form-item>
        </el-form>
        <template #footer>
            <span class="dialog-footer">
                <el-button @click="dialogVisible = false">{{ $t('common.cancel') }}</el-button>
                <el-button type="primary" @click="submitData">{{ $t('common.confirm') }}</el-button>
            </span>
        </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import api from '@/utils/api'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const list = ref([])
const dialogVisible = ref(false)
const dialogStatus = ref('create')
const temp = reactive({
    id: undefined,
    title: '',
    content: '',
    is_active: true
})

const getList = async () => {
    try {
        const response = await api.get('adym/announcements/')
        list.value = response.data
    } catch (e) {
        ElMessage.error(t('common.error'))
    }
}

const handleCreate = () => {
    dialogStatus.value = 'create'
    temp.id = undefined
    temp.title = ''
    temp.content = ''
    temp.is_active = true
    dialogVisible.value = true
}

const handleEdit = (row: any) => {
    dialogStatus.value = 'update'
    temp.id = row.id
    temp.title = row.title
    temp.content = row.content
    temp.is_active = row.is_active
    dialogVisible.value = true
}

const submitData = async () => {
    if (!temp.title || !temp.content) {
        ElMessage.warning(t('admin.titleAndContentRequired') || 'Title and content required')
        return
    }
    try {
        if (dialogStatus.value === 'create') {
            await api.post('adym/announcements/', temp)
        } else {
            await api.patch(`adym/announcements/${temp.id}/`, temp)
        }
        ElMessage.success(t('common.success'))
        dialogVisible.value = false
        getList()
    } catch (e) {
        ElMessage.error(t('common.error'))
    }
}

const handleStatusChange = async (row: any) => {
    try {
        await api.patch(`adym/announcements/${row.id}/`, { is_active: row.is_active })
        ElMessage.success(t('common.success'))
    } catch (e) {
         row.is_active = !row.is_active // revert
         ElMessage.error(t('common.error'))
    }
}

const handleDelete = (row: any) => {
    ElMessageBox.confirm(t('common.confirmDelete') || 'Are you sure?', 'Warning', { type: 'warning' })
    .then(async () => {
        await api.delete(`adym/announcements/${row.id}/`)
        ElMessage.success(t('common.success'))
        getList()
    })
    .catch(() => {})
}

onMounted(() => {
    getList()
})
</script>

<style scoped>
.announcements-container {
    padding: 20px;
}
.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}
</style>
