import { defineConfig } from 'vitepress'
import { en } from './en'
import { zh, zhSearch } from './zh'
import { ja, jaSearch } from './ja'
import { tabsMarkdownPlugin } from 'vitepress-plugin-tabs'

// https://vitepress.dev/reference/site-config
export default defineConfig({
  title: "LunaTranslator",
  head: [
    ['link', { rel: 'icon', href: 'https://image.lunatranslator.org/luna.ico' }],
    ['script', {},
      `
window.onload = function () {
  if (window.location.hostname.startsWith('docs')) {
    let replacetarget2 = window.location.protocol + '//' + window.location.hostname.substring(5);
    let ele = document.querySelector("#app > div > header > div > div.wrapper > div > div.content > div > nav > a:nth-child(2)")
    if (ele) {
      ele.href = ele.href.replace('https://lunatranslator.org', replacetarget2)
    }
  }
}
function openlink(url) {
    window.open(window.location.protocol + '//' + window.location.hostname.substring(5) + '/' + url, "_blank")
}
      `]
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
          ...jaSearch
        }
      }
    },
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