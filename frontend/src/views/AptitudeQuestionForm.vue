<template>
  <div class="max-w-2xl mx-auto px-6 py-12">
    <h1 class="font-display text-4xl font-medium text-pure-black mb-8" style="line-height: 1.0">
      {{ isEdit ? '编辑题目' : '录入新题' }}
    </h1>

    <form @submit.prevent="handleSubmit" class="space-y-6">
      <div>
        <label class="block text-sm text-near-black mb-2">题型</label>
        <select
          v-model="form.question_type"
          required
          class="w-full px-5 py-3 bg-pure-white border border-light-gray rounded-pill text-near-black text-base focus:outline-none focus:ring-2 focus:ring-[#3b82f6] focus:ring-opacity-50 appearance-none"
        >
          <option value="">请选择</option>
          <option v-for="t in questionTypes" :key="t" :value="t">{{ t }}</option>
        </select>
      </div>

      <div>
        <label class="block text-sm text-near-black mb-2">题目内容</label>
        <textarea
          v-model="form.question_text"
          rows="4"
          placeholder="输入题目内容..."
          class="w-full px-5 py-3 bg-pure-white border border-light-gray rounded-container text-near-black text-base placeholder-silver focus:outline-none focus:ring-2 focus:ring-[#3b82f6] focus:ring-opacity-50 resize-none"
        />
      </div>

      <div>
        <label class="block text-sm text-near-black mb-2">选项</label>
        <div class="space-y-3">
          <div v-for="key in optionKeys" :key="key" class="flex gap-3">
            <span class="w-8 h-10 flex items-center justify-center text-sm text-stone">{{ key }}</span>
            <input
              v-model="form.options[key]"
              type="text"
              :placeholder="`选项 ${key}`"
              class="flex-1 px-5 py-2 bg-pure-white border border-light-gray rounded-pill text-near-black text-base placeholder-silver focus:outline-none focus:ring-2 focus:ring-[#3b82f6] focus:ring-opacity-50"
            />
          </div>
        </div>
      </div>

      <div>
        <label class="block text-sm text-near-black mb-2">正确答案</label>
        <input
          v-model="form.correct_answer"
          type="text"
          placeholder="如：A"
          class="w-full px-5 py-3 bg-pure-white border border-light-gray rounded-pill text-near-black text-base placeholder-silver focus:outline-none focus:ring-2 focus:ring-[#3b82f6] focus:ring-opacity-50"
        />
      </div>

      <div>
        <label class="block text-sm text-near-black mb-2">难度 (1-5)</label>
        <input
          v-model.number="form.difficulty"
          type="number"
          min="1"
          max="5"
          class="w-full px-5 py-3 bg-pure-white border border-light-gray rounded-pill text-near-black text-base focus:outline-none focus:ring-2 focus:ring-[#3b82f6] focus:ring-opacity-50"
        />
      </div>

      <div class="flex gap-4 pt-4">
        <button
          type="submit"
          class="px-6 py-3 bg-pure-black text-pure-white rounded-pill text-base font-medium transition-colors hover:bg-near-black"
        >
          {{ isEdit ? '保存修改' : '提交录入' }}
        </button>
        <router-link
          to="/aptitude/questions"
          class="px-6 py-3 bg-light-gray text-near-black rounded-pill text-base font-medium transition-colors hover:bg-border-light"
        >
          取消
        </router-link>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import client from '../api/client'

const route = useRoute()
const router = useRouter()
const isEdit = ref(false)
const questionId = ref('')

const questionTypes = ['政治理论', '常识判断', '言语理解', '数量关系', '判断推理', '资料分析']
const optionKeys = ['A', 'B', 'C', 'D']

const form = reactive<{
  question_type: string
  question_text: string
  options: Record<string, string>
  correct_answer: string
  difficulty: number
}>({
  question_type: '',
  question_text: '',
  options: { A: '', B: '', C: '', D: '' },
  correct_answer: '',
  difficulty: 3,
})

onMounted(async () => {
  if (route.params.id) {
    isEdit.value = true
    questionId.value = route.params.id as string
    try {
      const res = await client.get(`/aptitude/questions/${questionId.value}`)
      const q = res.data
      form.question_type = q.question_type
      form.question_text = q.question_text || ''
      form.options = q.options || { A: '', B: '', C: '', D: '' }
      form.correct_answer = q.correct_answer || ''
      form.difficulty = q.difficulty || 3
    } catch (err) {
      alert('加载题目失败')
      router.push('/aptitude/questions')
    }
  }
})

const handleSubmit = async () => {
  try {
    const payload = {
      ...form,
      options: Object.fromEntries(Object.entries(form.options).filter(([, v]) => v))
    }
    if (isEdit.value) {
      await client.put(`/aptitude/questions/${questionId.value}`, payload)
    } else {
      await client.post('/aptitude/questions', payload)
    }
    router.push('/aptitude/questions')
  } catch (err: any) {
    alert(err.response?.data?.detail || '保存失败')
  }
}
</script>
