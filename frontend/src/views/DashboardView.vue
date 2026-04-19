<template>
  <div class="max-w-5xl mx-auto px-6 py-12">
    <h1 class="font-display text-4xl font-medium text-pure-black mb-2" style="line-height: 1.0">
      备考仪表盘
    </h1>
    <p class="text-stone text-lg mb-12">今日目标：行测 80 分</p>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
      <div class="bg-snow border border-light-gray rounded-container p-6">
        <p class="text-stone text-sm mb-2">总题目数</p>
        <p class="font-display text-3xl font-medium text-pure-black">{{ stats.total }}</p>
      </div>
      <div class="bg-snow border border-light-gray rounded-container p-6">
        <p class="text-stone text-sm mb-2">错题数</p>
        <p class="font-display text-3xl font-medium text-pure-black">{{ stats.mistakes }}</p>
      </div>
      <div class="bg-snow border border-light-gray rounded-container p-6">
        <p class="text-stone text-sm mb-2">正确率</p>
        <p class="font-display text-3xl font-medium text-pure-black">{{ stats.accuracy }}%</p>
      </div>
    </div>

    <div class="bg-pure-white border border-light-gray rounded-container p-6 mb-8">
      <h2 class="font-display text-2xl font-medium text-pure-black mb-6" style="line-height: 1.11">各模块进度</h2>
      <div class="space-y-4">
        <div v-for="mod in modules" :key="mod.name" class="flex items-center gap-4">
          <span class="w-24 text-sm text-near-black">{{ mod.name }}</span>
          <div class="flex-1 h-2 bg-light-gray rounded-pill overflow-hidden">
            <div class="h-full bg-pure-black rounded-pill" :style="{ width: mod.rate + '%' }"></div>
          </div>
          <span class="w-12 text-right text-sm text-stone">{{ mod.rate }}%</span>
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
import { reactive } from 'vue'

const stats = reactive({ total: 0, mistakes: 0, accuracy: 0 })

const modules = [
  { name: '政治理论', rate: 0 },
  { name: '常识判断', rate: 0 },
  { name: '言语理解', rate: 0 },
  { name: '数量关系', rate: 0 },
  { name: '判断推理', rate: 0 },
  { name: '资料分析', rate: 0 },
]
</script>
