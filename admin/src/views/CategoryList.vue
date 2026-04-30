<template>
  <div class="category-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>分类管理</span>
          <el-button type="primary" @click="showAddDialog">添加分类</el-button>
        </div>
      </template>
      
      <el-table :data="categoryList" style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="分类ID" width="80"></el-table-column>
        <el-table-column prop="name" label="分类名称"></el-table-column>
        <el-table-column prop="create_time" label="创建时间" width="180"></el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="scope">
            <el-button size="small" @click="showEditDialog(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteCategory(scope.row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 添加分类对话框 -->
    <el-dialog v-model="addDialogVisible" title="添加分类" width="500px" :modal-append-to-body="true" :append-to-body="true">
      <el-form :model="addForm" label-width="80px">
        <el-form-item label="分类名称">
          <el-input v-model="addForm.name" placeholder="请输入分类名称"></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="addDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="addCategory">确定</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 编辑分类对话框 -->
    <el-dialog v-model="editDialogVisible" title="编辑分类" width="500px" :modal-append-to-body="true" :append-to-body="true">
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="分类名称">
          <el-input v-model="editForm.name" placeholder="请输入分类名称"></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="updateCategory">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';

const categoryList = ref([]);
const loading = ref(false);
const addDialogVisible = ref(false);
const editDialogVisible = ref(false);
const addForm = ref({ name: '' });
const editForm = ref({ id: '', name: '' });

// 显示添加分类对话框
const showAddDialog = () => {
  addForm.value.name = '';
  addDialogVisible.value = true;
};

// 显示编辑分类对话框
const showEditDialog = (row) => {
  editForm.value.id = row.id;
  editForm.value.name = row.name;
  editDialogVisible.value = true;
};

// 获取分类列表
const getCategoryList = async () => {
  loading.value = true;
  try {
    const response = await axios.get('/api/admin/category/list', {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('admin_token')}`
      }
    });
    if (response.data.code === 200) {
      categoryList.value = response.data.data;
    }
  } catch (error) {
    console.error('获取分类列表失败:', error);
  } finally {
    loading.value = false;
  }
};

// 添加分类
const addCategory = async () => {
  try {
    const response = await axios.post('/api/admin/category/add', {
      name: addForm.value.name
    }, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('admin_token')}`
      }
    });
    if (response.data.code === 200) {
      addDialogVisible.value = false;
      getCategoryList();
    }
  } catch (error) {
    console.error('添加分类失败:', error);
  }
};

// 更新分类
const updateCategory = async () => {
  try {
    const response = await axios.put(`/api/admin/category/${editForm.value.id}`, {
      name: editForm.value.name
    }, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('admin_token')}`
      }
    });
    if (response.data.code === 200) {
      editDialogVisible.value = false;
      getCategoryList();
    }
  } catch (error) {
    console.error('更新分类失败:', error);
  }
};

// 删除分类
const deleteCategory = async (id) => {
  try {
    const response = await axios.delete(`/api/admin/category/${id}`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('admin_token')}`
      }
    });
    if (response.data.code === 200) {
      getCategoryList();
    }
  } catch (error) {
    console.error('删除分类失败:', error);
  }
};

// 页面挂载时获取分类列表
onMounted(() => {
  getCategoryList();
});
</script>

<style scoped>
.category-list {
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
  animation-delay: 0.2s;
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
  padding: 16px 20px;
  display: flex;
  align-items: center;
}

:deep(.el-dialog__title) {
  font-size: 18px;
  font-weight: bold;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  position: relative;
  padding-left: 32px;
}

:deep(.el-dialog__title)::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 8px;
  height: 24px;
  background-color: var(--primary-color);
  border-radius: 4px;
  margin-right: 12px;
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
  .category-list {
    padding: 20px;
  }
  
  .card-header {
    padding: 12px 16px;
  }
  
  .card-header span {
    font-size: 16px;
  }
}

@media (max-width: 768px) {
  .category-list {
    padding: 16px;
  }
  
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  :deep(.el-table) {
    font-size: 14px;
  }
  
  :deep(.el-table-column) {
    width: auto !important;
  }
}
</style>