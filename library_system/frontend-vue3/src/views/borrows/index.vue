<template>
  <div class="borrows-page">
    <el-card shadow="never" class="toolbar-card">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="我的借阅" name="my">
          <el-table :data="myBorrows" v-loading="loading" stripe>
            <el-table-column prop="book_title" label="图书" min-width="150" show-overflow-tooltip />
            <el-table-column prop="book_author" label="作者" width="120" />
            <el-table-column prop="borrow_date" label="借阅日期" width="120">
              <template #default="{ row }">{{ formatDate(row.borrow_date) }}</template>
            </el-table-column>
            <el-table-column prop="due_date" label="应还日期" width="120">
              <template #default="{ row }">
                <span :class="{ 'text-danger': row.status === 'overdue' }">
                  {{ formatDate(row.due_date) }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)" size="small">
                  {{ getStatusLabel(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="fine_amount" label="罚款" width="100">
              <template #default="{ row }">
                <span :class="{ 'text-danger': row.fine_amount > 0 }">
                  {{ formatMoney(row.fine_amount) }}
                </span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="180" fixed="right">
              <template #default="{ row }">
                <el-button
                  v-if="canReturn(row)"
                  type="success"
                  size="small"
                  :icon="RefreshLeft"
                  @click="handleReturn(row)"
                >归还</el-button>
                <el-button
                  v-if="canRenew(row)"
                  type="warning"
                  size="small"
                  :icon="Refresh"
                  @click="handleRenew(row)"
                >续借</el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="!loading && myBorrows.length === 0" description="暂无借阅记录" />
        </el-tab-pane>

        <el-tab-pane label="全部记录" name="all" v-if="userStore.isAdminOrLibrarian">
          <div class="toolbar">
            <el-button type="primary" :icon="Refresh" @click="handleCheckOverdue">
              检查逾期
            </el-button>
          </div>
          <el-table :data="allBorrows" v-loading="loadingAll" stripe>
            <el-table-column prop="user_name" label="借阅人" width="120" />
            <el-table-column prop="book_title" label="图书" min-width="150" show-overflow-tooltip />
            <el-table-column prop="borrow_date" label="借阅日期" width="120">
              <template #default="{ row }">{{ formatDate(row.borrow_date) }}</template>
            </el-table-column>
            <el-table-column prop="due_date" label="应还日期" width="120">
              <template #default="{ row }">{{ formatDate(row.due_date) }}</template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)" size="small">
                  {{ getStatusLabel(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="fine_amount" label="罚款" width="100">
              <template #default="{ row }">{{ formatMoney(row.fine_amount) }}</template>
            </el-table-column>
            <el-table-column label="操作" width="100" fixed="right">
              <template #default="{ row }">
                <el-button
                  v-if="row.status !== 'returned'"
                  type="success"
                  size="small"
                  @click="handleReturn(row)"
                >归还</el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="!loadingAll && allBorrows.length === 0" description="暂无借阅记录" />
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import {
  getMyBorrows, getAllBorrows, returnBook, renewBook, checkOverdue
} from '@/api/borrow'
import { formatDate, formatMoney, getStatusType, getStatusLabel } from '@/utils/format'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, RefreshLeft } from '@element-plus/icons-vue'

const userStore = useUserStore()
const activeTab = ref('my')
const loading = ref(false)
const loadingAll = ref(false)
const myBorrows = ref([])
const allBorrows = ref([])

function canReturn(row) {
  return ['borrowed', 'renewed', 'overdue'].includes(row.status)
}

function canRenew(row) {
  return ['borrowed', 'renewed'].includes(row.status) &&
         row.renew_count < 2 &&
         row.status !== 'overdue'
}

async function loadMyBorrows() {
  loading.value = true
  try {
    myBorrows.value = await getMyBorrows() || []
  } finally {
    loading.value = false
  }
}

async function loadAllBorrows() {
  loadingAll.value = true
  try {
    allBorrows.value = await getAllBorrows({ limit: 50 }) || []
  } finally {
    loadingAll.value = false
  }
}

async function handleReturn(row) {
  try {
    await ElMessageBox.confirm(`确定要归还《${row.book_title}》吗？`, '提示')
    await returnBook({ record_id: row.id })
    ElMessage.success('归还成功')
    loadMyBorrows()
    if (userStore.isAdminOrLibrarian) loadAllBorrows()
  } catch {
    // 取消
  }
}

async function handleRenew(row) {
  try {
    await ElMessageBox.confirm(`确定要续借《${row.book_title}》15天吗？`, '提示')
    await renewBook({ record_id: row.id, days: 15 })
    ElMessage.success('续借成功')
    loadMyBorrows()
  } catch {
    // 取消
  }
}

async function handleCheckOverdue() {
  loadingAll.value = true
  try {
    const res = await checkOverdue()
    ElMessage.success(res.message)
    loadAllBorrows()
  } finally {
    loadingAll.value = false
  }
}

onMounted(() => {
  loadMyBorrows()
  if (userStore.isAdminOrLibrarian) loadAllBorrows()
})
</script>

<style scoped lang="scss">
.toolbar-card {
  :deep(.el-card__body) {
    padding: 0;
  }

  :deep(.el-tabs__header) {
    padding: 0 20px;
    margin-bottom: 0;
  }

  :deep(.el-tabs__content) {
    padding: 20px;
  }
}

.toolbar {
  margin-bottom: 16px;
}

.text-danger {
  color: #f56c6c;
}
</style>
