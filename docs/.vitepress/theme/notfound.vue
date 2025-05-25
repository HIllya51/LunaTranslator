<script setup>

const supportlangs = ['zh', 'en', 'ja', 'vi']
function browserlang() {
    let l = navigator.language
    if (l.includes('-')) l = l.split('-')[0]
    if (supportlangs.includes(l)) return l
    return 'en'
}
function cachedlang() {
    return window.localStorage.currentlang ? window.localStorage.currentlang : browserlang()
}
function urlcheck() {
    let url = window.location.pathname;
    console.log(url)
    let sps = url.split('/')
    console.log(sps)
    if (sps.length >= 2) {
        if (!supportlangs.includes(sps[1])) {
            window.location.pathname = `/${cachedlang()}/` + sps.slice(1).join('/')
        }
        else {
            window.location.pathname = `/${sps[1]}/`
        }
    }
    else {
        window.location.pathname = `/${cachedlang()}/`
    }
}
urlcheck()
</script>

<template #not-found>
</template>