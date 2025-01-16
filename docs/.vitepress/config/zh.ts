import { defineConfig } from 'vitepress'

export const zh = defineConfig({
    lang: 'zh-CN',
    description: 'LunaTranslator',
    themeConfig: {
        outline: {
            label: "页面导航"
        },

        nav: [
            { text: "官方网站", link: "https://lunatranslator.org/" },
            {
                text: "软件下载", items: [
                    { text: "64位", link: "https://github.com/HIllya51/LunaTranslator/releases/latest/download/LunaTranslator.zip" },
                    { text: "32位", link: "https://github.com/HIllya51/LunaTranslator/releases/latest/download/LunaTranslator_x86.zip" }
                ]
            },
            { text: "视频教学", link: "https://space.bilibili.com/592120404/video" },
            { text: "QQ群963119821", link: "https://qm.qq.com/q/I5rr3uEpi2" }
        ],
        sidebar: [
            {
                text: '基本的',
                items: [
                    { text: '下载和启动', link: '/zh/README' },
                    { text: '无法启动软件', link: '/zh/cantstart' },
                    { text: '基本用法', link: '/zh/basicuse' },
                    { text: '软件更新', link: '/zh/update' },
                    { text: '支持作者', link: '/zh/support' }
                ]
            },
            {
                text: '详细的',
                items: [
                    {
                        text: 'HOOK相关设置', link: '/zh/hooksettings',
                        collapsed: true,
                        items: [
                            { text: 'HOOK设置', link: '/zh/hooksettings' },
                            { text: '内嵌翻译', link: '/zh/embedtranslate' },
                            { text: '在XP虚拟机上玩古老游戏并提取文本翻译', link: '/zh/playonxp' }
                        ]
                    },
                    {
                        text: 'OCR相关设置', link: '/zh/useapis/ocrapi',
                        collapsed: true,
                        items: [
                            { text: 'OCR接口设置', link: '/zh/useapis/ocrapi' },
                            { text: 'OCR自动化执行方法', link: '/zh/ocrparam' },
                            { text: 'OCR模式绑定游戏窗口', link: '/zh/gooduseocr' }
                        ]
                    },
                    {
                        text: '翻译接口设置', link: '/zh/useapis/tsapi',
                        collapsed: true,
                        items: [
                            { text: '传统在线翻译接口', link: '/zh/useapis/tsapi' },
                            { text: '大模型API翻译', link: '/zh/guochandamoxing' },
                            { text: '大模型离线翻译', link: '/zh/offlinellm' }
                        ]
                    },
                    {
                        text: '文本处理&翻译优化', link: '/zh/textprocess',
                        collapsed: true,
                        items: [
                            { text: '各种文本处理方法的作用和用法', link: '/zh/textprocess' },
                            { text: '各种翻译优化的作用', link: '/zh/transoptimi' }
                        ]
                    },
                    { text: '语音合成', link: '/zh/ttsofname' },
                    {
                        text: '分词&辞书', link: '/zh/qa1',
                        collapsed: true,
                        items: [
                            { text: '使用Mecab分词&词性颜色标注', link: '/zh/qa1' },
                            { text: 'Anki集成', link: '/zh/qa2' }
                        ]
                    },
                    { text: '工具按钮', link: '/zh/alltoolbuttons' },
                    { text: '快捷按键', link: '/zh/fastkeys' }
                ]
            }
        ]
    }
})