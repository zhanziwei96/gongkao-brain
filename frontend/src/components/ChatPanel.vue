<template>
  <div class="fixed bottom-6 right-6 z-50">
    <!-- 聊天窗口 -->
    <div
      v-if="isOpen"
      class="w-96 h-[500px] bg-pure-white border border-light-gray rounded-container flex flex-col shadow-sm"
    >
      <div class="flex items-center justify-between px-4 py-3 border-b border-light-gray">
        <span class="font-medium text-near-black text-sm">AI 助手</span>
        <button @click="isOpen = false" class="text-stone hover:text-pure-black text-lg leading-none">&times;</button>
      </div>
      <div ref="messagesContainer" class="flex-1 overflow-y-auto px-4 py-4 space-y-4">
        <div
          v-for="(msg, i) in messages"
          :key="i"
          :class="msg.role === 'user' ? 'flex justify-end' : 'flex justify-start'"
        >
          <div
            :class="[
              'max-w-[80%] px-4 py-2 text-sm',
              msg.role === 'user'
                ? 'bg-pure-black text-pure-white rounded-container rounded-br-none'
                : 'bg-snow text-near-black border border-light-gray rounded-container rounded-bl-none'
            ]"
          >
            {{ msg.content }}
          </div>
        </div>
        <div v-if="isLoading" class="flex justify-start">
          <div class="bg-snow border border-light-gray rounded-container rounded-bl-none px-4 py-2 text-sm text-stone">
            思考中...
          </div>
        </div>
      </div>
      <div class="px-4 py-3 border-t border-light-gray">
        <form @submit.prevent="sendMessage" class="flex gap-2">
          <input
            v-model="input"
            type="text"
            placeholder="输入消息..."
            class="flex-1 px-4 py-2 bg-pure-white border border-light-gray rounded-pill text-sm text-near-black placeholder-silver focus:outline-none focus:ring-2 focus:ring-[#3b82f6] focus:ring-opacity-50"
          />
          <button
            type="submit"
            class="px-5 py-2 bg-pure-black text-pure-white rounded-pill text-sm font-medium transition-colors hover:bg-near-black disabled:opacity-50"
            :disabled="isLoading || !input.trim()"
          >
            发送
          </button>
        </form>
      </div>
    </div>

    <!-- 悬浮按钮 -->
    <button
      v-else
      @click="isOpen = true"
      class="w-12 h-12 bg-pure-black text-pure-white rounded-pill flex items-center justify-center shadow-sm hover:bg-near-black transition-colors"
    >
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
      </svg>
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue'

const isOpen = ref(false)
const input = ref('')
const isLoading = ref(false)
const messages = ref<{ role: string; content: string }[]>([
  { role: 'assistant', content: '你好！我是你的公考备考助手，随时为你解答行测和申论问题。' }
])
const messagesContainer = ref<HTMLDivElement>()

const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const sendMessage = async () => {
  const text = input.value.trim()
  if (!text || isLoading.value) return

  messages.value.push({ role: 'user', content: text })
  input.value = ''
  isLoading.value = true
  await scrollToBottom()

  try {
    const token = localStorage.getItem('token')
    const response = await fetch('/api/chat/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        messages: messages.value.map(m => ({ role: m.role, content: m.content })),
        context: { page: window.location.pathname }
      })
    })

    const reader = response.body?.getReader()
    const decoder = new TextDecoder()
    let assistantMsg = ''

    if (reader) {
      messages.value.push({ role: 'assistant', content: '' })
      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        const chunk = decoder.decode(value)
        const lines = chunk.split('\n')
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              if (data.delta) {
                assistantMsg += data.delta
                messages.value[messages.value.length - 1].content = assistantMsg
                await scrollToBottom()
              }
              if (data.done) break
            } catch (e) {
              // ignore parse errors
            }
          }
        }
      }
    }
  } catch (err) {
    messages.value.push({ role: 'assistant', content: '抱歉，连接出错，请稍后重试。' })
  } finally {
    isLoading.value = false
    await scrollToBottom()
  }
}
</script>
