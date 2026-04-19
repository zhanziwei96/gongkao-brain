<template>
  <div class="min-h-screen bg-pure-white flex items-center justify-center px-4">
    <div class="w-full max-w-sm">
      <h1 class="font-display text-4xl font-medium text-pure-black text-center mb-12" style="line-height: 1.0">
        公考大脑
      </h1>
      <form @submit.prevent="handleLogin" class="space-y-4">
        <div>
          <input
            v-model="form.username"
            type="text"
            placeholder="用户名"
            class="w-full px-6 py-3 bg-pure-white border border-light-gray rounded-pill text-near-black placeholder-silver text-base focus:outline-none focus:ring-2 focus:ring-[#3b82f6] focus:ring-opacity-50"
          />
        </div>
        <div>
          <input
            v-model="form.password"
            type="password"
            placeholder="密码"
            class="w-full px-6 py-3 bg-pure-white border border-light-gray rounded-pill text-near-black placeholder-silver text-base focus:outline-none focus:ring-2 focus:ring-[#3b82f6] focus:ring-opacity-50"
          />
        </div>
        <button
          type="submit"
          class="w-full px-6 py-3 bg-pure-black text-pure-white rounded-pill text-base font-medium transition-colors hover:bg-near-black"
        >
          登录
        </button>
      </form>
      <p class="text-center mt-6 text-stone text-sm">
        没有账号？
        <router-link to="/register" class="text-pure-black underline">立即注册</router-link>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const form = reactive({ username: '', password: '' })

const handleLogin = async () => {
  try {
    await authStore.login(form.username, form.password)
    router.push('/')
  } catch (err: any) {
    alert(err.response?.data?.detail || '登录失败')
  }
}
</script>
