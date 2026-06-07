<template>
  <div class="login-page">
    <div class="login-box">
      <div class="logo">
        <el-icon :size="56" color="#4f46e5"><Reading /></el-icon>
        <h1>图书馆管理系统</h1>
        <p>Library Management System</p>
      </div>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        @keyup.enter="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="form.username"
            placeholder="用户名"
            :prefix-icon="User"
            size="large"
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码"
            :prefix-icon="Lock"
            size="large"
            show-password
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            class="login-btn"
            @click="handleLogin"
          >
            <el-icon><Key /></el-icon>
            登录
          </el-button>
        </el-form-item>
      </el-form>

      <div class="tips">
        <p>💡 测试账号：</p>
        <el-space wrap>
          <el-tag>admin / admin123</el-tag>
          <el-tag type="success">librarian / lib123</el-tag>
          <el-tag type="warning">reader / reader123</el-tag>
        </el-space>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { User, Lock, Key, Reading } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref()
const loading = ref(false)

const form = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

async function handleLogin() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    await userStore.login(form)
    ElMessage.success('登录成功')
    router.push('/dashboard')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped lang="scss">
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-box {
  background: #fff;
  padding: 48px;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.15);
  width: 100%;
  max-width: 420px;
  animation: slideUp 0.5s ease;
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

.logo {
  text-align: center;
  margin-bottom: 32px;

  h1 {
    font-size: 24px;
    font-weight: 700;
    margin-top: 16px;
    color: #1e293b;
  }

  p {
    color: #64748b;
    font-size: 14px;
    margin-top: 4px;
  }
}

.login-btn {
  width: 100%;
}

.tips {
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #e2e8f0;
  text-align: center;

  p {
    font-size: 13px;
    color: #64748b;
    margin-bottom: 12px;
  }
}
</style>
