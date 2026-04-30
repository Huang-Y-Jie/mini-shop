<template>
  <div class="product-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>商品管理</span>
          <el-button type="primary" @click="openAddModal">添加商品</el-button>
        </div>
      </template>
      
      <div class="search-bar">
        <el-input v-model="searchForm.keyword" placeholder="商品名称" style="width: 200px; margin-right: 10px;"></el-input>
        <el-select v-model="searchForm.status" placeholder="商品状态" style="width: 120px; margin-right: 10px;">
          <el-option label="全部" value=""></el-option>
          <el-option label="上架" value="1"></el-option>
          <el-option label="下架" value="0"></el-option>
        </el-select>
        <el-button type="primary" @click="search">搜索</el-button>
      </div>
      
      <el-table :data="productList" style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="商品ID" width="80"></el-table-column>
        <el-table-column label="商品名称">
          <template #default="scope">
            <div class="product-name">
              <span>{{ scope.row.name }}</span>
              <el-tag size="small" type="info" class="category-tag">{{ scope.row.category_name }}</el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="price" label="价格" width="100"></el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.status === 1 ? 'success' : 'info'">
              {{ scope.row.status === 1 ? '上架' : '下架' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="创建时间" width="180"></el-table-column>
        <el-table-column label="操作" width="300">
          <template #default="scope">
            <div class="action-buttons">
              <el-button size="small" @click="navigateToEdit(scope.row.id)">编辑</el-button>
              <el-button size="small" type="danger" @click="deleteProduct(scope.row.id)">删除</el-button>
              <el-button size="small" @click="toggleStatus(scope.row.id, scope.row.status)">
                {{ scope.row.status === 1 ? '下架' : '上架' }}
              </el-button>
            </div>
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
    
    <!-- 新增商品模态框 -->
    <el-dialog
      v-model="addDialogVisible"
      title="添加商品"
      width="800px"
    >
      <el-form :model="productForm" label-width="100px">
        <el-form-item label="商品名称">
          <el-input v-model="productForm.name" placeholder="请输入商品名称"></el-input>
        </el-form-item>
        
        <el-form-item label="商品分类">
          <el-select v-model="productForm.category_id" placeholder="请选择商品分类">
            <el-option 
              v-for="category in categories" 
              :key="category.id" 
              :label="category.name" 
              :value="category.id"
            ></el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item label="商品价格">
          <el-input v-model.number="productForm.price" type="number" placeholder="请输入商品价格"></el-input>
        </el-form-item>
        
        <el-form-item label="商品描述">
          <el-input 
            v-model="productForm.desc" 
            type="textarea" 
            placeholder="请输入商品描述" 
            :rows="3"
          ></el-input>
        </el-form-item>
        
        <el-form-item label="封面图片">
          <el-upload
            class="upload-demo"
            action=""
            :auto-upload="false"
            :on-change="handleCoverImageChange"
            :show-file-list="false"
          >
            <el-button type="primary">选择图片</el-button>
          </el-upload>
          <div v-if="productForm.cover_img" class="image-preview">
            <img :src="productForm.cover_img" alt="封面图片" style="width: 200px; height: 200px; object-fit: cover;">
            <el-button type="danger" size="small" @click="productForm.cover_img = ''">删除</el-button>
          </div>
        </el-form-item>
        
        <el-form-item label="商品图片">
          <el-upload
            class="upload-demo"
            action=""
            :auto-upload="false"
            :on-change="handleImagesChange"
            multiple
          >
            <el-button type="primary">选择图片</el-button>
          </el-upload>
          <div v-if="productForm.imgs && productForm.imgs.length > 0" class="images-preview">
            <div v-for="(img, index) in productForm.imgs" :key="index" class="image-item">
              <img :src="img" alt="商品图片" style="width: 100px; height: 100px; object-fit: cover;">
              <el-button type="danger" size="small" @click="productForm.imgs.splice(index, 1)">删除</el-button>
            </div>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="addDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm">提交</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';

const router = useRouter();
const productList = ref([]);
const loading = ref(false);
const searchForm = ref({
  keyword: '',
  status: ''
});
const pagination = ref({
  currentPage: 1,
  pageSize: 10,
  total: 0
});

// 新增商品模态框相关
const addDialogVisible = ref(false);
const productForm = ref({
  name: '',
  category_id: '',
  price: '',
  desc: '',
  cover_img: '',
  imgs: []
});
const categories = ref([]);

// 打开新增商品模态框
const openAddModal = () => {
  // 重置表单
  productForm.value = {
    name: '',
    category_id: '',
    price: '',
    desc: '',
    cover_img: '',
    imgs: []
  };
  // 打开模态框
  addDialogVisible.value = true;
};

// 导航到编辑商品页面
const navigateToEdit = (id) => {
  router.push(`/product/edit/${id}`);
};

// 搜索商品
const search = () => {
  getProductList();
};

// 获取商品列表
const getProductList = async () => {
  loading.value = true;
  try {
    const response = await axios.get('/api/admin/product/list', {
      params: {
        keyword: searchForm.value.keyword,
        status: searchForm.value.status,
        page: pagination.value.currentPage,
        size: pagination.value.pageSize
      },
      headers: {
        Authorization: `Bearer ${localStorage.getItem('admin_token')}`
      }
    });
    if (response.data.code === 200) {
      productList.value = response.data.data.list;
      pagination.value.total = response.data.data.total;
    }
  } catch (error) {
    console.error('获取商品列表失败:', error);
  } finally {
    loading.value = false;
  }
};

// 切换商品状态
const toggleStatus = async (id, status) => {
  try {
    const response = await axios.put(`/api/admin/product/${id}/status`, {
      status: status === 1 ? 0 : 1
    }, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('admin_token')}`
      }
    });
    if (response.data.code === 200) {
      getProductList();
    }
  } catch (error) {
    console.error('切换商品状态失败:', error);
  }
};

// 删除商品
const deleteProduct = async (id) => {
  try {
    const response = await axios.delete(`/api/admin/product/${id}`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('admin_token')}`
      }
    });
    if (response.data.code === 200) {
      getProductList();
    }
  } catch (error) {
    console.error('删除商品失败:', error);
  }
};

