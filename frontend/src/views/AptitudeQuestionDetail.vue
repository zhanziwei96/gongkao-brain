<template>
  <div class="max-w-5xl mx-auto px-6 py-12">
    <div v-if="loading" class="text-center py-24 text-stone">
      <p>加载中...</p>
    </div>

    <div v-else-if="!question" class="text-center py-24 text-stone">
      <p class="text-lg mb-2">题目不存在</p>
      <router-link to="/aptitude/questions" class="text-near-black underline">返回列表</router-link>
    </div>

    <div v-else>
      <!-- 顶部 -->
      <div class="flex items-center justify-between mb-8">
        <div class="flex items-center gap-3">
          <h1 class="font-display text-4xl font-medium text-pure-black" style="line-height: 1.0">
            题目详情
          </h1>
          <span class="px-3 py-1 bg-light-gray text-near-black rounded-pill text-xs">
            {{ question.question_type }}
          </span>
          <span v-if="question.difficulty" class="text-xs text-stone">
            难度 {{ question.difficulty }}
          </span>
        </div>
        <router-link
          to="/aptitude/questions"
          class="px-4 py-2 bg-light-gray text-near-black rounded-pill text-sm transition-colors hover:bg-border-light"
        >
          返回列表
        </router-link>
      </div>

      <!-- 题目内容 -->
      <div class="bg-pure-white border border-light-gray rounded-container p-8 mb-8">
        <div v-if="question.question_image_url" class="mb-6">
          <img :src="question.question_image_url" class="max-h-64 rounded-container border border-light-gray" />
        </div>

        <div v-if="question.question_pdf_url" class="flex items-center gap-2 mb-6 text-near-black">
          <svg class="w-5 h-5 text-stone" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
          </svg>
          <a :href="question.question_pdf_url" target="_blank" class="text-sm underline">查看 PDF</a>
        </div>

        <p v-if="question.question_text" class="text-near-black text-lg mb-6">
          {{ question.question_text }}
        </p>

        <div v-if="question.options" class="grid grid-cols-1 md:grid-cols-2 gap-3 mb-6">
          <div
            v-for="(val, key) in question.options"
            :key="key"
            class="px-5 py-3 rounded-container border border-light-gray text-base"
            :class="key === question.correct_answer ? 'bg-pure-black text-pure-white border-pure-black' : 'text-stone'"
          >
            <span class="font-medium">{{ key }}.</span> {{ val }}
          </div>
        </div>

        <p class="text-sm text-mid-gray">
          正确答案：<strong class="text-near-black">{{ question.correct_answer }}</strong>
        </p>
      </div>

      <!-- 历史答题记录 -->
      <div class="bg-pure-white border border-light-gray rounded-container p-8">
        <div class="flex items-center justify-between mb-6">
          <h2 class="font-display text-2xl font-medium text-pure-black">答题记录</h2>
          <button
            @click="openAnswerDialog"
            class="px-5 py-2 bg-pure-black text-pure-white rounded-pill text-sm transition-colors hover:bg-near-black"
          >
            重新作答
          </button>
        </div>

        <div v-if="attempts.length === 0" class="text-center py-12 text-stone">
          <p>还没有答题记录</p>
        </div>

        <div v-else class="space-y-3">
          <div
            v-for="attempt in attempts"
            :key="attempt.id"
            class="flex items-center justify-between px-5 py-4 rounded-container border transition-colors"
            :class="attempt.is_correct ? 'border-pure-black bg-snow' : 'border-light-gray bg-pure-white'"
          >
            <div class="flex items-center gap-4">
              <span
                class="w-8 h-8 flex items-center justify-center rounded-full text-sm font-medium"
                :class="attempt.is_correct ? 'bg-pure-black text-pure-white' : 'bg-near-black text-pure-white'"
              >
                {{ attempt.user_answer }}
              </span>
              <div>
                <p class="text-sm text-near-black">
                  {{ attempt.is_correct ? '回答正确' : '回答错误' }}
                </p>
                <p class="text-xs text-stone">
                  {{ formatDate(attempt.attempt_date) }}
                </p>
              </div>
            </div>
            <span
              v-if="attempt.is_mistake"
              class="px-3 py-1 rounded-pill text-xs bg-near-black text-pure-white"
            >
              错题
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 作答弹窗 -->
    <div
      v-if="answerDialog.open"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      @click.self="closeAnswerDialog"
    >
      <div class="bg-pure-white rounded-container max-w-lg w-full mx-4 p-8 shadow-lg">
        <div class="flex items-center justify-between mb-6">
          <h2 class="font-display text-2xl font-medium text-pure-black">作答</h2>
          <button
            @click="closeAnswerDialog"
            class="w-8 h-8 flex items-center justify-center text-stone hover:text-near-black transition-colors"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div v-if="question" class="space-y-6">
          <div>
            <p v-if="question.question_text" class="text-near-black text-base">
              {{ question.question_text }}
            </p>
          </div>

          <div v-if="question.options" class="space-y-2">
            <button
              v-for="(val, key) in question.options"
              :key="key"
              @click="selectOption(key)"
              :disabled="answerDialog.submitted"
              :class="[
                'w-full text-left px-5 py-3 rounded-container border text-base transition-colors',
                getOptionClass(key)
              ]"
            >
              <span class="font-medium">{{ key }}.</span> {{ val }}
            </button>
          </div>

          <div
            v-if="answerDialog.submitted"
            class="rounded-container p-4 text-center"
            :class="answerDialog.isCorrect ? 'bg-pure-black text-pure-white' : 'bg-near-black text-pure-white'"
          >
            <p class="text-lg font-medium mb-2">{{ answerDialog.resultText }}</p>
            <p v-if="!answerDialog.isCorrect" class="text-sm text-silver">
              正确答案：<strong class="text-pure-white">{{ question.correct_answer }}</strong>
            </p>
          </div>

          <div class="flex gap-3">
            <button
              v-if="!answerDialog.submitted"
              @click="submitAnswer"
              :disabled="!answerDialog.selected"
              class="flex-1 px-6 py-3 bg-pure-black text-pure-white rounded-pill text-base font-medium transition-colors hover:bg-near-black disabled:opacity-40 disabled:cursor-not-allowed"
            >
              提交答案
            </button>
            <button
              v-else
              @click="closeAnswerDialog"
              class="flex-1 px-6 py-3 bg-light-gray text-near-black rounded-pill text-base font-medium transition-colors hover:bg-border-light"
            >
              关闭
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import client from '../api/client'

