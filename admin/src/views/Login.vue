<template>
  <div class="login-container">
    <div class="login-form">
      <h2 class="login-title">商城管理后台</h2>
      <el-form :model="loginForm" :rules="rules" ref="loginFormRef" label-width="80px">
        <el-form-item label="账号" prop="username">
          <el-input v-model="loginForm.username" placeholder="请输入账号" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="loginForm.password" type="password" placeholder="请输入密码" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" class="login-btn" @click="login" :loading="loading">登录</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const router = useRouter()
const loginFormRef = ref(null)
const loading = ref(false)

const loginForm = reactive({
  username: 'admin',
  password: 'admin'
})

const rules = {
  username: [
    { required: true, message: '请输入账号', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
}

const login = async () => {
  if (!loginFormRef.value) return
  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const res = await axios.post('/api/admin/login', loginForm)
        if (res.data.code === 200) {
          localStorage.setItem('admin_token', res.data.data.token)
          router.push('/dashboard')
        } else {
          ElMessage.error(res.data.msg || '登录失败')
        }
      } catch (error) {
        console.error('登录失败', error)
        ElMessage.error('登录失败，请检查网络连接')
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
.login-container {
  width: 100vw;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--background-color);
  background-image: linear-gradient(135deg, #f0f2f5 0%, #d6e4f0 100%);
  position: relative;
  overflow: hidden;
}

.login-container::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(24, 144, 255, 0.1) 0%, rgba(24, 144, 255, 0) 70%);
  animation: pulse 6s infinite ease-in-out;
}

.login-form {
  width: 420px;
  padding: 48px;
  background-color: var(--white);
  border-radius: 16px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  position: relative;
  z-index: 1;
  transition: all 0.3s ease;
  animation: fadeIn 0.8s ease forwards;
}

.login-form:hover {
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.2);
  transform: translateY(-8px);
}

.login-title {
  text-align: center;
  margin-bottom: 36px;
  color: var(--text-primary);
  font-size: 24px;
  font-weight: bold;
  position: relative;
  display: inline-block;
  left: 50%;
  transform: translateX(-50%);
}

.login-title::after {
  content: '';
  position: absolute;
  bottom: -12px;
  left: 50%;
  transform: translateX(-50%);
  width: 80px;
  height: 4px;
  background-color: var(--primary-color);
  border-radius: 2px;
  animation: slideIn 0.5s ease forwards;
}

.login-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 500;
  border-radius: 8px;
  background: var(--gradient-bg);
  color: var(--white);
  border: none;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(24, 144, 255, 0.3);
}

.login-btn:hover {
  background: var(--gradient-bg);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(24, 144, 255, 0.4);
  opacity: 0.9;
}

.login-btn:active {
  transform: translateY(0);
}

/* 表单样式 */
:deep(.el-form) {
  margin-top: 24px;
}

:deep(.el-form-item) {
  margin-bottom: 24px;
  transition: all 0.3s ease;
}

:deep(.el-form-item:hover) {
  transform: translateX(4px);
}

:deep(.el-form-item__label) {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
}

:deep(.el-input) {
  border-radius: 8px;
  transition: all 0.3s ease;
}

:deep(.el-input__wrapper) {
  border-radius: 8px;
  transition: all 0.3s ease;
}

:deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 3px rgba(24, 144, 255, 0.1);
}

:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 3px rgba(24, 144, 255, 0.2);
}

:deep(.el-input__inner) {
  font-size: 14px;
  color: var(--text-primary);
}

/* 动画效果 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(40px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideIn {
  from {
    width: 0;
  }
  to {
    width: 80px;
  }
}

@keyframes pulse {
  0% {
    transform: scale(1);
    opacity: 0.5;
  }
  50% {
    transform: scale(1.1);
    opacity: 0.3;
  }
  100% {
    transform: scale(1);
    opacity: 0.5;
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .login-form {
    width: 90%;
    max-width: 400px;
    padding: 32px;
  }
  
  .login-title {
    font-size: 20px;
    margin-bottom: 28px;
  }
  
  .login-title::after {
    width: 60px;
  }
  
  :deep(.el-form-item) {
    margin-bottom: 20px;
  }
  
  .login-btn {
    height: 44px;
    font-size: 14px;
  }
}
</style>