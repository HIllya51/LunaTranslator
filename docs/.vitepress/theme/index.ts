import DefaultTheme from 'vitepress/theme';
import { useRouter } from 'vitepress'
import { watch, h, onMounted } from "vue"
import './style.css';
import { enhanceAppWithTabs } from 'vitepress-plugin-tabs/client'
import giscus from './giscus.vue'
import notfound from './notfound.vue';
export default {
    ...DefaultTheme,
    Layout() {
        return h(DefaultTheme.Layout, null, {
            'not-found': () => h(notfound),
            'doc-after': () => h(giscus)
        })
    },
    enhanceApp({ app }) {
        enhanceAppWithTabs(app)
    },
    setup() {
        const handleRouteChange = () => {
            document.querySelectorAll('.downloadlink').forEach((e) => {
                e.target = '_blank'
                e.addEventListener('click', function (e) {
                    window.location.href = `/${window.localStorage.currentlang}/support.html`
                });
            })
            let timeout = 0;
            if (window.location.href.endsWith('support.html')) {
                if (window.localStorage.currentlang != 'zh') {
                    timeout = setTimeout(
                        () => {
                            window.location.href = 'https://www.patreon.com/hillya51'
                        }, 5000
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