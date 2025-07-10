import { defineConfig } from 'vitepress'
import { en } from './en'
import { zh, zhSearch } from './zh'
import { ja, jaSearch } from './ja'
import { vi, viSearch } from './vi'
import { cht, chtSearch } from './cht'
import { ko, koSearch } from './ko'
import { tabsMarkdownPlugin } from 'vitepress-plugin-tabs'

// https://vitepress.dev/reference/site-config
export default defineConfig({
  title: "LunaTranslator",
  head: [
    ['link', { rel: 'icon', href: 'https://image.lunatranslator.org/luna.ico' }],
  ],
  rewrites: {
    //  'zh/:rest*': ':rest*'
  },

  lastUpdated: true,
  themeConfig: {
    // https://vitepress.dev/reference/default-theme-config
    socialLinks: [
      { icon: 'github', link: 'https://github.com/HIllya51/LunaTranslator' }
    ],
    outline: {
      level: [2, 3],
    },
    search: {
      provider: 'local', options: {
        locales: {
          ...zhSearch,
          ...jaSearch,
          ...viSearch,
          ...chtSearch,
          ...koSearch,
        }
      }
    },
    logo: 'https://image.lunatranslator.org/luna.ico'
  },

  locales: {
    zh: { label: '简体中文', ...zh },
    cht: { label: '繁體中文', ...cht },
    en: { label: 'English', ...en },
    ja: { label: '日本語', ...ja },
    vi: { label: 'Tiếng Việt', ...vi },
    ko: { label: '한국어', ...ko },
  },
  ignoreDeadLinks: true,
  markdown: {
    config(md) {
      md.use(tabsMarkdownPlugin)
    }
  }
})