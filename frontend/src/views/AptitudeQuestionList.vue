<template>
  <div class="max-w-5xl mx-auto px-6 py-12">
    <div class="flex items-center justify-between mb-8">
      <h1 class="font-display text-4xl font-medium text-pure-black" style="line-height: 1.0">
        行测错题
      </h1>
      <router-link
        to="/aptitude/questions/new"
        class="px-6 py-3 bg-pure-black text-pure-white rounded-pill text-base font-medium transition-colors hover:bg-near-black"
      >
        录入新题
      </router-link>
    </div>

    <div class="flex gap-2 mb-6 flex-wrap">
      <button
        v-for="type in questionTypes"
        :key="type"
        @click="filterType = type"
        :class="[
          'px-5 py-2 rounded-pill text-sm transition-colors',
          filterType === type
            ? 'bg-light-gray text-near-black'
            : 'bg-pure-white text-stone border border-light-gray hover:bg-snow'
        ]"
      >
        {{ type || '全部' }}
      </button>
    </div>

    <div v-if="questions.length === 0" class="text-center py-24 text-stone">
      <p class="text-lg mb-2">暂无题目</p>
      <p class="text-sm">点击右上角录入你的第一道错题</p>
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="q in filteredQuestions"
        :key="q.id"
        class="bg-pure-white border border-light-gray rounded-container p-6 transition-colors hover:bg-snow"
      >
        <div class="flex items-start justify-between gap-4">
          <div class="flex-1">
            <div class="flex items-center gap-3 mb-2">
              <span class="px-3 py-1 bg-light-gray text-near-black rounded-pill text-xs">
                {{ q.question_type }}
              </span>
              <span v-if="q.difficulty" class="text-xs text-stone">
                难度 {{ q.difficulty }}
              </span>
            </div>

            <!-- 图片预览 -->
            <div v-if="q.question_image_url" class="mb-3">
              <img :src="q.question_image_url" class="max-h-40 rounded-container border border-light-gray" />
            </div>

            <!-- PDF 标识 -->
            <div v-if="q.question_pdf_url" class="flex items-center gap-2 mb-3 text-near-black">
              <svg class="w-5 h-5 text-stone" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
              </svg>
              <a :href="q.question_pdf_url" target="_blank" class="text-sm underline">查看 PDF</a>
            </div>

            <p v-if="q.question_text" class="text-near-black text-base mb-3">{{ q.question_text }}</p>
            <div v-if="q.options" class="grid grid-cols-2 gap-2 mb-3">
              <div
                v-for="(val, key) in q.options"
                :key="key"
                class="text-sm text-stone"
              >
                {{ key }}. {{ val }}
              </div>
            </div>
            <p class="text-sm text-mid-gray">
              正确答案: {{ q.correct_answer }}
            </p>
          </div>
          <div class="flex items-center gap-2">
            <router-link
              :to="`/aptitude/questions/${q.id}/edit`"
              class="px-4 py-2 bg-light-gray text-near-black rounded-pill text-sm transition-colors hover:bg-border-light"
            >
              编辑
            </router-link>
            <button
              @click="deleteQuestion(q.id)"
              class="px-4 py-2 bg-pure-white border border-light-gray text-stone rounded-pill text-sm transition-colors hover:bg-snow"
            >
              删除
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import client from '../api/client'

const questions = ref<any[]>([])
const filterType = ref('')

const questionTypes = ['', '政治理论', '常识判断', '言语理解', '数量关系', '判断推理', '资料分析']

const filteredQuestions = computed(() => {
  if (!filterType.value) return questions.value
  return questions.value.filter(q => q.question_type === filterType.value)
})

const fetchQuestions = async () => {
  try {
    const res = await client.get('/aptitude/questions')
    questions.value = res.data.items
  } catch (err) {
    console.error('Failed to fetch questions', err)
  }
}

const deleteQuestion = async (id: string) => {
  if (!confirm('确定要删除这道题吗？')) return
  try {
    await client.delete(`/aptitude/questions/${id}`)
    questions.value = questions.value.filter(q => q.id !== id)
  } catch (err) {
    alert('删除失败')
  }
}

onMounted(fetchQuestions)
</script>
