<template>
  <div class="user-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>用户管理</span>
        </div>
      </template>
      
      <div class="search-bar">
        <el-input v-model="searchForm.phone" placeholder="手机号" style="width: 200px; margin-right: 10px;"></el-input>
        <el-input v-model="searchForm.nickname" placeholder="昵称" style="width: 200px; margin-right: 10px;"></el-input>
        <el-button type="primary" @click="search">搜索</el-button>
      </div>
      
      <el-table :data="userList" style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="用户ID" width="80"></el-table-column>
        <el-table-column prop="nickname" label="昵称"></el-table-column>
        <el-table-column prop="phone" label="手机号"></el-table-column>
        <el-table-column prop="create_time" label="创建时间" width="180"></el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="scope">
            <el-button size="small" @click="viewUserDetail(scope.row.id)">查看</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination" style="margin-top: 20px;">
        <el-pagination
          v-model:current-page="pagination.currentPage"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="pagination.total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        ></el-pagination>
      </div>
    </el-card>
    
    <!-- 用户详情对话框 -->
    <el-dialog v-model="detailDialogVisible" title="用户详情">
      <el-form :model="userDetail" label-width="100px">
        <el-form-item label="用户ID">
          <el-input v-model="userDetail.id" disabled></el-input>
        </el-form-item>
        <el-form-item label="昵称">
          <el-input v-model="userDetail.nickname" disabled></el-input>
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="userDetail.phone" disabled></el-input>
        </el-form-item>
        <el-form-item label="地址">
          <el-input v-model="userDetail.address" type="textarea" disabled :rows="3"></el-input>
        </el-form-item>
        <el-form-item label="创建时间">
          <el-input v-model="userDetail.create_time" disabled></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="detailDialogVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';

const userList = ref([]);
const loading = ref(false);
const searchForm = ref({
  phone: '',
  nickname: ''
});
const pagination = ref({
  currentPage: 1,
  pageSize: 10,
  total: 0
});
const detailDialogVisible = ref(false);
const userDetail = ref({});

// 搜索用户
const search = () => {
  getUserList();
};

// 获取用户列表
const getUserList = async () => {
  loading.value = true;
  try {
    const response = await axios.get('/api/admin/user/list', {
      params: {
        phone: searchForm.value.phone,
        nickname: searchForm.value.nickname,
        page: pagination.value.currentPage,
        size: pagination.value.pageSize
      },
      headers: {
        Authorization: `Bearer ${localStorage.getItem('admin_token')}`
      }
    });
    if (response.data.code === 200) {
      userList.value = response.data.data.list;
      pagination.value.total = response.data.data.total;
    }
  } catch (error) {
    console.error('获取用户列表失败:', error);
  } finally {
    loading.value = false;
  }
};

// 查看用户详情
const viewUserDetail = async (id) => {
  try {
    const response = await axios.get(`/api/admin/user/${id}`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('admin_token')}`
      }
    });
    if (response.data.code === 200) {
      userDetail.value = response.data.data;
      detailDialogVisible.value = true;
    }
  } catch (error) {
    console.error('获取用户详情失败:', error);
  }
};

// 处理分页大小变化
const handleSizeChange = (size) => {
  pagination.value.pageSize = size;
  getUserList();
};

// 处理当前页变化
const handleCurrentChange = (current) => {
  pagination.value.currentPage = current;
  getUserList();
};

// 页面挂载时获取用户列表
onMounted(() => {
  getUserList();
});
</script>

<style scoped>
.user-list {
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

.search-bar {
  margin: 24px 0;
  padding: 20px;
  background-color: rgba(0, 0, 0, 0.02);
  border-radius: 8px;
  display: flex;
  align-items: center;
  transition: all 0.3s ease;
  animation: slideUp 0.5s ease forwards;
  animation-delay: 0.2s;
}

.search-bar:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid var(--border-color);
  animation: slideUp 0.5s ease forwards;
  animation-delay: 0.4s;
}

.dialog-footer {
  width: 100%;
  display: flex;
  justify-content: flex-end;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
}

/* 表格样式 */
:deep(.el-table) {
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  animation: slideUp 0.5s ease forwards;
  animation-delay: 0.3s;
}

:deep(.el-table:hover) {
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
}

:deep(.el-table__header-wrapper) {
  background-color: rgba(0, 0, 0, 0.02);
}

:deep(.el-table__header th) {
  font-weight: 500;
  color: var(--text-primary);
  background-color: rgba(0, 0, 0, 0.02);
}

:deep(.el-table__row) {
  transition: all 0.3s ease;
}

:deep(.el-table__row:hover) {
  background-color: rgba(255, 107, 53, 0.05);
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

/* 输入框样式 */
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

/* 模态框样式 */
:deep(.el-dialog) {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
  animation: fadeIn 0.5s ease forwards;
}

:deep(.el-dialog__header) {
  background-color: rgba(255, 107, 53, 0.1);
  border-bottom: 1px solid rgba(255, 107, 53, 0.2);
}

:deep(.el-dialog__title) {
  font-size: 18px;
  font-weight: 500;
  color: var(--text-primary);
}

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

:deep(.el-input.is-disabled .el-input__wrapper) {
  background-color: rgba(0, 0, 0, 0.02);
  border-color: var(--border-color);
}

:deep(.el-input.is-disabled .el-input__inner) {
  color: var(--text-secondary);
}

/* 分页样式 */
:deep(.el-pagination) {
  transition: all 0.3s ease;
}

:deep(.el-pagination__item:hover) {
  transform: translateY(-2px);
}

:deep(.el-pagination__item.is-current) {
  background-color: var(--primary-color);
  border-color: var(--primary-color);
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
  .user-list {
    padding: 20px;
  }
  
  .card-header {
    padding: 12px 16px;
  }
  
  .card-header span {
    font-size: 16px;
  }
  
  .search-bar {
    padding: 16px;
    margin: 20px 0;
  }
  
  .pagination {
    margin-top: 20px;
    padding-top: 16px;
  }
}

@media (max-width: 768px) {
  .user-list {
    padding: 16px;
  }
  
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .search-bar {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  :deep(.el-input) {
    width: 100% !important;
    margin-right: 0 !important;
  }
  
  :deep(.el-table) {
    font-size: 14px;
  }
  
  :deep(.el-table-column) {
    width: auto !important;
  }
}
</style>