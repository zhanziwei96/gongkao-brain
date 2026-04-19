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

    <!-- 筛选栏 -->
    <div class="flex flex-wrap items-center gap-3 mb-6">
      <button
        v-for="type in questionTypes"
        :key="type.value"
        @click="filterType = type.value"
        :class="[
          'px-5 py-2 rounded-pill text-sm transition-colors',
          filterType === type.value
            ? 'bg-light-gray text-near-black'
            : 'bg-pure-white text-stone border border-light-gray hover:bg-snow'
        ]"
      >
        {{ type.label }}
      </button>
      <div class="flex-1"></div>
      <button
        @click="showMistakesOnly = !showMistakesOnly"
        :class="[
          'px-5 py-2 rounded-pill text-sm transition-colors border',
          showMistakesOnly
            ? 'bg-pure-black text-pure-white border-pure-black'
            : 'bg-pure-white text-stone border-light-gray hover:bg-snow'
        ]"
      >
        {{ showMistakesOnly ? '只看错题' : '全部题目' }}
      </button>
    </div>

    <div v-if="questions.length === 0" class="text-center py-24 text-stone">
      <p class="text-lg mb-2">暂无题目</p>
      <p class="text-sm">点击右上角录入你的第一道错题</p>
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="q in questions"
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

            <router-link
              :to="`/aptitude/questions/${q.id}`"
              class="block text-near-black text-base mb-3 hover:underline"
            >
              {{ q.question_text || '（图片/PDF 题目）' }}
            </router-link>
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
            <button
              @click="openAnswerDialog(q)"
              class="px-4 py-2 bg-pure-black text-pure-white rounded-pill text-sm transition-colors hover:bg-near-black"
            >
              开始作答
            </button>
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

        <div v-if="answerDialog.question" class="space-y-6">
          <!-- 题目内容 -->
          <div>
            <div class="flex items-center gap-2 mb-3">
              <span class="px-3 py-1 bg-light-gray text-near-black rounded-pill text-xs">
                {{ answerDialog.question.question_type }}
              </span>
            </div>
            <div v-if="answerDialog.question.question_image_url" class="mb-3">
              <img :src="answerDialog.question.question_image_url" class="max-h-48 rounded-container border border-light-gray" />
            </div>
            <p v-if="answerDialog.question.question_text" class="text-near-black text-base">
              {{ answerDialog.question.question_text }}
            </p>
          </div>

          <!-- 选项 -->
          <div v-if="answerDialog.question.options" class="space-y-2">
            <button
              v-for="(val, key) in answerDialog.question.options"
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

          <!-- 结果 -->
          <div
            v-if="answerDialog.submitted"
            class="rounded-container p-4 text-center"
            :class="answerDialog.isCorrect ? 'bg-pure-black text-pure-white' : 'bg-near-black text-pure-white'"
          >
            <p class="text-lg font-medium mb-2">{{ answerDialog.resultText }}</p>
            <p v-if="!answerDialog.isCorrect" class="text-sm text-silver">
              正确答案：<strong class="text-pure-white">{{ answerDialog.question.correct_answer }}</strong>
            </p>
          </div>

          <!-- 操作按钮 -->
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
import { ref, watch, onMounted } from 'vue'
import client from '../api/client'

const questions = ref<any[]>([])
const filterType = ref('')
const showMistakesOnly = ref(false)

const questionTypes = [
  { value: '', label: '全部' },
  { value: '政治理论', label: '政治理论' },
  { value: '常识判断', label: '常识判断' },
  { value: '言语理解', label: '言语理解' },
  { value: '数量关系', label: '数量关系' },
  { value: '判断推理', label: '判断推理' },
  { value: '资料分析', label: '资料分析' },
]

const answerDialog = ref({
  open: false,
  question: null as any,
  selected: '' as string,
  submitted: false,
  isCorrect: false,
  resultText: '',
  resultClass: '',
})

const fetchQuestions = async () => {
  try {
    const params: any = {}
    if (filterType.value) params.question_type = filterType.value
    if (showMistakesOnly.value) params.is_mistake = true
    const res = await client.get('/aptitude/questions', { params })
    questions.value = res.data.items
  } catch (err) {
    console.error('Failed to fetch questions', err)
  }
}

watch([filterType, showMistakesOnly], fetchQuestions, { immediate: false })

const openAnswerDialog = (question: any) => {
  answerDialog.value = {
    open: true,
    question,
    selected: '',
    submitted: false,
    isCorrect: false,
    resultText: '',
    resultClass: '',
  }
}

const closeAnswerDialog = () => {
  answerDialog.value.open = false
  // 如果已经提交过，刷新列表
  if (answerDialog.value.submitted) {
    fetchQuestions()
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
  // 已提交
  const correct = d.question.correct_answer
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
  if (!d.selected || !d.question) return

  try {
    const res = await client.post('/aptitude/attempts', {
      question_id: d.question.id,
      user_answer: d.selected,
    })
    d.isCorrect = res.data.is_correct
    d.submitted = true
    if (d.isCorrect) {
      d.resultText = '回答正确！'
      d.resultClass = 'bg-green-50 text-green-800'
    } else {
      d.resultText = '回答错误'
      d.resultClass = 'bg-red-50 text-red-800'
    }
    // 通知仪表盘和其他页面刷新统计数据
    window.dispatchEvent(new CustomEvent('aptitude-stats-updated'))
  } catch (err) {
    console.error('Submit failed', err)
    alert('提交失败')
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
