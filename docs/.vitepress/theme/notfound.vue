<script setup>

const supportlangs = ['zh', 'en', 'ja', 'vi', 'cht', 'ko']

function browserlang() {
    let l = navigator.language
    let ls = l.split('-')
    if (ls.length) l = ls[0]
    if (l == 'zh' && ls.length == 2 && (ls[1] == 'HK' || ls[1] == 'TW')) return 'cht'
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