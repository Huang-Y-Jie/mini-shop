<template>
  <div class="order-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>订单管理</span>
          <el-switch v-model="soundEnabled" @change="toggleSound" active-text="声音提醒: 开启" inactive-text="声音提醒: 关闭"></el-switch>
        </div>
      </template>
      
      <div class="search-bar">
        <el-input v-model="searchForm.order_no" placeholder="订单号" style="width: 200px; margin-right: 10px;"></el-input>
        <el-select v-model="searchForm.pay_status" placeholder="支付状态" style="width: 120px; margin-right: 10px;">
          <el-option label="全部" value=""></el-option>
          <el-option label="未支付" value="0"></el-option>
          <el-option label="已支付" value="1"></el-option>
          <el-option label="退款" value="2"></el-option>
        </el-select>
        <el-select v-model="searchForm.order_status" placeholder="订单状态" style="width: 120px; margin-right: 10px;">
          <el-option label="全部" value=""></el-option>
          <el-option label="待支付" value="1"></el-option>
          <el-option label="已完成" value="2"></el-option>
          <el-option label="已取消" value="3"></el-option>
          <el-option label="超时取消" value="4"></el-option>
        </el-select>
        <el-button type="primary" @click="search">搜索</el-button>
      </div>
      
      <el-table :data="orderList" style="width: 100%" v-loading="loading">
        <el-table-column prop="order_id" label="订单ID" width="100"></el-table-column>
        <el-table-column prop="order_no" label="订单号"></el-table-column>
        <el-table-column prop="user_id" label="用户ID" width="80"></el-table-column>
        <el-table-column prop="total_amount" label="总金额" width="100"></el-table-column>
        <el-table-column prop="pay_status" label="支付状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.pay_status === 1 ? 'success' : scope.row.pay_status === 2 ? 'warning' : 'info'">
              {{ scope.row.pay_status === 0 ? '未支付' : scope.row.pay_status === 1 ? '已支付' : '退款' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="order_status" label="订单状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.order_status === 1 ? 'info' : scope.row.order_status === 2 ? 'primary' : scope.row.order_status === 3 ? 'success' : 'danger'">
              {{ scope.row.order_status === 1 ? '待支付' : scope.row.order_status === 2 ? '已支付' : scope.row.order_status === 3 ? '已完成' : (scope.row.order_status === 4 || scope.row.order_status === 5) ? '已取消' : '待支付' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="创建时间" width="180"></el-table-column>
        <el-table-column label="商品信息" min-width="200">
          <template #default="scope">
            <div v-if="scope.row.items && scope.row.items.length > 0">
              <div v-for="(item, index) in scope.row.items" :key="index" v-if="index < 2">
                {{ item.product_name }} × {{ item.quantity }}
              </div>
              <div v-if="scope.row.items.length > 2">
                等{{ scope.row.items.length }}件商品
              </div>
            </div>
            <div v-else>无商品</div>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="scope">
            <el-button size="small" @click="viewOrderDetail(scope.row.order_id)">查看</el-button>
            <el-button size="small" type="danger" @click="cancelOrder(scope.row.order_id)" :disabled="scope.row.order_status !== 1">取消</el-button>
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
    
    <!-- 订单详情对话框 -->
    <el-dialog v-model="detailDialogVisible" title="订单详情">
      <el-form :model="orderDetail" label-width="100px">
        <el-form-item label="订单ID">
          <el-input v-model="orderDetail.order_id" disabled></el-input>
        </el-form-item>
        <el-form-item label="订单号">
          <el-input v-model="orderDetail.order_no" disabled></el-input>
        </el-form-item>
        <el-form-item label="总金额">
          <el-input v-model="orderDetail.total_amount" disabled></el-input>
        </el-form-item>
        <el-form-item label="支付状态">
          <el-input v-model="orderDetail.pay_status_text" disabled></el-input>
        </el-form-item>
        <el-form-item label="订单状态">
          <el-input v-model="orderDetail.order_status_text" disabled></el-input>
        </el-form-item>
        <el-form-item label="收货人">
          <el-input v-model="orderDetail.consignee" disabled></el-input>
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="orderDetail.phone" disabled></el-input>
        </el-form-item>
        <el-form-item label="地址">
          <el-input v-model="orderDetail.address" type="textarea" disabled :rows="3"></el-input>
        </el-form-item>
        <el-form-item label="创建时间">
          <el-input v-model="orderDetail.create_time" disabled></el-input>
        </el-form-item>
        <el-form-item label="支付时间">
          <el-input v-model="orderDetail.pay_time" disabled></el-input>
        </el-form-item>
        <el-form-item label="商品信息">
          <el-table :data="orderDetail.items" style="width: 100%">
            <el-table-column prop="product_id" label="商品ID" width="80"></el-table-column>
            <el-table-column prop="product_name" label="商品名称"></el-table-column>
            <el-table-column prop="quantity" label="数量" width="80"></el-table-column>
            <el-table-column prop="price" label="单价" width="80"></el-table-column>
          </el-table>
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
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';

const router = useRouter();
const orderList = ref([]);
const loading = ref(false);
const searchForm = ref({
  order_no: '',
  pay_status: '',
  order_status: ''
});
const pagination = ref({
  currentPage: 1,
  pageSize: 10,
  total: 0
});
const detailDialogVisible = ref(false);
const orderDetail = ref({});
const soundEnabled = ref(false);
let socket = null;
let audio = null;

// 搜索订单
const search = () => {
  getOrderList();
};

// 获取订单列表
const getOrderList = async () => {
  loading.value = true;
  try {
    const params = {
      order_no: searchForm.value.order_no,
      page: pagination.value.currentPage,
      size: pagination.value.pageSize
    };
    
    // 只有当状态值不为空字符串时才传递参数
    if (searchForm.value.pay_status !== '') {
      params.pay_status = parseInt(searchForm.value.pay_status);
    }
    
    if (searchForm.value.order_status !== '') {
      params.order_status = parseInt(searchForm.value.order_status);
    }
    
    const response = await axios.get('/api/admin/order/list', {
      params: params,
      headers: {
        Authorization: `Bearer ${localStorage.getItem('admin_token')}`
      }
    });
    if (response.data.code === 200) {
      orderList.value = response.data.data.list;
      pagination.value.total = response.data.data.total;
    }
  } catch (error) {
    console.error('获取订单列表失败:', error);
  } finally {
    loading.value = false;
  }
};

// 查看订单详情
const viewOrderDetail = async (id) => {
  try {
    const response = await axios.get(`/api/admin/order/${id}`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('admin_token')}`
      }
    });
    if (response.data.code === 200) {
      const data = response.data.data;
      orderDetail.value = {
        ...data,
        pay_status_text: data.pay_status === 0 ? '未支付' : data.pay_status === 1 ? '已支付' : '退款',
        order_status_text: data.order_status === 1 ? '待支付' : data.order_status === 2 ? '已完成' : data.order_status === 3 ? '已取消' : '超时取消'
      };
      detailDialogVisible.value = true;
    }
  } catch (error) {
    console.error('获取订单详情失败:', error);
  }
};

// 取消订单
const cancelOrder = async (id) => {
  try {
    const response = await axios.put(`/api/admin/order/${id}/cancel`, {}, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('admin_token')}`
      }
    });
    if (response.data.code === 200) {
      getOrderList();
    }
  } catch (error) {
    console.error('取消订单失败:', error);
  }
};

// 处理分页大小变化
const handleSizeChange = (size) => {
  pagination.value.pageSize = size;
  getOrderList();
};

// 处理当前页变化
const handleCurrentChange = (current) => {
  pagination.value.currentPage = current;
  getOrderList();
};

// 切换声音提醒
const toggleSound = async () => {
  try {
    const response = await axios.put('/api/admin/notify/setting', {
      is_enable: soundEnabled.value
    }, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('admin_token')}`
      }
    });
    if (response.data.code !== 200) {
      soundEnabled.value = !soundEnabled.value;
    }
  } catch (error) {
    console.error('设置声音提醒失败:', error);
    soundEnabled.value = !soundEnabled.value;
  }
};

// 初始化WebSocket连接
const initWebSocket = () => {
  const token = localStorage.getItem('admin_token');
  if (!token) return;
  
  // 使用原生WebSocket
  socket = new WebSocket(`ws://localhost:8002/ws/admin/order?admin_token=${token}`);
  
  socket.onopen = () => {
    console.log('WebSocket连接成功');
  };
  
  socket.onclose = () => {
    console.log('WebSocket连接断开');
    // 尝试重连
    setTimeout(initWebSocket, 3000);
  };
  
  socket.onerror = (error) => {
    console.error('WebSocket错误:', error);
  };
  
  socket.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      console.log('收到WebSocket消息:', data);
      
      if (data.type === 'new_order') {
        console.log('新订单:', data.data);
        getOrderList();
      } else if (data.type === 'order_status') {
        console.log('订单状态更新:', data.data);
        getOrderList();
        // 只有当订单状态更新为已支付时才语音播报
        if (soundEnabled.value && data.data.order_status === 2) {
          playSound();
        }
      } else if (data.type === 'order_timeout') {
        console.log('订单超时取消:', data.data);
        getOrderList();
      } else if (data.type === 'ping') {
        // 发送心跳响应
        socket.send('pong');
      }
    } catch (error) {
      console.error('解析WebSocket消息失败:', error);
    }
  };
};

