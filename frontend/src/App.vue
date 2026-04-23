<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AppHeader from './components/layout/AppHeader.vue'
import AppFooter from './components/layout/AppFooter.vue'

const route = useRoute()
const isAdminRoute = computed(() => route.path.startsWith('/admin'))
</script>

<template>
  <!-- Layout admin: sin header ni footer público -->
  <router-view v-if="isAdminRoute" />

  <!-- Layout público -->
  <div v-else class="min-h-screen flex flex-col bg-white">
    <AppHeader />
    <main class="flex-1">
      <router-view v-slot="{ Component }">
        <transition name="page" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
    <AppFooter />
  </div>
</template>
