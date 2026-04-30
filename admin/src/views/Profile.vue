<template>
  <div class="profile">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>个人中心</span>
        </div>
      </template>
      
      <el-form :model="adminInfo" label-width="100px" style="max-width: 600px;">
        <el-form-item label="用户名">
          <el-input v-model="adminInfo.username" disabled></el-input>
        </el-form-item>
        <el-form-item label="昵称">
          <el-input v-model="adminInfo.nickname"></el-input>
        </el-form-item>
        <el-form-item label="角色">
          <el-input v-model="adminInfo.role_text" disabled></el-input>
        </el-form-item>
        <el-form-item label="声音提醒">
          <el-switch v-model="adminInfo.sound_enabled" @change="toggleSound"></el-switch>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="updateInfo">更新信息</el-button>
        </el-form-item>
      </el-form>
      
      <el-divider>修改密码</el-divider>
      
      <el-form :model="passwordForm" label-width="100px" style="max-width: 600px;">
        <el-form-item label="旧密码">
          <el-input v-model="passwordForm.old_password" type="password"></el-input>
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="passwordForm.new_password" type="password"></el-input>
        </el-form-item>
        <el-form-item label="确认新密码">
          <el-input v-model="passwordForm.confirm_password" type="password"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="changePassword">修改密码</el-button>
        </el-form-item>
      </el-form>
      
      <el-divider>系统信息</el-divider>
      
      <el-form label-width="100px" style="max-width: 600px;">
        <el-form-item label="系统版本">
          <el-input v-model="systemInfo.version" disabled></el-input>
        </el-form-item>
        <el-form-item label="后端API地址">
          <el-input v-model="systemInfo.api_url" disabled></el-input>
        </el-form-item>
        <el-form-item label="WebSocket地址">
          <el-input v-model="systemInfo.ws_url" disabled></el-input>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import config from '../config';

const adminInfo = ref({
  username: '',
  nickname: '',
  role: '',
  role_text: '',
  sound_enabled: false
});
const passwordForm = ref({
  old_password: '',
  new_password: '',
  confirm_password: ''
});
const systemInfo = ref({
  version: '1.0.0',
  api_url: config.api.baseUrl,
  ws_url: config.api.baseUrl.replace('http', 'ws') + '/ws/admin/order'
});

// 获取管理员信息
const getAdminInfo = async () => {
  try {
    const response = await axios.get('/api/admin/info', {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('admin_token')}`
      }
    });
    if (response.data.code === 200) {
      const data = response.data.data;
      adminInfo.value = {
        ...data,
        role_text: data.role === 1 ? '超级管理员' : '普通管理员',
        sound_enabled: false // 这里应该从Redis获取声音提醒设置，这里简化处理
      };
    }
  } catch (error) {
    console.error('获取管理员信息失败:', error);
  }
};

// 更新管理员信息
const updateInfo = async () => {
  try {
    // 这里应该调用更新管理员信息的API，这里简化处理
    console.log('更新管理员信息:', adminInfo.value);
  } catch (error) {
    console.error('更新管理员信息失败:', error);
  }
};

// 修改密码
const changePassword = async () => {
  try {
    if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
      console.error('两次输入的密码不一致');
      return;
    }
    // 这里应该调用修改密码的API，这里简化处理
    console.log('修改密码:', passwordForm.value);
  } catch (error) {
    console.error('修改密码失败:', error);
  }
};

// 切换声音提醒
const toggleSound = async () => {
  try {
    const response = await axios.put('/api/admin/notify/setting', {
      is_enable: adminInfo.value.sound_enabled
    }, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('admin_token')}`
      }
    });
    if (response.data.code !== 200) {
      adminInfo.value.sound_enabled = !adminInfo.value.sound_enabled;
    }
  } catch (error) {
    console.error('设置声音提醒失败:', error);
    adminInfo.value.sound_enabled = !adminInfo.value.sound_enabled;
  }
};

// 页面挂载时获取管理员信息
onMounted(() => {
  getAdminInfo();
});
</script>

<style scoped>
.profile {
  padding: 24px;
  animation: fadeIn 0.5s ease forwards;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background-color: rgba(255, 107, 53, 0.1);
  border-bottom: 1px solid rgba(255, 107, 53, 0.2);
  border-radius: 8px 8px 0 0;
}

.card-header span {
  font-size: 18px;
  font-weight: bold;
  color: var(--text-primary);
  display: flex;
  align-items: center;
}

.card-header span::before {
  content: '';
  width: 8px;
  height: 24px;
  background-color: var(--primary-color);
  border-radius: 4px;
  margin-right: 12px;
}

/* 表单样式 */
:deep(.el-form) {
  margin-top: 24px;
  animation: slideUp 0.5s ease forwards;
}

:deep(.el-form:nth-child(1)) {
  animation-delay: 0.1s;
}

:deep(.el-form:nth-child(3)) {
  animation-delay: 0.2s;
}

:deep(.el-form:nth-child(5)) {
  animation-delay: 0.3s;
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
  transition: all 0.3s ease;
  border-radius: 8px;
}

:deep(.el-input__wrapper) {
  border-radius: 8px;
  transition: all 0.3s ease;
}

:deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 3px rgba(255, 107, 53, 0.1);
}

:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 3px rgba(255, 107, 53, 0.2);
}

:deep(.el-input.is-disabled .el-input__wrapper) {
  background-color: rgba(0, 0, 0, 0.02);
  border-color: var(--border-color);
}

:deep(.el-input.is-disabled .el-input__inner) {
  color: var(--text-secondary);
}

/* 开关样式 */
:deep(.el-switch) {
  transition: all 0.3s ease;
}

:deep(.el-switch:hover) {
  transform: translateY(-2px);
}

:deep(.el-switch__input.is-checked + .el-switch__core) {
  background-color: var(--primary-color);
  border-color: var(--primary-color);
}

/* 按钮样式 */
:deep(.el-button) {
  transition: all 0.3s ease;
  border-radius: 8px;
}

:deep(.el-button:hover) {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

:deep(.el-button--primary) {
  background-color: var(--primary-color);
  border-color: var(--primary-color);
  box-shadow: 0 4px 8px rgba(255, 107, 53, 0.3);
}

:deep(.el-button--primary:hover) {
  background-color: var(--secondary-color);
  border-color: var(--secondary-color);
  box-shadow: 0 6px 12px rgba(255, 107, 53, 0.4);
}

/* 分割线样式 */
:deep(.el-divider) {
  margin: 32px 0;
  border-top: 1px solid var(--border-color);
}

/* 卡片样式 */
:deep(.el-card) {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

:deep(.el-card:hover) {
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
  transform: translateY(-4px);
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

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(40px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .profile {
    padding: 20px;
  }
  
  .card-header {
    padding: 12px 16px;
  }
  
  .card-header span {
    font-size: 16px;
  }
  
  :deep(.el-form) {
    margin-top: 20px;
  }
  
  :deep(.el-form-item) {
    margin-bottom: 20px;
  }
  
  :deep(.el-divider) {
    margin: 24px 0;
  }
}

@media (max-width: 768px) {
  .profile {
    padding: 16px;
  }
  
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  :deep(.el-form) {
    max-width: 100% !important;
  }
  
  :deep(.el-form-item__label) {
    width: 80px !important;
  }
  
  :deep(.el-form-item__content) {
    margin-left: 90px !important;
  }
}
</style>