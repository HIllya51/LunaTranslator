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
    }
}