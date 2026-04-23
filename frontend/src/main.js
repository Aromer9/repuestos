import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import './assets/styles/main.css'

import HomeView from './views/HomeView.vue'
import CatalogView from './views/CatalogView.vue'
import ProductDetailView from './views/ProductDetailView.vue'
import InquiryView from './views/InquiryView.vue'
import AdminLoginView from './views/admin/AdminLoginView.vue'
import AdminDashboardView from './views/admin/AdminDashboardView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/catalogo', name: 'catalog', component: CatalogView },
    { path: '/producto/:id', name: 'product-detail', component: ProductDetailView },
    { path: '/cotizar', name: 'inquiry', component: InquiryView },

    { path: '/admin/login', name: 'admin-login', component: AdminLoginView },
    {
      path: '/admin',
      name: 'admin',
      component: AdminDashboardView,
      meta: { requiresAuth: true },
    },
  ],
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) return savedPosition
    return { top: 0, behavior: 'smooth' }
  },
})

router.beforeEach((to) => {
  if (to.meta.requiresAuth) {
    const token = localStorage.getItem('argparts_token')
    if (!token) return { name: 'admin-login' }
  }
  if (to.name === 'admin-login') {
    const token = localStorage.getItem('argparts_token')
    if (token) return { name: 'admin' }
  }
})

createApp(App).use(router).mount('#app')
