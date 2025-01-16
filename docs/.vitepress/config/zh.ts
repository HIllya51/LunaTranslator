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
            message: "<a href='support'>支持作者</a>",
            copyright: `基于 GPLv3 许可发布`
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
            { text: "QQ群963119821", link: "https://qm.qq.com/q/I5rr3uEpi2" }
        ],
        sidebar: [
            {
                text: '基本的',
                items: [
                    { text: '下载和启动', link: './README' },
                    { text: '无法启动软件', link: './cantstart' },
                    { text: '基本用法', link: './basicuse' },
                    { text: '软件更新', link: './update' },
                    { text: '支持作者', link: './support' }
                ]
            },
            {
                text: '详细的',
                items: [
                    {
                        text: 'HOOK相关设置', link: './hooksettings',
                        collapsed: true,
                        items: [
                            { text: 'HOOK设置', link: './hooksettings' },
                            { text: '内嵌翻译', link: './embedtranslate' },
                            { text: '在XP虚拟机上玩古老游戏并提取文本翻译', link: './playonxp' }
                        ]
                    },
                    {
                        text: 'OCR相关设置', link: './useapis/ocrapi',
                        collapsed: true,
                        items: [
                            { text: 'OCR接口设置', link: './useapis/ocrapi' },
                            { text: 'OCR自动化执行方法', link: './ocrparam' },
                            { text: 'OCR模式绑定游戏窗口', link: './gooduseocr' }
                        ]
                    },
                    {
                        text: '翻译接口设置', link: './useapis/tsapi',
                        collapsed: true,
                        items: [
                            { text: '传统在线翻译接口', link: './useapis/tsapi' },
                            { text: '大模型API翻译', link: './guochandamoxing' },
                            { text: '大模型离线翻译', link: './offlinellm' }
                        ]
                    },
                    {
                        text: '文本处理&翻译优化', link: './textprocess',
                        collapsed: true,
                        items: [
                            { text: '各种文本处理方法的作用和用法', link: './textprocess' },
                            { text: '各种翻译优化的作用', link: './transoptimi' }
                        ]
                    },
                    { text: '语音合成', link: './ttsofname' },
                    {
                        text: '分词&辞书', link: './qa1',
                        collapsed: true,
                        items: [
                            { text: '使用Mecab分词&词性颜色标注', link: './qa1' },
                            { text: 'Anki集成', link: './qa2' }
                        ]
                    },
                    { text: '工具按钮', link: './alltoolbuttons' },
                    { text: '快捷按键', link: './fastkeys' }
                ]
            }
        ]
    }
})