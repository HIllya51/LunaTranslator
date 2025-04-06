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
window.onmousemove = function(){
  if (!window.location.hostname.startsWith('docs'))return;
  {
    let replacetarget = window.location.protocol + '//image.' + window.location.hostname.substring(5);
    let origin='https://image.lunatranslator.org'
    let images = document.getElementsByTagName('img');
    for (var i = 0; i < images.length; i++) {
      if(images[i].src!=images[i].src.replace(origin, replacetarget))
        images[i].src = images[i].src.replace(origin, replacetarget)
    }
  }
  {
    let replacetarget = window.location.protocol + '//' + window.location.hostname.substring(5);
    let origin='https://lunatranslator.org'
    let srcs = document.getElementsByTagName('a');
    for (var i = 0; i < srcs.length; i++) {
      if(srcs[i].href!=srcs[i].href.replace(origin, replacetarget))
        srcs[i].href = srcs[i].href.replace(origin, replacetarget)
    }
  }
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