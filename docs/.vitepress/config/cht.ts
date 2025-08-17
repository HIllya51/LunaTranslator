import { defineConfig } from 'vitepress'
//https://github.com/vuejs/vitepress/blob/main/docs/.vitepress/config/zh.ts#L161C2-L205C2
export const chtSearch = {
    cht: {
        placeholder: '搜索文檔',
        translations: {
            button: {
                buttonText: '搜索文檔',
                buttonAriaLabel: '搜索文檔'
            },
            modal: {
                searchBox: {
                    resetButtonTitle: '清除查詢條件',
                    resetButtonAriaLabel: '清除查詢條件',
                    cancelButtonText: '取消',
                    cancelButtonAriaLabel: '取消'
                },
                startScreen: {
                    recentSearchesTitle: '搜索歷史',
                    noRecentSearchesText: '沒有搜索歷史',
                    saveRecentSearchButtonTitle: '保存至搜索歷史',
                    removeRecentSearchButtonTitle: '從搜索歷史中移除',
                    favoriteSearchesTitle: '收藏',
                    removeFavoriteSearchButtonTitle: '從收藏中移除'
                },
                errorScreen: {
                    titleText: '無法獲取結果',
                    helpText: '你可能需要檢查你的網絡連接'
                },
                footer: {
                    selectText: '選擇',
                    navigateText: '切換',
                    closeText: '關閉',
                    searchByText: '搜索提供者'
                },
                noResultsScreen: {
                    noResultsText: '無法找到相關結果',
                    suggestedQueryText: '你可以嘗試查詢',
                    reportMissingResultsText: '你認爲該查詢應該有結果？',
                    reportMissingResultsLinkText: '點擊反饋'
                }
            }
        }
    }
}
export const cht = defineConfig({
    themeConfig: {
        outline: {
            level: [2, 3],
            label: "頁面導航"
        },
        footer: {
            copyright: `基於 <a href="https://github.com/HIllya51/LunaTranslator/blob/main/LICENSE">GPLv3</a> 許可發佈`
        },

        editLink: {
            pattern: 'https://github.com/HIllya51/LunaTranslator/edit/main/docs/:path',
            text: '在 GitHub 上編輯此頁面'
        },

        docFooter: {
            prev: '上一頁',
            next: '下一頁'
        },

        lastUpdated: {
            text: '最後更新於',
            formatOptions: {
                dateStyle: 'short',
                timeStyle: 'medium'
            }
        },
        nav: [
            // { text: "官方網站", link: "https://lunatranslator.org/" },
            { text: "視頻教程", link: "https://space.bilibili.com/592120404/video" },
            { text: "QQ羣", link: "https://qm.qq.com/q/I5rr3uEpi2" },
            { text: "Discord", link: "https://discord.com/invite/ErtDwVeAbB" },
            { text: "支持作者", link: "/cht/support" },
        ],
        sidebar: [
            {
                text: '基本的',
                items: [
                    { text: '下載 & 啟動 & 更新', link: '/cht/README' },
                    { text: '基本用法', link: '/cht/basicuse' },
                    { text: '支持作者', link: '/cht/support' }
                ]
            },
            {
                text: '詳細的',
                items: [
                    {
                        text: 'HOOK相關設置', link: '/cht/hooksettings',
                        collapsed: true,
                        items: [
                            { text: 'HOOK設置', link: '/cht/hooksettings' },
                            { text: '內嵌翻譯', link: '/cht/embedtranslate' },
                            { text: '模擬器遊戲支持', link: '/cht/emugames' },
                        ]
                    },
                    {
                        text: 'OCR相關設置', link: '/cht/useapis/ocrapi',
                        collapsed: true,
                        items: [
                            { text: 'OCR接口設置', link: '/cht/useapis/ocrapi' },
                            { text: 'OCR自動化執行方法', link: '/cht/ocrparam' },
                        ]
                    },
                    {
                        text: '翻譯接口設置', link: '/cht/useapis/tsapi',
                        collapsed: true,
                        items: [
                            { text: '大模型翻譯接口', link: '/cht/guochandamoxing' },
                            { text: '傳統在線翻譯接口', link: '/cht/useapis/tsapi' },
                        ]
                    },
                    {
                        text: '文本處理&翻譯優化', link: '/cht/textprocess',
                        collapsed: true,
                        items: [
                            { text: '各種文本處理方法的作用和用法', link: '/cht/textprocess' },
                            { text: '各種翻譯優化的作用', link: '/cht/transoptimi' }
                        ]
                    },
                    {
                        text: '語音合成', link: '/cht/ttsengines',
                        collapsed: true,
                        items: [
                            { text: '語音合成引擎', link: '/cht/ttsengines' },
                            { text: '根據不同的人物使用不同的聲音', link: '/cht/ttsofname' }
                        ]
                    },
                    {
                        text: '語言學習', link: '/cht/qa1',
                        collapsed: true,
                        items: [
                            { text: '日語分詞及假名注音', link: '/cht/qa1' },
                            { text: '使用內建查詞工具', link: '/cht/internaldict' },
                            { text: '安裝Yomitan瀏覽器插件', link: '/cht/yomitan' },
                            { text: 'Anki集成', link: '/cht/qa2' },
                        ]
                    },
                    { text: '工具按鈕', link: '/cht/alltoolbuttons' },
                    { text: '快捷按鍵', link: '/cht/fastkeys' },
                    { text: '網絡服務', link: '/cht/apiservice' },
                    { text: '語音識別', link: '/cht/sr' },
                    {
                        text: '實用技巧', link: '/cht/gooduse/multiconfigs',
                        collapsed: true,
                        items: [
                            { text: '創建多份配置檔案', link: '/cht/gooduse/multiconfigs' },
                            { text: '在HOOK模式下臨時使用OCR', link: '/cht/gooduse/useocrinhook' },
                            { text: 'OCR模式綁定遊戲窗口', link: '/cht/gooduse/gooduseocr' },
                        ]
                    }
                ]
            }
        ]
    }
})