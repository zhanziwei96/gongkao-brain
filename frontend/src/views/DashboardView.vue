<template>
  <div class="max-w-5xl mx-auto px-6 py-12">
    <h1 class="font-display text-4xl font-medium text-pure-black mb-2" style="line-height: 1.0">
      备考仪表盘
    </h1>
    <p class="text-stone text-lg mb-12">今日目标：行测 80 分</p>

    <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
      <div class="bg-snow border border-light-gray rounded-container p-6">
        <p class="text-stone text-sm mb-2">总题目数</p>
        <p class="font-display text-3xl font-medium text-pure-black">{{ stats.total_questions }}</p>
      </div>
      <div class="bg-snow border border-light-gray rounded-container p-6">
        <p class="text-stone text-sm mb-2">答题次数</p>
        <p class="font-display text-3xl font-medium text-pure-black">{{ stats.total_attempts }}</p>
      </div>
      <div class="bg-snow border border-light-gray rounded-container p-6">
        <p class="text-stone text-sm mb-2">错题数</p>
        <p class="font-display text-3xl font-medium text-pure-black">{{ stats.mistake_count }}</p>
      </div>
      <div class="bg-snow border border-light-gray rounded-container p-6">
        <p class="text-stone text-sm mb-2">正确率</p>
        <p class="font-display text-3xl font-medium text-pure-black">{{ stats.accuracy_rate }}%</p>
      </div>
    </div>

    <div class="bg-pure-white border border-light-gray rounded-container p-6 mb-8">
      <h2 class="font-display text-2xl font-medium text-pure-black mb-6" style="line-height: 1.11">
        各模块正确率
      </h2>
      <div class="space-y-4">
        <div v-for="mod in stats.module_stats" :key="mod.name" class="flex items-center gap-4">
          <span class="w-24 text-sm text-near-black">{{ mod.name }}</span>
          <div class="flex-1 h-2 bg-light-gray rounded-pill overflow-hidden">
            <div
              class="h-full bg-pure-black rounded-pill transition-all duration-500"
              :style="{ width: mod.rate + '%' }"
            />
          </div>
          <span class="w-20 text-right text-sm text-stone">
            {{ mod.correct_count }}/{{ mod.attempt_count }}
          </span>
          <span class="w-12 text-right text-sm text-near-black font-medium">
            {{ mod.rate }}%
          </span>
        </div>
      </div>
    </div>

    <div class="flex gap-4">
      <router-link
        to="/aptitude/questions/new"
        class="px-6 py-3 bg-pure-black text-pure-white rounded-pill text-base font-medium transition-colors hover:bg-near-black"
      >
        录入新题
      </router-link>
      <router-link
        to="/aptitude/questions"
        class="px-6 py-3 bg-light-gray text-near-black rounded-pill text-base font-medium transition-colors hover:bg-border-light"
      >
        查看错题
      </router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, onMounted, onUnmounted } from 'vue'
import client from '../api/client'

interface ModuleStat {
  name: string
  question_count: number
  attempt_count: number
  correct_count: number
  rate: number
}

interface Stats {
  total_questions: number
  total_attempts: number
  correct_count: number
  mistake_count: number
  accuracy_rate: number
  module_stats: ModuleStat[]
}

const stats = reactive<Stats>({
  total_questions: 0,
  total_attempts: 0,
  correct_count: 0,
  mistake_count: 0,
  accuracy_rate: 0,
  module_stats: []
})

const fetchStats = async () => {
  try {
    const res = await client.get('/aptitude/stats')
    Object.assign(stats, res.data)
  } catch (err) {
    console.error('获取统计数据失败', err)
  }
}

onMounted(() => {
  fetchStats()
  window.addEventListener('aptitude-stats-updated', fetchStats)
})

onUnmounted(() => {
  window.removeEventListener('aptitude-stats-updated', fetchStats)
})
</script>
