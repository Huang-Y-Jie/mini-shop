import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('./views/Login.vue')
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('./views/Dashboard.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/product/list',
    name: 'ProductList',
    component: () => import('./views/ProductList.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/product/add',
    name: 'ProductAdd',
    component: () => import('./views/ProductAdd.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/product/edit/:id',
    name: 'ProductEdit',
    component: () => import('./views/ProductEdit.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/category/list',
    name: 'CategoryList',
    component: () => import('./views/CategoryList.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/user/list',
    name: 'UserList',
    component: () => import('./views/UserList.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/order/list',
    name: 'OrderList',
    component: () => import('./views/OrderList.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/order/detail/:id',
    name: 'OrderDetail',
    component: () => import('./views/OrderDetail.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/pay/list',
    name: 'PayList',
    component: () => import('./views/PayList.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('./views/Profile.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/banner/list',
    name: 'BannerList',
    component: () => import('./views/BannerList.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/region/list',
    name: 'RegionList',
    component: () => import('./views/RegionList.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('admin_token')
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router