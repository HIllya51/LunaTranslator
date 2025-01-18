<script setup lang="ts">
import Giscus from '@giscus/vue';
import { useData } from 'vitepress';
const { frontmatter, title, isDark } = useData()
</script>

<style>
.giscus_wrapper {
    margin-top: 2rem;
    padding-top: 2rem;
    border-width: 1px 0 0 0;
    border-style: solid;
    border-color: gainsboro;
}
</style>

<template #doc-after>
    <div v-if="frontmatter.__giscus__ !== false" :key="title" class="giscus_wrapper">
        <Giscus id="__giscus__" repo="HIllya51/LunaTranslator" repo-id="R_kgDOIFQnug" category="document_giscus"
            category-id="DIC_kwDOIFQnus4CmETc" mapping="title" strict="0" reactions-enabled="1" emit-metadata="0"
            input-position="top" :theme="isDark ? 'transparent_dark' : 'light'" />
    </div>
</template>

<style scoped></style>