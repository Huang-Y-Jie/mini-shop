<template>
  <div class="product-edit">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>编辑商品</span>
          <el-button @click="navigateBack">返回</el-button>
        </div>
      </template>
      
      <el-form :model="productForm" label-width="100px" style="max-width: 800px;" v-loading="loading">
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
        
        <el-form-item>
          <el-button type="primary" @click="submitForm">提交</el-button>
          <el-button @click="resetForm">重置</el-button>
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
const productForm = ref({
  name: '',
  category_id: '',
  price: '',
  desc: '',
  cover_img: '',
  imgs: []
});
const categories = ref([]);
const loading = ref(false);
const productId = ref(route.params.id);

// 导航返回
const navigateBack = () => {
  router.push('/product/list');
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

// 获取商品详情
const getProductDetail = async () => {
  loading.value = true;
  try {
    const response = await axios.get(`/api/product/detail/${productId.value}`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('admin_token')}`
      }
    });
    if (response.data.code === 200) {
      productForm.value = {
        name: response.data.data.name,
        category_id: response.data.data.category_id,
        price: response.data.data.price,
        desc: response.data.data.desc,
        cover_img: response.data.data.cover_img,
        imgs: response.data.data.imgs
      };
    }
  } catch (error) {
    console.error('获取商品详情失败:', error);
  } finally {
    loading.value = false;
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
    const response = await axios.put(`/api/admin/product/${productId.value}`, {
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
      router.push('/product/list');
    }
  } catch (error) {
    console.error('编辑商品失败:', error);
  }
};

// 重置表单
const resetForm = () => {
  getProductDetail();
};

// 页面挂载时获取数据
onMounted(() => {
  getCategories();
  getProductDetail();
});
</script>

<style scoped>
.product-edit {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.image-preview {
  margin-top: 10px;
}

.images-preview {
  display: flex;
  flex-wrap: wrap;
  margin-top: 10px;
}

.image-item {
  margin-right: 10px;
  margin-bottom: 10px;
  position: relative;
}

.image-item button {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
}
</style>