<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :lg="6" v-for="stat in stats" :key="stat.title">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <el-icon :size="40" :color="stat.color">
              <component :is="stat.icon" />
            </el-icon>
            <div class="stat-info">
              <div class="stat-value" :style="{ color: stat.color }">{{ stat.value }}</div>
              <div class="stat-title">{{ stat.title }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 最近借阅 -->
    <el-card class="recent-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span><el-icon><Timer /></el-icon> 最近借阅记录</span>
          <el-button text type="primary" @click="$router.push('/borrows')">
            查看全部 <el-icon><ArrowRight /></el-icon>
          </el-button>
        </div>
      </template>

      <el-table :data="recentBorrows" v-loading="loading" stripe>
        <el-table-column prop="book_title" label="图书" min-width="150" />
        <el-table-column prop="user_name" label="借阅人" width="120" />
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
      </el-table>

      <el-empty v-if="!loading && recentBorrows.length === 0" description="暂无借阅记录" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getAllBorrows, getBorrowStatistics } from '@/api/borrow'
import { getBooks } from '@/api/book'
import { formatDate, getStatusType, getStatusLabel } from '@/utils/format'
import { Reading, Handbag, Warning, Coin, Timer, ArrowRight } from '@element-plus/icons-vue'

const loading = ref(false)
const stats = ref([
  { title: '图书总数', value: 0, icon: 'Reading', color: '#3b82f6' },
  { title: '当前借阅', value: 0, icon: 'Handbag', color: '#10b981' },
  { title: '逾期数量', value: 0, icon: 'Warning', color: '#f59e0b' },
  { title: '累计罚款', value: '¥0.00', icon: 'Coin', color: '#ef4444' }
])
const recentBorrows = ref([])

async function loadData() {
  loading.value = true
  try {
    const [books, statistics, borrows] = await Promise.all([
      // getBooks({ limit: 1 }),
        getBooks(),
      getBorrowStatistics(),
      getAllBorrows({ limit: 5 })
    ])

    stats.value[0].value = books?.length || 0
    stats.value[1].value = statistics?.active_borrows || 0
    stats.value[2].value = statistics?.overdue_count || 0
    stats.value[3].value = '¥' + ((statistics?.total_fines || 0) / 100).toFixed(2)

    recentBorrows.value = borrows || []
  } finally {
    loading.value = false
  }
}

onMounted(loadData)
</script>

<style scoped lang="scss">
.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  margin-bottom: 20px;

  :deep(.el-card__body) {
    padding: 20px;
  }
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  line-height: 1.2;
}

.stat-title {
  font-size: 14px;
  color: #64748b;
  margin-top: 4px;
}

.recent-card {
  :deep(.el-card__header) {
    padding: 16px 20px;
  }
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-weight: 600;

  .el-icon {
    margin-right: 6px;
    vertical-align: middle;
  }
}
</style>
