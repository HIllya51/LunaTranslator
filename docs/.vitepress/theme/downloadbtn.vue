<script setup>
import { useData } from 'vitepress'

const { isDark } = useData()

</script>
<style>
.downloadlink-1 {
    background-image: url("/download.svg");
}

.downloadlink-2 {
    background-image: url("/download-2.svg");
}

.downloadlink {
    background-repeat: no-repeat;
    background-size: contain;
    width: 48px;
    height: 48px;
}
</style>

<template>
    <a v-if="isDark" target="_blank" class="downloadlink downloadlink-2"></a>
    <a v-else target="_blank" class="downloadlink downloadlink-1"></a>
</template>