// 处理分页大小变化
const handleSizeChange = (size) => {
  pagination.value.pageSize = size;
  getProductList();
};

// 处理当前页变化
const handleCurrentChange = (current) => {
  pagination.value.currentPage = current;
  getProductList();
};

// 获取分类列表
const getCategories = async () => {
  try {
    const response = await axios.get('/api/admin/category/list', {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('admin_token')}`
      }
    });
    if (response.data.code === 200) {
      categories.value = response.data.data;
    }
  } catch (error) {
    console.error('获取分类列表失败:', error);
  }
};

// 处理封面图片选择
const handleCoverImageChange = async (file) => {
  try {
    // 创建FormData对象
    const formData = new FormData();
    formData.append('file', file.raw);
    
    // 调用上传接口
    const response = await axios.post('/api/upload/image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        Authorization: `Bearer ${localStorage.getItem('admin_token')}`
      }
    });
    
    if (response.data.code === 200) {
      productForm.value.cover_img = response.data.data.url;
    }
  } catch (error) {
    console.error('上传封面图片失败:', error);
  }
};

// 处理商品图片选择
const handleImagesChange = async (file) => {
  try {
    // 创建FormData对象
    const formData = new FormData();
    formData.append('file', file.raw);
    
    // 调用上传接口
    const response = await axios.post('/api/upload/image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        Authorization: `Bearer ${localStorage.getItem('admin_token')}`
      }
    });
    
    if (response.data.code === 200) {
      productForm.value.imgs.push(response.data.data.url);
    }
  } catch (error) {
    console.error('上传商品图片失败:', error);
  }
};

// 提交表单
const submitForm = async () => {
  try {
    const response = await axios.post('/api/admin/product/add', {
      name: productForm.value.name,
      category_id: productForm.value.category_id,
      price: productForm.value.price,
      desc: productForm.value.desc,
      cover_img: productForm.value.cover_img,
      imgs: productForm.value.imgs
    }, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('admin_token')}`
      }
    });
    if (response.data.code === 200) {
      // 关闭模态框
      addDialogVisible.value = false;
      // 刷新商品列表
      getProductList();
    }
  } catch (error) {
    console.error('添加商品失败:', error);
  }
};

// 页面挂载时获取商品列表和分类列表
onMounted(() => {
  getProductList();
  getCategories();
});
</script>

<style scoped>
.product-list {
  padding: 0;
  animation: fadeIn 0.5s ease forwards;
  height: 100%;
  overflow-y: auto;
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

/* 商品名称和分类标签样式 */
.product-name {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.product-name span {
  font-weight: 500;
}

.category-tag {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 4px;
  background-color: rgba(24, 144, 255, 0.1);
  color: var(--primary-color);
  border: 1px solid rgba(24, 144, 255, 0.2);
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

.image-preview {
  margin-top: 16px;
  padding: 16px;
  background-color: rgba(0, 0, 0, 0.02);
  border-radius: 8px;
  transition: all 0.3s ease;
  display: inline-block;
}

.image-preview:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.images-preview {
  display: flex;
  flex-wrap: wrap;
  margin-top: 16px;
  gap: 16px;
}

.image-item {
  margin-right: 0;
  margin-bottom: 0;
  position: relative;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.image-item:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  transform: translateY(-4px);
}

.image-item img {
  border-radius: 8px;
  transition: all 0.3s ease;
}

.image-item:hover img {
  transform: scale(1.05);
}

.image-item button {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  border-radius: 0 0 8px 8px;
  opacity: 0;
  transition: all 0.3s ease;
}

.image-item:hover button {
  opacity: 1;
  transform: translateY(0);
}

/* 操作按钮样式 */
.action-buttons {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: nowrap;
}

/* 表格样式 */
:deep(.el-table) {
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  animation: slideUp 0.5s ease forwards;
  animation-delay: 0.3s;
  margin-bottom: 24px;
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

:deep(.el-upload) {
  transition: all 0.3s ease;
}

:deep(.el-upload:hover) {
  transform: translateY(-2px);
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
  .product-list {
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
  .product-list {
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
  
  .images-preview {
    gap: 12px;
  }
  
  .image-item {
    width: calc(50% - 6px);
  }
  
  .image-item img {
    width: 100% !important;
    height: auto !important;
  }
}
</style>