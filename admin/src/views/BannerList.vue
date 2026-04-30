<template>
  <div class="banner-list">
    <div class="page-header">
      <h2>轮播图管理</h2>
      <el-button type="primary" @click="handleAddBanner" class="add-btn">
        <el-icon><Plus /></el-icon>
        添加轮播图
      </el-button>
    </div>

    <div class="card">
      <el-table :data="bannerList" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column label="图片" width="150">
          <template #default="scope">
            <el-image
              :src="scope.row.image.replace('http://localhost:8000', 'http://localhost:8002')"
              fit="cover"
              style="width: 100px; height: 50px; border-radius: 4px"
            />
          </template>
        </el-table-column>
        <el-table-column prop="title" label="标题" />
        <el-table-column prop="subtitle" label="副标题" />
        <el-table-column prop="link" label="链接" />
        <el-table-column prop="sort" label="排序" width="80" />
        <el-table-column prop="status" label="状态" width="80">
          <template #default="scope">
            <el-switch
              v-model="scope.row.status"
              active-color="#1890ff"
              inactive-color="#d9d9d9"
              @change="handleStatusChange(scope.row)"
            />
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="180">
          <template #default="scope">
            <el-button type="primary" size="small" @click="handleEditBanner(scope.row)">
              编辑
            </el-button>
            <el-button type="danger" size="small" @click="handleDeleteBanner(scope.row.id)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- 添加/编辑轮播图对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="500px"
    >
      <el-form :model="formData" label-width="80px">
        <el-form-item label="标题" required>
          <el-input v-model="formData.title" placeholder="请输入轮播图标题" />
        </el-form-item>
        <el-form-item label="副标题" required>
          <el-input v-model="formData.subtitle" placeholder="请输入轮播图副标题" />
        </el-form-item>
        <el-form-item label="图片" required>
          <el-upload
            class="avatar-uploader"
            :action="uploadUrl"
            :show-file-list="false"
            :on-success="handleImageUpload"
            :before-upload="beforeUpload"
          >
            <img v-if="formData.image" :src="formData.image.replace('http://localhost:8000', 'http://localhost:8002')" class="avatar" />
            <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
          </el-upload>
          <div class="upload-tip">请上传轮播图图片，建议尺寸：750x350px</div>
        </el-form-item>
        <el-form-item label="链接">
          <el-input v-model="formData.link" placeholder="请输入轮播图链接（可选）" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="formData.sort" :min="0" :step="1" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="formData.status" active-color="#1890ff" inactive-color="#d9d9d9" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const bannerList = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const dialogVisible = ref(false)
const dialogTitle = ref('添加轮播图')
const formData = ref({
  title: '',
  subtitle: '',
  image: '',
  link: '',
  sort: 0,
  status: true
})
const uploadUrl = '/api/upload/image' // 使用配置的上传接口

// 获取轮播图列表
const getBannerList = async () => {
  try {
    const token = localStorage.getItem('admin_token')
    const res = await axios.get('/api/banner/admin/list', {
      params: {
        page: currentPage.value,
        size: pageSize.value
      },
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
    if (res.data.code === 200) {
      bannerList.value = res.data.data.list
      total.value = res.data.data.total
    }
  } catch (error) {
    console.error('获取轮播图列表失败', error)
  }
}

// 处理页码变化
const handleSizeChange = (size) => {
  pageSize.value = size
  getBannerList()
}

const handleCurrentChange = (current) => {
  currentPage.value = current
  getBannerList()
}

// 处理添加轮播图
const handleAddBanner = () => {
  dialogTitle.value = '添加轮播图'
  formData.value = {
    title: '',
    subtitle: '',
    image: '',
    link: '',
    sort: 0,
    status: true
  }
  dialogVisible.value = true
}

// 处理编辑轮播图
const handleEditBanner = (banner) => {
  dialogTitle.value = '编辑轮播图'
  formData.value = {
    id: banner.id,
    title: banner.title,
    subtitle: banner.subtitle,
    image: banner.image,
    link: banner.link,
    sort: banner.sort,
    status: banner.status
  }
  dialogVisible.value = true
}

// 处理提交
const handleSubmit = async () => {
  try {
    // 检查图片是否已上传
    if (!formData.value.image) {
      ElMessage.error('请上传轮播图图片')
      return
    }
    
    const token = localStorage.getItem('admin_token')
    let res
    
    if (formData.value.id) {
      // 更新轮播图
      res = await axios.put(`/api/banner/admin/update/${formData.value.id}`, formData.value, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      })
    } else {
      // 添加轮播图
      res = await axios.post('/api/banner/admin/add', formData.value, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      })
    }
    
    if (res.data.code === 200) {
      ElMessage.success('操作成功')
      dialogVisible.value = false
      getBannerList()
    }
  } catch (error) {
    console.error('提交失败', error)
    ElMessage.error('操作失败，请重试')
  }
}

// 处理删除轮播图
const handleDeleteBanner = async (id) => {
  try {
    const token = localStorage.getItem('admin_token')
    const res = await axios.delete(`/api/banner/admin/delete/${id}`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
    if (res.data.code === 200) {
      getBannerList()
    }
  } catch (error) {
    console.error('删除失败', error)
  }
}

// 处理状态变化
const handleStatusChange = async (banner) => {
  try {
    const token = localStorage.getItem('admin_token')
    await axios.put(`/api/banner/admin/update/${banner.id}`, {
      status: banner.status
    }, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
  } catch (error) {
    console.error('更新状态失败', error)
    getBannerList() // 失败后刷新列表
  }
}

// 处理图片上传
const handleImageUpload = (response) => {
  if (response.code === 200) {
    formData.value.image = response.data.url
  }
}

// 上传前检查
const beforeUpload = (file) => {
  const isJPG = file.type === 'image/jpeg' || file.type === 'image/png'
  const isLt2M = file.size / 1024 / 1024 < 2
  
  if (!isJPG) {
    ElMessage.error('只能上传 JPG/PNG 图片')
    return false
  }
  if (!isLt2M) {
    ElMessage.error('图片大小不能超过 2MB')
    return false
  }
  
  return true // 允许自动上传
}

// 页面挂载时获取数据
onMounted(() => {
  getBannerList()
})
</script>

<style scoped>
.banner-list {
  padding: 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h2 {
  font-size: 24px;
  font-weight: bold;
  color: var(--text-primary);
  margin: 0;
}

.add-btn {
  display: flex;
  align-items: center;
}

.card {
  background-color: var(--white);
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  padding: 24px;
}

.pagination-container {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
}

.avatar-uploader {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 200px;
  height: 100px;
  border: 1px dashed var(--border-color);
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
}

.avatar-uploader:hover {
  border-color: var(--primary-color);
}

.avatar-uploader-icon {
  font-size: 32px;
  color: var(--text-light);
}

.avatar {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.upload-tip {
  margin-top: 8px;
  font-size: 14px;
  color: var(--text-light);
}

.dialog-footer {
  width: 100%;
  display: flex;
  justify-content: flex-end;
}
</style>