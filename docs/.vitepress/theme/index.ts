import DefaultTheme from 'vitepress/theme';
import { useRouter } from 'vitepress'
import { watch, h, onMounted } from "vue"
import './style.css';
import './components/download.css'
import { enhanceAppWithTabs } from 'vitepress-plugin-tabs/client'
import giscus from './giscus.vue'
import notfound from './notfound.vue';
import DownloadLink from './components/DownloadLink.vue' // 路径根据你的结构调整
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
    },
    setup() {
        const handleRouteChange = () => {
            document.querySelectorAll('.downloadlink').forEach((e) => {
                e.target = '_blank'
                e.addEventListener('click', async function (_) {
                    const response = await fetch(e.href);
                    if (!response.ok) {
                        return
                    }
                    window.open(`/${window.localStorage.currentlang}/support.html`, '_blank')
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
        onMounted(
            () => {
                window.localStorage.currentlang = window.location.pathname.split('/')[1]
                handleRouteChange()
            }
        )
        const router = useRouter();
        watch(
            () => router.route.path,
            (path) => {
                window.localStorage.currentlang = path.split('/')[1]
            }
        )
        router.onAfterRouteChange = () => {
            handleRouteChange()
        };
    }
}