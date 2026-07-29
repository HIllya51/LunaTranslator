
<template>
  <div v-if="loading" class="loading">加载中...</div>
  <div v-else-if="error" class="error">{{ error }}</div>
  <div v-else class="remote-content">
    <div v-html="renderedMarkdown"></div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import MarkdownIt from 'markdown-it'

const props = defineProps()

const loading = ref(true)
const error = ref(null)
const renderedMarkdown = ref('')

const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true
})

onMounted(async () => {
  try {
    const response = await fetch('https://lunatranslator.org/posts_api?postid=1820086668481265664&p=0')
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`)
    
    const data = await response.json()
    const markdownContent = data[0].content
    
    renderedMarkdown.value = md.render(markdownContent)
  } catch (err) {
    error.value = `加载失败: ${err.message}`
  } finally {
    loading.value = false
  }
})
</script>
