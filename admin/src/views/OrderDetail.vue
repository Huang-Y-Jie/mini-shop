<template>
  <div class="order-detail">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>订单详情</span>
          <el-button @click="navigateBack">返回</el-button>
        </div>
      </template>
      
      <el-form :model="orderDetail" label-width="100px" style="max-width: 800px;" v-loading="loading">
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
            <el-table-column prop="price" label="单价"></el-table-column>
          </el-table>
        </el-form-item>
        <el-form-item>
          <el-button type="danger" @click="cancelOrder" :disabled="orderDetail.order_status !== 1">取消订单</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import axios from 'axios';

const router = useRouter();
const route = useRoute();
const orderDetail = ref({});
const loading = ref(false);
const orderId = ref(route.params.id);

// 导航返回
const navigateBack = () => {
  router.push('/order/list');
};

// 获取订单详情
const getOrderDetail = async () => {
  loading.value = true;
  try {
    const response = await axios.get(`/api/admin/order/${orderId.value}`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('admin_token')}`
      }
    });
    if (response.data.code === 200) {
      const data = response.data.data;
      orderDetail.value = {
        ...data,
        pay_status_text: data.pay_status === 0 ? '未支付' : data.pay_status === 1 ? '已支付' : '退款',
        order_status_text: data.order_status === 1 ? '待支付' : data.order_status === 2 ? '已支付' : data.order_status === 3 ? '已完成' : (data.order_status === 4 || data.order_status === 5) ? '已取消' : '待支付'
      };
    }
  } catch (error) {
    console.error('获取订单详情失败:', error);
  } finally {
    loading.value = false;
  }
};

// 取消订单
const cancelOrder = async () => {
  try {
    const response = await axios.put(`/api/admin/order/${orderId.value}/cancel`, {}, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('admin_token')}`
      }
    });
    if (response.data.code === 200) {
      getOrderDetail();
    }
  } catch (error) {
    console.error('取消订单失败:', error);
  }
};

// 页面挂载时获取订单详情
onMounted(() => {
  getOrderDetail();
});
</script>

<style scoped>
.order-detail {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>