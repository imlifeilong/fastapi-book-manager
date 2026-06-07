import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'
import NProgress from 'nprogress'
import 'nprogress/nprogress.css'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/index.vue'),
    meta: { public: true }
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/index.vue'),
        meta: { title: '数据概览', icon: 'DataLine' }
      },
      {
        path: 'books',
        name: 'Books',
        component: () => import('@/views/books/index.vue'),
        meta: { title: '图书管理', icon: 'Reading' }
      },
      {
        path: 'borrows',
        name: 'Borrows',
        component: () => import('@/views/borrows/index.vue'),
        meta: { title: '借阅管理', icon: 'Collection' }
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('@/views/users/index.vue'),
        meta: { title: '用户管理', icon: 'User', admin: true }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

NProgress.configure({ showSpinner: false })

router.beforeEach(async (to, from, next) => {
  NProgress.start()
  const userStore = useUserStore()

  if (to.meta.public) {
    next()
    return
  }

  if (!userStore.isLoggedIn) {
    next('/login')
    return
  }

  if (!userStore.userInfo) {
    await userStore.fetchUserInfo()
  }

  if (to.meta.admin && !userStore.isAdmin) {
    next('/dashboard')
    return
  }

  next()
})

router.afterEach(() => {
  NProgress.done()
})

export default router
