<template>
  <div class="app-container">
    <router-view v-if="$route.path === '/login'" />
    <div v-else class="main-layout">
      <el-container style="height: 100vh;">
        <el-aside width="200px" class="aside">
          <div class="logo">
            <h2>商城管理后台</h2>
          </div>
          <el-menu
            :default-active="activeMenu"
            class="el-menu-vertical-demo"
            router
            background-color="#1890ff"
            text-color="#fff"
            active-text-color="#ffffff"
          >
            <el-menu-item index="/dashboard">
              <el-icon><i class="el-icon-s-home"></i></el-icon>
              <span>控制台</span>
            </el-menu-item>
            <el-menu-item index="/product/list">
              <el-icon><i class="el-icon-s-goods"></i></el-icon>
              <span>商品管理</span>
            </el-menu-item>
            <el-menu-item index="/category/list">
              <el-icon><i class="el-icon-menu"></i></el-icon>
              <span>分类管理</span>
            </el-menu-item>
            <el-menu-item index="/user/list">
              <el-icon><i class="el-icon-user"></i></el-icon>
              <span>用户管理</span>
            </el-menu-item>
            <el-menu-item index="/order/list">
              <el-icon><i class="el-icon-s-order"></i></el-icon>
              <span>订单管理</span>
            </el-menu-item>
            <el-menu-item index="/pay/list">
              <el-icon><i class="el-icon-s-finance"></i></el-icon>
              <span>支付记录</span>
            </el-menu-item>
            <el-menu-item index="/banner/list">
              <el-icon><i class="el-icon-picture-outline"></i></el-icon>
              <span>轮播图管理</span>
            </el-menu-item>
            <el-menu-item index="/region/list">
              <el-icon><i class="el-icon-map-location"></i></el-icon>
              <span>地区运费管理</span>
            </el-menu-item>
            <el-menu-item index="/profile">
              <el-icon><i class="el-icon-user-solid"></i></el-icon>
              <span>个人中心</span>
            </el-menu-item>
          </el-menu>
        </el-aside>
        <el-container>
          <el-header class="header">
            <div class="header-right">
              <el-dropdown>
                <span class="user-info">
                  <el-avatar size="small" :src="userInfo.avatar || 'https://img.icons8.com/ios-filled/50/000000/user.png'" />
                  <span>{{ userInfo.nickname || '管理员' }}</span>
                </span>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item @click="navigateToProfile">个人中心</el-dropdown-item>
                    <el-dropdown-item @click="logout">退出登录</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </el-header>
          <el-main class="main">
            <router-view />
          </el-main>
        </el-container>
      </el-container>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const userInfo = ref({})

const activeMenu = computed(() => {
  const path = router.currentRoute.value.path
  return path
})

const getUserInfo = async () => {
  try {
    const token = localStorage.getItem('admin_token')
    if (token) {
      const res = await axios.get('/api/admin/info', {
        headers: {
          Authorization: `Bearer ${token}`
        }
      })
      if (res.data.code === 200) {
        userInfo.value = res.data.data
      }
    }
  } catch (error) {
    console.error('获取用户信息失败', error)
  }
}

const navigateToProfile = () => {
  router.push('/profile')
}

const logout = async () => {
  try {
    const token = localStorage.getItem('admin_token')
    if (token) {
      await axios.post('/api/admin/logout', {}, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      })
    }
    localStorage.removeItem('admin_token')
    router.push('/login')
  } catch (error) {
    console.error('退出登录失败', error)
    localStorage.removeItem('admin_token')
    router.push('/login')
  }
}

onMounted(() => {
  getUserInfo()
})
</script>

<style>
/* 全局样式 */
:root {
  --primary-color: #1890ff;
  --secondary-color: #40a9ff;
  --accent-color: #69c0ff;
  --accent-secondary: #91d5ff;
  --text-primary: #333333;
  --text-secondary: #666666;
  --text-light: #999999;
  --background-color: #f0f2f5;
  --white: #ffffff;
  --border-color: #e8e8e8;
  --success-color: #52c41a;
  --error-color: #ff4d4f;
  --warning-color: #faad14;
  --info-color: #1890ff;
  --light-gray: #f5f5f5;
  --medium-gray: #e8e8e8;
  --card-bg: #ffffff;
  --card-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  --gradient-bg: linear-gradient(135deg, #1890ff 0%, #40a9ff 100%);
  --gradient-accent: linear-gradient(135deg, #69c0ff 0%, #91d5ff 100%);
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  font-size: 14px;
  color: var(--text-primary);
  line-height: 1.5;
  background-color: var(--background-color);
}
</style>

<style scoped>
.app-container {
  width: 100%;
  height: 100vh;
  overflow: hidden;
}

.main-layout {
  width: 100%;
  height: 100%;
}

.aside {
  background-color: #1890ff;
  overflow-y: auto;
  transition: all 0.3s ease;
}

.aside:hover {
  box-shadow: 2px 0 8px rgba(24, 144, 255, 0.3);
}

.logo {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 18px;
  font-weight: bold;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  background-color: rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
}

.logo:hover {
  background-color: rgba(255, 255, 255, 0.2);
}

.header {
  background-color: var(--white);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  display: flex;
  justify-content: flex-end;
  align-items: center;
  padding: 0 24px;
  height: 64px;
  transition: all 0.3s ease;
}

.header:hover {
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 8px 16px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.user-info:hover {
  background-color: rgba(0, 0, 0, 0.05);
  transform: translateY(-2px);
}

.user-info span {
  margin-left: 12px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.main {
  padding: 24px;
  overflow-y: auto;
  background-color: #f5f7fa;
  height: 100%;
  min-height: calc(100vh - 64px);
}

/* 卡片样式 */
.card {
  background-color: var(--white);
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.card:hover {
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
  transform: translateY(-4px);
}

/* 按钮样式 */
.btn {
  display: inline-block;
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
  cursor: pointer;
  border: none;
  outline: none;
}

.btn-primary {
  background: var(--gradient-bg);
  color: var(--white);
  box-shadow: 0 4px 8px rgba(24, 144, 255, 0.3);
}

.btn-primary:hover {
  background: var(--gradient-bg);
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(24, 144, 255, 0.4);
  opacity: 0.9;
}

.btn-default {
  background-color: var(--white);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}

.btn-default:hover {
  border-color: var(--primary-color);
  color: var(--primary-color);
  transform: translateY(-2px);
}

/* 表格样式 */
.table-container {
  background-color: var(--white);
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  margin-bottom: 24px;
}

/* 表单样式 */
.form-item {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: var(--text-primary);
}

.form-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.3s ease;
}

.form-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(24, 144, 255, 0.1);
}

/* 动画效果 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.fade-in {
  animation: fadeIn 0.5s ease forwards;
}
</style>