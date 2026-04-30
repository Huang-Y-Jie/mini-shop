<template>
  <div class="pay-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>支付记录</span>
        </div>
      </template>
      
      <div class="search-bar">
        <el-input v-model="searchForm.order_no" placeholder="订单号" style="width: 200px; margin-right: 10px;"></el-input>
        <el-input v-model="searchForm.transaction_id" placeholder="交易号" style="width: 200px; margin-right: 10px;"></el-input>
        <el-select v-model="searchForm.pay_status" placeholder="支付状态" style="width: 120px; margin-right: 10px;">
          <el-option label="全部" value=""></el-option>
          <el-option label="未支付" value="0"></el-option>
          <el-option label="已支付" value="1"></el-option>
          <el-option label="退款" value="2"></el-option>
        </el-select>
        <el-button type="primary" @click="search">搜索</el-button>
      </div>
      
      <el-table :data="payList" style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="记录ID" width="80"></el-table-column>
        <el-table-column prop="order_no" label="订单号"></el-table-column>
        <el-table-column prop="transaction_id" label="交易号"></el-table-column>
        <el-table-column prop="pay_status" label="支付状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.pay_status === 1 ? 'success' : scope.row.pay_status === 2 ? 'warning' : 'info'">
              {{ scope.row.pay_status === 0 ? '未支付' : scope.row.pay_status === 1 ? '已支付' : '退款' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="pay_time" label="支付时间" width="180"></el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="scope">
            <el-button size="small" @click="viewPayDetail(scope.row.id)">查看</el-button>
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
    
    <!-- 支付详情对话框 -->
    <el-dialog v-model="detailDialogVisible" title="支付详情">
      <el-form :model="payDetail" label-width="100px">
        <el-form-item label="记录ID">
          <el-input v-model="payDetail.id" disabled></el-input>
        </el-form-item>
        <el-form-item label="订单号">
          <el-input v-model="payDetail.order_no" disabled></el-input>
        </el-form-item>
        <el-form-item label="交易号">
          <el-input v-model="payDetail.transaction_id" disabled></el-input>
        </el-form-item>
        <el-form-item label="支付状态">
          <el-input v-model="payDetail.pay_status_text" disabled></el-input>
        </el-form-item>
        <el-form-item label="支付时间">
          <el-input v-model="payDetail.pay_time" disabled></el-input>
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

const payList = ref([]);
const loading = ref(false);
const searchForm = ref({
  order_no: '',
  transaction_id: '',
  pay_status: ''
});
const pagination = ref({
  currentPage: 1,
  pageSize: 10,
  total: 0
});
const detailDialogVisible = ref(false);
const payDetail = ref({});

// 搜索支付记录
const search = () => {
  getPayList();
};

// 获取支付记录列表
const getPayList = async () => {
  loading.value = true;
  try {
    const response = await axios.get('/api/admin/pay/list', {
      params: {
        order_no: searchForm.value.order_no,
        transaction_id: searchForm.value.transaction_id,
        pay_status: searchForm.value.pay_status,
        page: pagination.value.currentPage,
        size: pagination.value.pageSize
      },
      headers: {
        Authorization: `Bearer ${localStorage.getItem('admin_token')}`
      }
    });
    if (response.data.code === 200) {
      payList.value = response.data.data.list;
      pagination.value.total = response.data.data.total;
    }
  } catch (error) {
    console.error('获取支付记录失败:', error);
  } finally {
    loading.value = false;
  }
};

// 查看支付详情
const viewPayDetail = async (id) => {
  try {
    const response = await axios.get(`/api/admin/pay/${id}`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('admin_token')}`
      }
    });
    if (response.data.code === 200) {
      const data = response.data.data;
      payDetail.value = {
        ...data,
        pay_status_text: data.pay_status === 0 ? '未支付' : data.pay_status === 1 ? '已支付' : '退款'
      };
      detailDialogVisible.value = true;
    }
  } catch (error) {
    console.error('获取支付详情失败:', error);
  }
};

// 处理分页大小变化
const handleSizeChange = (size) => {
  pagination.value.pageSize = size;
  getPayList();
};

// 处理当前页变化
const handleCurrentChange = (current) => {
  pagination.value.currentPage = current;
  getPayList();
};

// 页面挂载时获取支付记录
onMounted(() => {
  getPayList();
});
</script>

<style scoped>
.pay-list {
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

/* 输入框和选择框样式 */
:deep(.el-input),
:deep(.el-select) {
  transition: all 0.3s ease;
  border-radius: 8px;
}

:deep(.el-input__wrapper),
:deep(.el-select__wrapper) {
  border-radius: 8px;
  transition: all 0.3s ease;
}

:deep(.el-input__wrapper:hover),
:deep(.el-select__wrapper:hover) {
  box-shadow: 0 0 0 3px rgba(255, 107, 53, 0.1);
}

:deep(.el-input__wrapper.is-focus),
:deep(.el-select__wrapper.is-focus) {
  box-shadow: 0 0 0 3px rgba(255, 107, 53, 0.2);
}

/* 标签样式 */
:deep(.el-tag) {
  border-radius: 8px;
  font-size: 12px;
  padding: 2px 8px;
  transition: all 0.3s ease;
}

:deep(.el-tag:hover) {
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
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
  .pay-list {
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
  .pay-list {
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
  
  :deep(.el-input),
  :deep(.el-select) {
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