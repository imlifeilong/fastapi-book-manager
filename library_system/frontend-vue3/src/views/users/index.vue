<template>
  <div class="users-page">
    <el-card shadow="never" class="toolbar-card">
      <el-form :inline="true">
        <el-form-item>
          <el-input
            v-model="searchKeyword"
            placeholder="搜索用户名、邮箱..."
            clearable
            :prefix-icon="Search"
            style="width: 280px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">搜索</el-button>
          <el-button :icon="Refresh" @click="resetSearch">重置</el-button>
          <el-button type="success" :icon="Plus" @click="openAddDialog">添加用户</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="never">
      <el-table :data="filteredUsers" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="email" label="邮箱" min-width="180" />
        <el-table-column prop="full_name" label="姓名" width="120">
          <template #default="{ row }">{{ row.full_name || '--' }}</template>
        </el-table-column>
        <el-table-column prop="role" label="角色" width="120">
          <template #default="{ row }">
            <el-tag :type="getRoleType(row.role)" size="small">
              {{ getRoleLabel(row.role) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
              {{ row.is_active ? '正常' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button type="danger" size="small" :icon="Delete" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 添加用户弹窗 -->
    <el-dialog v-model="dialogVisible" title="添加用户" width="500px" destroy-on-close>
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="80px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="至少6位" show-password />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="user@example.com" />
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="form.full_name" placeholder="真实姓名" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="form.role" style="width: 100%">
            <el-option label="读者" value="reader" />
            <el-option label="图书管理员" value="librarian" />
            <el-option label="管理员" value="admin" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { getUsers, deleteUser } from '@/api/user'
import { register } from '@/api/auth'
import { formatDateTime, getRoleType, getRoleLabel } from '@/utils/format'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Plus, Delete } from '@element-plus/icons-vue'

const loading = ref(false)
const users = ref([])
const searchKeyword = ref('')

const dialogVisible = ref(false)
const formRef = ref()
const submitting = ref(false)
const form = reactive({
  username: '',
  password: '',
  email: '',
  full_name: '',
  role: 'reader'
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }
  ]
}

const filteredUsers = computed(() => {
  if (!searchKeyword.value) return users.value
  const kw = searchKeyword.value.toLowerCase()
  return users.value.filter(u =>
    u.username.toLowerCase().includes(kw) ||
    u.email.toLowerCase().includes(kw)
  )
})

async function loadUsers() {
  loading.value = true
  try {
    users.value = await getUsers({ limit: 100 }) || []
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  // 前端过滤
}

function resetSearch() {
  searchKeyword.value = ''
}

function openAddDialog() {
  Object.assign(form, {
    username: '', password: '', email: '', full_name: '', role: 'reader'
  })
  dialogVisible.value = true
}

async function handleSubmit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    await register(form)
    ElMessage.success('用户添加成功')
    dialogVisible.value = false
    loadUsers()
  } finally {
    submitting.value = false
  }
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(`确定要删除用户 ${row.username} 吗？`, '提示', {
      type: 'warning'
    })
    await deleteUser(row.id)
    ElMessage.success('用户已禁用')
    loadUsers()
  } catch {
    // 取消
  }
}

onMounted(loadUsers)
</script>

<style scoped lang="scss">
.toolbar-card {
  margin-bottom: 20px;

  :deep(.el-card__body) {
    padding: 16px 20px;
  }
}
</style>
