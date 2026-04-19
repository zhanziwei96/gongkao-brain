<template>
  <div class="min-h-screen bg-pure-white">
    <NavigationMenu v-if="isLoggedIn" />
    <router-view />
    <ChatPanel v-if="isLoggedIn" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import NavigationMenu from './components/NavigationMenu.vue'
import ChatPanel from './components/ChatPanel.vue'

const isLoggedIn = computed(() => !!localStorage.getItem('token'))
</script>
