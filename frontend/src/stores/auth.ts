import { defineStore } from 'pinia'
import { ref } from 'vue'
import { authApi } from '../api/auth'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const username = ref('')

  const login = async (username: string, password: string) => {
    const res = await authApi.login({ username, password })
    token.value = res.data.access_token
    localStorage.setItem('token', token.value)
    return res.data
  }

  const register = async (username: string, email: string, password: string) => {
    const res = await authApi.register({ username, email, password })
    return res.data
  }

  const logout = () => {
    token.value = ''
    localStorage.removeItem('token')
    window.location.href = '/login'
  }

  return { token, username, login, register, logout }
})
