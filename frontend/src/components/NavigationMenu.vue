<template>
  <nav class="w-full bg-pure-white border-b border-light-gray">
    <div class="max-w-5xl mx-auto px-6 h-14 flex items-center justify-between">
      <div class="flex items-center gap-8">
        <router-link to="/" class="font-display text-xl font-medium text-pure-black">公考大脑</router-link>
        <div class="hidden md:flex items-center gap-1">
          <router-link
            v-for="link in links"
            :key="link.to"
            :to="link.to"
            class="px-4 py-2 rounded-pill text-sm text-near-black transition-colors hover:bg-light-gray"
            :class="{ 'bg-light-gray': $route.path === link.to }"
          >
            {{ link.label }}
          </router-link>
        </div>
      </div>
      <div class="flex items-center gap-3">
        <span class="text-sm text-stone hidden sm:inline">{{ authStore.token ? '已登录' : '' }}</span>
        <button
          @click="authStore.logout"
          class="px-5 py-2 bg-light-gray text-near-black rounded-pill text-sm transition-colors hover:bg-border-light"
        >
          退出
        </button>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()

const links = [
  { to: '/', label: '仪表盘' },
  { to: '/aptitude/questions', label: '行测错题' },
]
</script>
