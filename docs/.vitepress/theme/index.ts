import DefaultTheme from 'vitepress/theme';
import { useRouter } from 'vitepress'
import { watch } from "vue"
import './style.css';
import { enhanceAppWithTabs } from 'vitepress-plugin-tabs/client'

export default {
    ...DefaultTheme,
    enhanceApp({ app }) {
        enhanceAppWithTabs(app)
    },
    setup() {
        const router = useRouter();
        watch(
            () => router.route.path,
            (path) => {
                window.localStorage.currentlang = path.split('/')[1]
            }
        )
        router.onAfterRouteChanged = () => {
            if (!window.location.hostname.startsWith('docs')) return
            let replacetarget = window.location.protocol + '//image.' + window.location.hostname.substring(5);
            var images = document.getElementsByTagName('img');

            for (var i = 0; i < images.length; i++) {

                images[i].src = images[i].src.replace('https://image.lunatranslator.org', replacetarget)
            }
        };
    }
}