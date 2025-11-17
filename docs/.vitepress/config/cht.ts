import { defineConfig } from 'vitepress'
//https://github.com/vuejs/vitepress/blob/main/docs/.vitepress/config/zh.ts#L161C2-L205C2
export const chtSearch = {
    cht: {
        placeholder: '搜尋文件',
        translations: {
            button: {
                buttonText: '搜尋文件',
                buttonAriaLabel: '搜尋文件'
            },
            modal: {
                searchBox: {
                    resetButtonTitle: '清除查詢條件',
                    resetButtonAriaLabel: '清除查詢條件',
                    cancelButtonText: '取消',
                    cancelButtonAriaLabel: '取消'
                },
                startScreen: {
                    recentSearchesTitle: '搜尋歷史',
                    noRecentSearchesText: '沒有搜尋歷史',
                    saveRecentSearchButtonTitle: '儲存至搜尋歷史',
                    removeRecentSearchButtonTitle: '從搜尋歷史中移除',
                    favoriteSearchesTitle: '我的最愛',
                    removeFavoriteSearchButtonTitle: '從我的最愛中移除'
                },
                errorScreen: {
                    titleText: '無法取得結果',
                    helpText: '您可能需要檢查您的網路連接'
                },
                footer: {
                    selectText: '選擇',
                    navigateText: '切換',
                    closeText: '關閉',
                    searchByText: '搜尋提供者'
                },
                noResultsScreen: {
                    noResultsText: '無法找到相關結果',
                    suggestedQueryText: '您可以嘗試查詢',
                    reportMissingResultsText: '您認為該查詢應該有結果？',
                    reportMissingResultsLinkText: '點擊回饋'
                }
            }
        }
    }
}
export const cht = defineConfig({
    themeConfig: {
        outline: {
            level: [2, 3],
            label: "頁面導覽"
        },
        footer: {
            copyright: `基於 <a href="https://github.com/HIllya51/LunaTranslator/blob/main/LICENSE">GPLv3</a> 授權條款發佈`
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
            { text: "影片教學", link: "https://space.bilibili.com/592120404/video" },
            { text: "QQ 群", link: "https://qm.qq.com/q/mPSu3sG5ri" },
            { text: "Discord", link: "https://discord.com/invite/ErtDwVeAbB" },
            { text: "支持作者", link: "/cht/support" },
        ],
        sidebar: [
            {
                text: '基本的',
                items: [
                    { text: '軟體下載 & 常見問題', link: '/cht/README' },
                    { text: '基本用法', link: '/cht/basicuse' },
                    { text: '支持作者', link: '/cht/support' }
                ]
            },
            {
                text: '詳細的',
                items: [
                    {
                        text: 'HOOK 相關設定', link: '/cht/hooksettings',
                        collapsed: true,
                        items: [
                            { text: 'HOOK 設定', link: '/cht/hooksettings' },
                            { text: '內嵌翻譯', link: '/cht/embedtranslate' },
                            { text: '模擬器遊戲支援', link: '/cht/emugames' },
                        ]
                    },
                    {
                        text: 'OCR 相關設定', link: '/cht/useapis/ocrapi',
                        collapsed: true,
                        items: [
                            { text: 'OCR 介面設定', link: '/cht/useapis/ocrapi' },
                            { text: 'OCR 自動化執行方法', link: '/cht/ocrparam' },
                        ]
                    },
                    {
                        text: '翻譯介面設定', link: '/cht/guochandamoxing',
                        collapsed: true,
                        items: [
                            { text: '大模型翻譯介面', link: '/cht/guochandamoxing' },
                            { text: '傳統線上翻譯介面', link: '/cht/useapis/tsapi' },
                        ]
                    },
                    {
                        text: '文字處理＆翻譯優化', link: '/cht/textprocess',
                        collapsed: true,
                        items: [
                            { text: '各種文字處理方法的作用和用法', link: '/cht/textprocess' },
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
                            { text: '日文分詞及假名注音', link: '/cht/qa1' },
                            { text: '使用內建查詞工具', link: '/cht/internaldict' },
                            { text: '安裝 Yomitan 瀏覽器外掛程式', link: '/cht/yomitan' },
                            { text: 'Anki 整合', link: '/cht/qa2' },
                            // { text: '中文分詞及注音', link: '/cht/jiebapinyin' },
                        ]
                    },
                    { text: '工具按鈕', link: '/cht/alltoolbuttons' },
                    { text: '快速按鍵', link: '/cht/fastkeys' },
                    { text: '網路服務', link: '/cht/apiservice' },
                    { text: '語音辨識', link: '/cht/sr' },
                    {
                        text: '實用技巧', link: '/cht/gooduse/multiconfigs',
                        collapsed: true,
                        items: [
                            { text: '建立多份設定檔', link: '/cht/gooduse/multiconfigs' },
                            { text: '在 HOOK 模式下臨時使用 OCR', link: '/cht/gooduse/useocrinhook' },
                            { text: 'OCR 模式綁定遊戲視窗', link: '/cht/gooduse/gooduseocr' },
                        ]
                    }
                ]
            }
        ]
    }
})