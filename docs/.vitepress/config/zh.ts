import { defineConfig } from 'vitepress'
//https://github.com/vuejs/vitepress/blob/main/docs/.vitepress/config/zh.ts#L161C2-L205C2
export const zhSearch = {
    zh: {
        placeholder: '搜索文档',
        translations: {
            button: {
                buttonText: '搜索文档',
                buttonAriaLabel: '搜索文档'
            },
            modal: {
                searchBox: {
                    resetButtonTitle: '清除查询条件',
                    resetButtonAriaLabel: '清除查询条件',
                    cancelButtonText: '取消',
                    cancelButtonAriaLabel: '取消'
                },
                startScreen: {
                    recentSearchesTitle: '搜索历史',
                    noRecentSearchesText: '没有搜索历史',
                    saveRecentSearchButtonTitle: '保存至搜索历史',
                    removeRecentSearchButtonTitle: '从搜索历史中移除',
                    favoriteSearchesTitle: '收藏',
                    removeFavoriteSearchButtonTitle: '从收藏中移除'
                },
                errorScreen: {
                    titleText: '无法获取结果',
                    helpText: '你可能需要检查你的网络连接'
                },
                footer: {
                    selectText: '选择',
                    navigateText: '切换',
                    closeText: '关闭',
                    searchByText: '搜索提供者'
                },
                noResultsScreen: {
                    noResultsText: '无法找到相关结果',
                    suggestedQueryText: '你可以尝试查询',
                    reportMissingResultsText: '你认为该查询应该有结果？',
                    reportMissingResultsLinkText: '点击反馈'
                }
            }
        }
    }
}
export const zh = defineConfig({
    themeConfig: {
        outline: {
            level: [2, 3],
            label: "页面导航"
        },
        footer: {
            copyright: `基于 <a href="https://github.com/HIllya51/LunaTranslator/blob/main/LICENSE">GPLv3</a> 许可发布`
        },

        editLink: {
            pattern: 'https://github.com/HIllya51/LunaTranslator/edit/main/docs/:path',
            text: '在 GitHub 上编辑此页面'
        },

        docFooter: {
            prev: '上一页',
            next: '下一页'
        },

        lastUpdated: {
            text: '最后更新于',
            formatOptions: {
                dateStyle: 'short',
                timeStyle: 'medium'
            }
        },
        nav: [
            { text: "官方网站", link: "https://lunatranslator.org/" },
            { text: "视频教学", link: "https://space.bilibili.com/592120404/video" },
            { text: "QQ群963119821", link: "https://qm.qq.com/q/I5rr3uEpi2" },
            { text: "支持作者", link: "/zh/support" },
        ],
        sidebar: [
            {
                text: '基本的',
                items: [
                    { text: '下载和启动', link: '/zh/README' },
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
                            { text: '模拟器游戏支持', link: '/zh/emugames' },
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
                            { text: '大模型在线翻译', link: '/zh/guochandamoxing' },
                            { text: '大模型离线翻译', link: '/zh/offlinellm' },
                            { text: '传统在线翻译接口', link: '/zh/useapis/tsapi' },
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
                    { text: '快捷按键', link: '/zh/fastkeys' },
                    { text: '网络服务', link: '/zh/apiservice' },
                ]
            }
        ]
    }
})