<template>
  <div class="product-add">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>添加商品</span>
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
            ></el-option