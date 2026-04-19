<template>
  <div class="min-h-screen bg-pure-white flex items-center justify-center px-4">
    <div class="w-full max-w-sm">
      <h1 class="font-display text-4xl font-medium text-pure-black text-center mb-12" style="line-height: 1.0">
        注册账号
      </h1>
      <form @submit.prevent="handleRegister" class="space-y-4">
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
            v-model="form.email"
            type="email"
            placeholder="邮箱"
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
          注册
        </button>
      </form>
      <p class="text-center mt-6 text-stone text-sm">
        已有账号？
        <router-link to="/login" class="text-pure-black underline">去登录</router-link>
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

const form = reactive({ username: '', email: '', password: '' })

const handleRegister = async () => {
  try {
    await authStore.register(form.username, form.email, form.password)
    alert('注册成功，请登录')
    router.push('/login')
  } catch (err: any) {
    alert(err.response?.data?.detail || '注册失败')
  }
}
</script>
