import { defineConfig } from 'vitepress'
import { en } from './en'
import { zh } from './zh'
import { ja } from './ja'
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

  themeConfig: {
    // https://vitepress.dev/reference/default-theme-config
    socialLinks: [
      { icon: 'github', link: 'https://github.com/HIllya51/LunaTranslator' }
    ],

    footer: {
      message: 'Made with ❤️️ love by <a href="https://github.com/HIllya51">HIllya51</a>.',
      copyright: 'Code licensed under MIT, documentation under <a href=\"https://creativecommons.org/licenses/by-sa/4.0/deed.en\">CC BY-SA 4.0</a>.</br>Art image from <a href=\"https://www.pixiv.net/artworks/92978748">Pixiv</a>.'
    },

    logo: 'https://image.lunatranslator.org/luna.ico'
  },

  locales: {
    zh: { label: '简体中文', ...zh },
    en: { label: 'English', ...en },
    ja: { label: '日本語', ...ja }
  },
  ignoreDeadLinks: true,
  markdown: {
    config(md) {
      md.use(tabsMarkdownPlugin)
    }
  }
})