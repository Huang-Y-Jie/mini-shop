<template>
  <div class="dashboard-container">
    <h2 class="page-title">控制台</h2>
    
    <!-- 数据卡片 -->
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="data-card">
          <template #header>
            <div class="card-header">
              <span>本月订单数</span>
            </div>
          </template>
          <div class="data-value">{{ dashboardData.month_order_count }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="data-card">
          <template #header>
            <div class="card-header">
              <span>本月销售额</span>
            </div>
          </template>
          <div class="data-value">¥{{ dashboardData.month_sales }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="data-card">
          <template #header>
            <div class="card-header">
              <span>今日订单数</span>
            </div>
          </template>
          <div class="data-value">{{ dashboardData.today_order_count }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="data-card">
          <template #header>
            <div class="card-header">
              <span>今日销售额</span>
            </div>
          </template>
          <div class="data-value">¥{{ dashboardData.today_sales }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="data-card">
          <template #header>
            <div class="card-header">
              <span>待支付订单</span>
            </div>
          </template>
          <div class="data-value">{{ dashboardData.pending_pay_count }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="data-card">
          <template #header>
            <div class="card-header">
              <span>新订单数</span>
            </div>
          </template>
          <div class="data-value">{{ dashboardData.new_order_count }}</div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 新订单列表 -->
    <el-card class="order-card">
      <template #header>
        <div class="card-header">
          <span>今日新订单</span>
        </div>
      </template>
      <el-table :data="newOrders" style="width: 100%">
        <el-table-column prop="order_no" label="订单号" width="200" />
        <el-table-column prop="user_id" label="用户ID" width="100" />
        <el-table-column prop="total_amount" label="金额" width="100" />
        <el-table-column prop="create_time" label="创建时间" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <span v-if="scope.row.status === 0">待支付</span>
            <span v-else-if="scope.row.status === 1">已支付</span>
            <span v-else-if="scope.row.status === 2">已发货</span>
            <span v-else-if="scope.row.status === 3">已完成</span>
            <span v-else-if="scope.row.status === 4">已取消</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="scope">
            <el-button size="small" @click="viewOrderDetail(scope.row.order_id)">查看详情</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 新订单提醒 -->
    <el-dialog
      v-model="newOrderDialogVisible"
      title="新订单提醒"
      width="500px"
    >
      <div class="new-order-info">
        <p>订单号：{{ newOrderInfo.order_no }}</p>
        <p>金额：¥{{ newOrderInfo.total_amount }}</p>
        <p>用户ID：{{ newOrderInfo.user_id }}</p>
        <p>创建时间：{{ newOrderInfo.create_time }}</p>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="newOrderDialogVisible = false">关闭</el-button>
          <el-button type="primary" @click="viewOrderDetail(newOrderInfo.order_id)">查看详情</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { io } from 'socket.io-client'

const router = useRouter()
const dashboardData = ref({
  month_order_count: 0,
  month_sales: 0,
  today_order_count: 0,
  today_sales: 0,
  pending_pay_count: 0,
  new_order_count: 0
})
const newOrders = ref([])
const newOrderDialogVisible = ref(false)
const newOrderInfo = ref({})
let socket = null

const getDashboardData = async () => {
  try {
    const token = localStorage.getItem('admin_token')
    const res = await axios.get('/api/admin/dashboard', {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
    dashboardData.value = res.data.data || {
      today_order_count: 0,
      today_sales: 0,
      pending_pay_count: 0,
      new_order_count: 0
    }
  } catch (error) {
    console.error('获取数据失败', error)
    dashboardData.value = {
      today_order_count: 0,
      today_sales: 0,
      pending_pay_count: 0,
      new_order_count: 0
    }
  }
}

const getNewOrders = async () => {
  try {
    const token = localStorage.getItem('admin_token')
    const res = await axios.get('/api/admin/order/list', {
      headers: {
        Authorization: `Bearer ${token}`
      },
      params: {
        page: 1,
        size: 10
      }
    })
    if (res.data.data && res.data.data.list) {
      newOrders.value = res.data.data.list
    } else {
      newOrders.value = []
    }
  } catch (error) {
    console.error('获取订单失败', error)
    newOrders.value = []
  }
}

const viewOrderDetail = (orderId) => {
  newOrderDialogVisible.value = false
  router.push(`/order/detail/${orderId}`)
}

const initWebSocket = () => {
  const token = localStorage.getItem('admin_token')
  socket = new WebSocket(`ws://localhost:8000/ws/admin/order?admin_token=${token}`)
  
  socket.onopen = () => {
    console.log('WebSocket连接成功')
  }
  
  socket.onclose = () => {
    console.log('WebSocket连接断开')
  }
  
  socket.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      if (data.type === 'new_order') {
        console.log('新订单', data.data)
        newOrderInfo.value = data.data
        newOrderDialogVisible.value = true
        // 刷新数据
        getDashboardData()
        getNewOrders()
      } else if (data.type === 'order_status') {
        console.log('订单状态更新', data.data)
        getNewOrders()
        // 只有当订单状态更新为已支付时才播放提醒音效
        if (data.data.order_status === 2) {
          const audio = new Audio('/alert.mp3')
          audio.play().catch(err => console.error('播放音效失败', err))
        }
      } else if (data.type === 'order_timeout') {
        console.log('订单超时取消', data.data)
        getNewOrders()
      }
    } catch (error) {
      console.error('解析消息失败', error)
    }
  }
}

onMounted(() => {
  getDashboardData()
  getNewOrders()
  initWebSocket()
})

onUnmounted(() => {
  if (socket) {
    socket.close()
  }
})
</script>

<style scoped>
.dashboard-container {
  padding: 24px 0;
  animation: fadeIn 0.5s ease forwards;
}

.page-title {
  font-size: 28px;
  margin-bottom: 24px;
  color: var(--text-primary);
  font-weight: bold;
  display: flex;
  align-items: center;
  position: relative;
  padding-left: 16px;
}

.page-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 8px;
  height: 32px;
  background: var(--gradient-bg);
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(24, 144, 255, 0.3);
}

.data-card {
  margin-bottom: 24px;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  animation: slideUp 0.5s ease forwards;
}

.data-card:nth-child(1) {
  animation-delay: 0.1s;
}

.data-card:nth-child(2) {
  animation-delay: 0.2s;
}

.data-card:nth-child(3) {
  animation-delay: 0.3s;
}

.data-card:nth-child(4) {
  animation-delay: 0.4s;
}

.data-card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  transform: translateY(-8px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background-color: rgba(24, 144, 255, 0.1);
  border-bottom: 1px solid rgba(24, 144, 255, 0.2);
}

.card-header span {
  font-size: 16px;
  font-weight: 500;
  color: var(--text-secondary);
}

.data-value {
  font-size: 36px;
  font-weight: bold;
  color: var(--primary-color);
  text-align: center;
  margin-top: 24px;
  margin-bottom: 24px;
  transition: all 0.3s ease;
}

.data-card:hover .data-value {
  transform: scale(1.05);
  text-shadow: 0 2px 8px rgba(24, 144, 255, 0.3);
}

.order-card {
  margin-top: 24px;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  animation: slideUp 0.5s ease forwards;
  animation-delay: 0.5s;
}

.order-card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  transform: translateY(-4px);
}

.order-card .card-header {
  background-color: rgba(0, 0, 0, 0.05);
  border-bottom: 1px solid var(--border-color);
}

.new-order-info {
  padding: 24px 0;
  animation: fadeIn 0.5s ease forwards;
}

.new-order-info p {
  margin-bottom: 16px;
  font-size: 16px;
  color: var(--text-primary);
  line-height: 1.5;
}

.new-order-info p span {
  font-weight: 500;
  color: var(--text-secondary);
  margin-right: 8px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
}

/* 表格样式 */
:deep(.el-table) {
  border-radius: 8px;
  overflow: hidden;
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
  background-color: rgba(24, 144, 255, 0.05);
}

:deep(.el-button) {
  transition: all 0.3s ease;
  border-radius: 8px;
}

:deep(.el-button:hover) {
  transform: translateY(-2px);
}

:deep(.el-dialog) {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
}

:deep(.el-dialog__header) {
  background-color: rgba(24, 144, 255, 0.1);
  border-bottom: 1px solid rgba(24, 144, 255, 0.2);
}

:deep(.el-dialog__title) {
  font-size: 18px;
  font-weight: 500;
  color: var(--text-primary);
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
  .data-card {
    margin-bottom: 20px;
  }
  
  .data-value {
    font-size: 32px;
  }
  
  .page-title {
    font-size: 24px;
  }
}

@media (max-width: 768px) {
  .dashboard-container {
    padding: 20px 0;
  }
  
  .page-title {
    font-size: 20px;
    margin-bottom: 20px;
  }
  
  .data-value {
    font-size: 28px;
    margin-top: 20px;
    margin-bottom: 20px;
  }
  
  .card-header {
    padding: 12px 16px;
  }
  
  .card-header span {
    font-size: 14px;
  }
  
  .new-order-info p {
    font-size: 14px;
    margin-bottom: 12px;
  }
}
</style>