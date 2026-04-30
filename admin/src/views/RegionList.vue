<template>
  <div class="region-list-container">
    <el-card class="page-card">
      <template #header>
        <div class="card-header">
          <h1>地区运费管理</h1>
          <el-button type="primary" @click="addRegion" icon="Plus">添加地区</el-button>
        </div>
      </template>
      
      <el-table :data="regions" style="width: 100%" border>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="region_name" label="地区名称" width="200" />
        <el-table-column prop="shipping_fee" label="运费" width="120" />
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.is_active ? 'success' : 'danger'">
              {{ scope.row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="创建时间" width="200" />
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button type="primary" size="small" @click="editRegion(scope.row)" icon="Edit">编辑</el-button>
            <el-button type="danger" size="small" @click="deleteRegion(scope.row.id)" icon="Delete">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 添加/编辑地区对话框 -->
    <el-dialog
      :title="dialogTitle"
      v-model="dialogVisible"
      width="500px"
    >
      <el-form :model="formData" label-width="120px">
        <el-form-item label="地区名称">
          <el-input v-model="formData.region_name" placeholder="请输入地区名称" />
        </el-form-item>
        <el-form-item label="运费金额">
          <el-input v-model="formData.shipping_fee" type="number" placeholder="请输入运费金额" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="formData.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveRegion">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import api from '../utils/api'

export default {
  data() {
    return {
      regions: [],
      dialogVisible: false,
      dialogTitle: '添加地区',
      formData: {
        id: '',
        region_name: '',
        shipping_fee: '',
        is_active: true
      }
    }
  },
  mounted() {
    this.getRegions()
  },
  methods: {
    async getRegions() {
      try {
        const response = await api.get('/region/list')
        if (response.code === 200) {
          this.regions = response.data
        }
      } catch (error) {
        console.error('获取地区列表失败:', error)
        this.$message.error('获取地区列表失败')
      }
    },
    addRegion() {
      this.dialogTitle = '添加地区'
      this.formData = {
        id: '',
        region_name: '',
        shipping_fee: '',
        is_active: true
      }
      this.dialogVisible = true
    },
    editRegion(region) {
      this.dialogTitle = '编辑地区'
      this.formData = {
        id: region.id,
        region_name: region.region_name,
        shipping_fee: region.shipping_fee,
        is_active: region.is_active
      }
      this.dialogVisible = true
    },
    async saveRegion() {
      try {
        if (!this.formData.region_name) {
          this.$message.error('请输入地区名称')
          return
        }
        if (this.formData.shipping_fee === undefined || this.formData.shipping_fee === null) {
          this.$message.error('请输入运费金额')
          return
        }
        
        let response
        if (this.formData.id) {
          // 编辑
          response = await api.put(`/region/${this.formData.id}`, this.formData)
        } else {
          // 添加
          response = await api.post('/region', this.formData)
        }
        
        if (response.code === 200) {
          this.$message.success(this.formData.id ? '更新成功' : '添加成功')
          this.dialogVisible = false
          this.getRegions()
        }
      } catch (error) {
        console.error('保存地区失败:', error)
        this.$message.error('保存地区失败')
      }
    },
    async deleteRegion(id) {
      try {
        await this.$confirm('确定要删除这个地区吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        
        const response = await api.delete(`/region/${id}`)
        if (response.code === 200) {
          this.$message.success('删除成功')
          this.getRegions()
        }
      } catch (error) {
        console.error('删除地区失败:', error)
        if (error !== 'cancel') {
          this.$message.error('删除地区失败')
        }
      }
    }
  }
}
</script>

<style scoped>
.region-list-container {
  padding: 20px;
}

.page-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h1 {
  font-size: 24px;
  margin: 0;
  color: #333;
}

.dialog-footer {
  width: 100%;
  display: flex;
  justify-content: flex-end;
}
</style>