// 播放提醒音效
const playSound = () => {
  // 使用Web Speech API实现语音播报
  if ('speechSynthesis' in window) {
    const speech = new SpeechSynthesisUtterance('新订单来了，请注意查收');
    speech.lang = 'zh-CN';
    speech.rate = 1;
    speech.pitch = 1;
    speech.volume = 1;
    window.speechSynthesis.speak(speech);
  } else {
    // 兼容不支持Web Speech API的浏览器
    if (!audio) {
      audio = new Audio();
      audio.src = '/sound/notify.mp3';
    }
    audio.play().catch(err => {
      console.error('播放音效失败:', err);
    });
  }
};

// 页面挂载时初始化
onMounted(() => {
  getOrderList();
  initWebSocket();
  // 检查声音提醒设置
  axios.get('/api/admin/info', {
    headers: {
      Authorization: `Bearer ${localStorage.getItem('admin_token')}`
    }
  }).then(response => {
    if (response.data.code === 200) {
      // 默认开启声音提醒
      soundEnabled.value = true;
      // 保存到后端
      axios.put('/api/admin/notify/setting', {
        is_enable: true
      }, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('admin_token')}`
        }
      });
    }
  });
});

// 页面卸载时清理
onUnmounted(() => {
  if (socket) {
    socket.close();
  }
  if (audio) {
    audio.pause();
  }
});
</script>

<style scoped>
.order-list {
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

:deep(.el-button--danger) {
  background-color: var(--error-color);
  border-color: var(--error-color);
  box-shadow: 0 4px 8px rgba(255, 77, 79, 0.3);
}

:deep(.el-button--danger:hover) {
  background-color: #ff7875;
  border-color: #ff7875;
  box-shadow: 0 6px 12px rgba(255, 77, 79, 0.4);
}

:deep(.el-button:disabled) {
  opacity: 0.6;
  cursor: not-allowed;
}

:deep(.el-button:disabled:hover) {
  transform: none;
  box-shadow: none;
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
  max-width: 90%;
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
  .order-list {
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
  .order-list {
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
  
  :deep(.el-dialog) {
    width: 95% !important;
    max-width: 95% !important;
  }
}
</style>