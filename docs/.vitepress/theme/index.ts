import DefaultTheme from 'vitepress/theme';
import { useRouter } from 'vitepress'
import { watch, h, onMounted } from "vue"
import './style.css';
import './components/download.css'
import { enhanceAppWithTabs } from 'vitepress-plugin-tabs/client'
import giscus from './giscus.vue'
import notfound from './notfound.vue';
import DownloadLink from './components/DownloadLink.vue' // 路径根据你的结构调整
import downloadbtn from './downloadbtn.vue' // 路径根据你的结构调整
export default {
    ...DefaultTheme,
    Layout() {
        return h(DefaultTheme.Layout, null, {
            'not-found': () => h(notfound),
            // 'doc-after': () => h(giscus)
        })
    },
    enhanceApp({ app }) {
        enhanceAppWithTabs(app)
        app.component('DownloadLink', DownloadLink)
        app.component('downloadbtn', downloadbtn)
    },
    setup() {
        const handleRouteChange = () => {
            document.querySelectorAll('.downloadlink').forEach((e) => {
                e.target = '_blank'
                e.addEventListener('click', () => {
                    if (!e.href.includes('x64_win10')) return;
                    function checkIfMobile() {
                        const userAgent = navigator.userAgent || navigator.vendor || window.opera;
                        return /android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(userAgent);
                    }
                    if (checkIfMobile()) return;
                    //setTimeout(() => {
                    window.open(window.location.href, '_blank');
                    window.location.href = `/${window.localStorage.currentlang}/support.html`
                    //}, 50);
                });
            })
            if (!window.location.hostname.startsWith('docs')) return;
            ['', 'image.'].forEach(
                (pre) => {
                    let replacetarget = window.location.protocol + '//' + pre + window.location.hostname.substring(5);
                    let origin = 'https://' + pre + 'lunatranslator.org'
                    let srcs = document.querySelectorAll(pre ? "img" : 'a');
                    srcs.forEach(
                        (e) => {
                            let att = pre ? 'src' : 'href';
                            let tgt = e.getAttribute(att).replace(origin, replacetarget)
                            if (tgt != e.getAttribute(att)) {
                                e.setAttribute(att, tgt)
                            }
                        }
                    )
                }
            )
        }
        const supportlangs = ['zh', 'en', 'ja', 'vi', 'cht', 'ko', 'ru']
        onMounted(
            () => {
                let _ = window.location.pathname.split('/')[1]
                if (supportlangs.includes(_))
                    window.localStorage.currentlang = _
                handleRouteChange()
            }
        )
        const router = useRouter();
        watch(
            () => router.route.path,
            (path) => {
                let _ = path.split('/')[1]
                if (supportlangs.includes(_))
                    window.localStorage.currentlang = _
            }
        )
        router.onAfterRouteChange = () => {
            handleRouteChange()
        };
    }
}