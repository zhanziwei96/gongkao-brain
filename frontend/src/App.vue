<template>
  <div class="min-h-screen bg-pure-white">
    <NavigationMenu v-if="authStore.token" />
    <router-view />
    <ChatPanel v-if="authStore.token" />
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from './stores/auth'
import NavigationMenu from './components/NavigationMenu.vue'
import ChatPanel from './components/ChatPanel.vue'

const authStore = useAuthStore()
</script>
