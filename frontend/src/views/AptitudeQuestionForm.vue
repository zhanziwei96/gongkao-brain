<template>
  <div class="max-w-2xl mx-auto px-6 py-12">
    <h1 class="font-display text-4xl font-medium text-pure-black mb-8" style="line-height: 1.0">
      {{ isEdit ? '编辑题目' : '录入新题' }}
    </h1>

    <form @submit.prevent="handleSubmit" class="space-y-6">
      <!-- 文件上传 -->
      <div>
        <label class="block text-sm text-near-black mb-2">题目文件（图片或 PDF）</label>
        <div
          @click="triggerFileInput"
          @drop.prevent="handleDrop"
          @dragover.prevent="dragOver = true"
          @dragleave.prevent="dragOver = false"
          :class="[
            'w-full border-2 border-dashed rounded-container p-8 text-center cursor-pointer transition-colors',
            dragOver ? 'border-pure-black bg-snow' : 'border-light-gray bg-pure-white'
          ]"
        >
          <input
            ref="fileInput"
            type="file"
            accept="image/*,.pdf"
            class="hidden"
            @change="handleFileSelect"
          />
          <div v-if="!previewUrl && !pdfName">
            <svg class="w-8 h-8 mx-auto mb-3 text-stone" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
            <p class="text-stone text-sm">点击或拖拽上传图片 / PDF</p>
          </div>
          <div v-else-if="previewUrl" class="relative">
            <img :src="previewUrl" class="max-h-48 mx-auto rounded-container" />
            <button
              type="button"
              @click.stop="clearFile"
              class="absolute top-2 right-2 w-6 h-6 bg-pure-black text-pure-white rounded-full text-xs flex items-center justify-center"
            >
              &times;
            </button>
          </div>
          <div v-else-if="pdfName" class="flex items-center justify-center gap-2 text-near-black">
            <svg class="w-6 h-6 text-stone" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
            </svg>
            <span class="text-sm">{{ pdfName }}</span>
            <button
              type="button"
              @click.stop="clearFile"
              class="ml-2 w-5 h-5 bg-pure-black text-pure-white rounded-full text-xs flex items-center justify-center"
            >
              &times;
            </button>
          </div>
        </div>
      </div>

      <div>
        <label class="block text-sm text-near-black mb-2">题型 <span class="text-stone">*</span></label>
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
          placeholder="可手动输入或补充题目文字内容..."
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
  question_image_url: string
  question_pdf_url: string
}>({
  question_type: '',
  question_text: '',
  options: { A: '', B: '', C: '', D: '' },
  correct_answer: '',
  difficulty: 3,
  question_image_url: '',
  question_pdf_url: '',
})

const fileInput = ref<HTMLInputElement>()
const dragOver = ref(false)
const previewUrl = ref('')
const pdfName = ref('')
const uploadedFileUrl = ref('')

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileSelect = async (e: Event) => {
  const target = e.target as HTMLInputElement
  if (target.files && target.files[0]) {
    await processFile(target.files[0])
  }
}

const handleDrop = async (e: DragEvent) => {
  dragOver.value = false
  if (e.dataTransfer?.files && e.dataTransfer.files[0]) {
    await processFile(e.dataTransfer.files[0])
  }
}

const processFile = async (file: File) => {
  if (!file.type.startsWith('image/') && file.type !== 'application/pdf') {
    alert('仅支持图片或 PDF 格式')
    return
  }

  const formData = new FormData()
  formData.append('file', file)

  try {
    const res = await client.post('/aptitude/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    uploadedFileUrl.value = res.data.url

    if (file.type.startsWith('image/')) {
      previewUrl.value = URL.createObjectURL(file)
      form.question_image_url = res.data.url
      form.question_pdf_url = ''
      pdfName.value = ''
    } else {
      pdfName.value = file.name
      form.question_pdf_url = res.data.url
      form.question_image_url = ''
      previewUrl.value = ''
    }
  } catch (err: any) {
    alert(err.response?.data?.detail || '上传失败')
  }
}

const clearFile = () => {
  previewUrl.value = ''
  pdfName.value = ''
  uploadedFileUrl.value = ''
  form.question_image_url = ''
  form.question_pdf_url = ''
  if (fileInput.value) fileInput.value.value = ''
}

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
      form.question_image_url = q.question_image_url || ''
      form.question_pdf_url = q.question_pdf_url || ''
      if (q.question_image_url) {
        previewUrl.value = q.question_image_url
      }
      if (q.question_pdf_url) {
        pdfName.value = '已上传的 PDF'
      }
    } catch (err) {
      alert('加载题目失败')
      router.push('/aptitude/questions')
    }
  }
})

const handleSubmit = async () => {
  try {
    const payload = {
      question_type: form.question_type,
      question_text: form.question_text,
      options: Object.fromEntries(Object.entries(form.options).filter(([, v]) => v)),
      correct_answer: form.correct_answer,
      difficulty: form.difficulty,
      question_image_url: form.question_image_url,
      question_pdf_url: form.question_pdf_url,
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
