<template>
  <span>
    <a href="#" class="downloadlink" @click.prevent="startDownload"></a>

    <div v-if="showModal" class="download-overlay" @click="closeModal"></div>
    <div v-if="showModal" class="download-modal">
      <div v-if="!error && !loading" class="progress-bar-container">
        <div class="progress-bar" :style="{ width: progress.toFixed(0) + '%' }"></div>
      </div>
      <div v-if="loading && !error">
        <svg width="100%" height="2em" viewBox="0 0 30 10">
          <circle cx="5" cy="5" r="3" fill="#000">
            <animate attributeName="opacity" values="0;1;0" dur="1s" repeatCount="indefinite" begin="0.1" />
          </circle>
          <circle cx="15" cy="5" r="3" fill="#000">
            <animate attributeName="opacity" values="0;1;0" dur="1s" repeatCount="indefinite" begin="0.2" />
          </circle>
          <circle cx="25" cy="5" r="3" fill="#000">
            <animate attributeName="opacity" values="0;1;0" dur="1s" repeatCount="indefinite" begin="0.3" />
          </circle>
        </svg>
      </div>
      <p v-if="!loading && !error" style="display: flex; justify-content: space-between;"><span>{{ getprogresstext1()
          }}</span> <span>{{ getprogresstext2() }}</span></p>
      <p v-if="error" class="error-message">{{ error }}</p>
      <h3 v-if="error"><a :href=href>{{ getFilename() }}</a></h3>
    </div>
  </span>
</template>

<script setup>
import { ref } from 'vue';

const props = defineProps({
  href: { // 文件的实际URL
    type: String,
    required: true,
  },
});
const loading = ref(false)
const showModal = ref(false);
const progress = ref(0);
const error = ref(null);
const downloading = ref(false);
const contentLength = ref(0);
const receivedLength = ref(0);
let objectUrl = null; // Store object URL to revoke later

const getprogresstext1 = () => {
  return progress.value.toFixed(0) + '%'
}

const getprogresstext2 = () => {
  return (receivedLength.value / 1024 / 1024).toFixed(1) + ' MB / ' + (contentLength.value / 1024 / 1024).toFixed(1) + ' MB'
}

const getFilename = () => {
  let spls = props.href.split('/')
  return 'LunaTranslator_' + spls[spls.length - 1].split('?')[0] + '.zip'
};


let lasttime = 0
function _redirect() {
  let curlink = window.location.href
  if (lasttime) clearTimeout(lasttime)
  lasttime = setTimeout(() => {
    if (window.__ishowing) return;
    if (curlink == window.location.href) {
      window.location.href = `/${window.localStorage.currentlang}/support.html`
    }
  }, 1000)
}
const startDownload = async () => {
  window.__ishowing = true
  if (downloading.value) return; // 防止重复点击 
  showModal.value = true;
  progress.value = 0;
  error.value = null;
  downloading.value = true;
  contentLength.value = 0;
  receivedLength.value = 0;

  loading.value = true;
  //document.getElementById('downloadoriginlink').href=props.href
  try {
    const response = await fetch(props.href);

    if (!response.ok) {
      throw new Error(`${response.status} ${response.statusText} ${await response.text()}`);
    }

    loading.value = false;
    const _contentLength = +response.headers.get('Content-Length');
    const reader = response.body.getReader();

    const chunks = [];

    // eslint-disable-next-line no-constant-condition
    while (downloading.value) {
      const { done, value } = await reader.read();
      if (done) {
        break;
      }
      chunks.push(value);
      receivedLength.value += value.length;
      contentLength.value = _contentLength
      if (_contentLength) {
        progress.value = (receivedLength.value / _contentLength) * 100;
      } else {
        // 如果没有 Content-Length，我们不能精确计算进度
        // 可以显示一个不确定的进度条或只是"下载中..."
        // 这里简单处理，进度条不会动，直到完成
        progress.value = 50; // Or some visual cue
      }
    }
    if (!downloading.value) return
    const blob = new Blob(chunks);
    objectUrl = URL.createObjectURL(blob);

    const link = document.createElement('a');
    link.href = objectUrl;
    link.download = getFilename();
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    progress.value = 100; // 标记完成
    window.__ishowing = false
    _redirect()
  } catch (err) {
    console.error(err);
    error.value = err.message;
    progress.value = 0; // 重置进度
  } finally {
    downloading.value = false;
    // objectUrl 将在 closeModal 时或下次下载前被 revoke
  }
};
const closeModal = () => {
  window.__ishowing = false
  showModal.value = false;
  if (objectUrl) {
    URL.revokeObjectURL(objectUrl); // 释放内存
    objectUrl = null;
    _redirect()
  }
  // 如果下载未完成或出错，重置状态
  if (progress.value < 100 || error.value) {
    progress.value = 0;
    error.value = null;
  }
  downloading.value = false;
};
</script>

<style scoped>
/* 确保组件的<a>标签样式与普通链接一致或自定义 */
a {
  cursor: pointer;
  /* color: var(--vp-c-brand-1); */
  /* 使用VitePress品牌色 */
  /* text-decoration: underline; */
}

.download-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.6);
  z-index: 999;
  display: flex;
  align-items: center;
  justify-content: center;
}

.download-modal {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background-color: white;
  padding: 25px 30px;
  border-radius: 8px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
  z-index: 1000;
  width: 80%;
  max-width: 400px;
  text-align: center;
  color: #333;
  /* 确保文本颜色在浅色背景上可见 */
}

.download-modal h3 {
  margin-top: 0;
  font-size: 1.2em;
  color: #333;
}

.progress-bar-container {
  width: 100%;
  background-color: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 10px;
}

.progress-bar {
  height: 20px;
  background-color: #4CAF50;
  /* 绿色进度条 */
  width: 0%;
  transition: width 0.1s ease-in-out;
  border-radius: 4px;
}

.download-modal p {
  margin-bottom: 0px;
  font-size: 0.9em;
  color: #555;
}

.error-message {
  margin-top: 0px;
  color: red;
  font-weight: bold;
}

.close-button {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 0.9em;
  margin-top: 10px;
}

.close-button:hover {
  background-color: #0056b3;
}
</style>