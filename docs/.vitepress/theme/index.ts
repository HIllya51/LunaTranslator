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
                    setTimeout(() => {
                        window.location.href = `/${window.localStorage.currentlang}/support.html`;
                    }, 50);
                });
            })
            let timeout = 0;
            if (window.location.href.endsWith('support.html')) {
                if (window.localStorage.currentlang != 'zh') {
                    timeout = setTimeout(
                        () => {
                            window.location.href = 'https://www.patreon.com/hillya51'
                        }, 8000
                    )
                }
            }
            else {
                if (timeout) {
                    timeout = 0
                    clearTimeout(timeout)
                }
            }
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
        const supportlangs = ['zh', 'en', 'ja', 'vi']
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