const route = useRoute()
const router = useRouter()
const loading = ref(true)
const question = ref<any>(null)
const attempts = ref<any[]>([])

const answerDialog = ref({
  open: false,
  selected: '' as string,
  submitted: false,
  isCorrect: false,
  resultText: '',
})

const fetchQuestion = async () => {
  try {
    const res = await client.get(`/aptitude/questions/${route.params.id}`)
    question.value = res.data
  } catch (err) {
    console.error('获取题目失败', err)
    question.value = null
  }
}

const fetchAttempts = async () => {
  try {
    const res = await client.get('/aptitude/attempts', {
      params: { question_id: route.params.id }
    })
    attempts.value = res.data
  } catch (err) {
    console.error('获取答题记录失败', err)
  }
}

const openAnswerDialog = () => {
  answerDialog.value = {
    open: true,
    selected: '',
    submitted: false,
    isCorrect: false,
    resultText: '',
  }
}

const closeAnswerDialog = () => {
  answerDialog.value.open = false
  if (answerDialog.value.submitted) {
    fetchAttempts()
    window.dispatchEvent(new CustomEvent('aptitude-stats-updated'))
  }
}

const selectOption = (key: string) => {
  if (answerDialog.value.submitted) return
  answerDialog.value.selected = key
}

const getOptionClass = (key: string) => {
  const d = answerDialog.value
  if (!d.submitted) {
    return d.selected === key
      ? 'border-pure-black bg-snow'
      : 'border-light-gray hover:border-mid-gray'
  }
  const correct = question.value?.correct_answer
  if (key === correct) {
    return 'border-pure-black bg-pure-black text-pure-white'
  }
  if (d.selected === key && key !== correct) {
    return 'border-near-black bg-near-black text-pure-white'
  }
  return 'border-light-gray opacity-50'
}

const submitAnswer = async () => {
  const d = answerDialog.value
  if (!d.selected || !question.value) return

  try {
    const res = await client.post('/aptitude/attempts', {
      question_id: question.value.id,
      user_answer: d.selected,
    })
    d.isCorrect = res.data.is_correct
    d.submitted = true
    d.resultText = d.isCorrect ? '回答正确！' : '回答错误'
    window.dispatchEvent(new CustomEvent('aptitude-stats-updated'))
  } catch (err) {
    console.error('提交失败', err)
    alert('提交失败')
  }
}

const formatDate = (dateStr: string) => {
  const d = new Date(dateStr)
  return d.toLocaleString('zh-CN', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

onMounted(async () => {
  await fetchQuestion()
  await fetchAttempts()
  loading.value = false
})
</script>
