import { defineConfig } from 'vitepress'
export const jaSearch = {
    ja: {
        placeholder: 'ドキュメントを検索',
        translations: {
            button: {
                buttonText: 'ドキュメントを検索',
                buttonAriaLabel: 'ドキュメントを検索'
            },
            modal: {
                searchBox: {
                    resetButtonTitle: '検索条件をクリア',
                    resetButtonAriaLabel: '検索条件をクリア',
                    cancelButtonText: 'キャンセル',
                    cancelButtonAriaLabel: 'キャンセル'
                },
                startScreen: {
                    recentSearchesTitle: '検索履歴',
                    noRecentSearchesText: '検索履歴はありません',
                    saveRecentSearchButtonTitle: '検索履歴に保存',
                    removeRecentSearchButtonTitle: '検索履歴から削除',
                    favoriteSearchesTitle: 'お気に入り',
                    removeFavoriteSearchButtonTitle: 'お気に入りから削除'
                },
                errorScreen: {
                    titleText: '結果を取得できません',
                    helpText: 'ネットワーク接続を確認してください'
                },
                footer: {
                    selectText: '選択',
                    navigateText: '切り替え',
                    closeText: '閉じる',
                    searchByText: '検索プロバイダ'
                },
                noResultsScreen: {
                    noResultsText: '関連する結果が見つかりません',
                    suggestedQueryText: '以下のクエリを試してみてください',
                    reportMissingResultsText: 'このクエリに結果があるべきだと思いますか？',
                    reportMissingResultsLinkText: 'フィードバックを送信'
                }
            }
        }
    }
}
export const ja = defineConfig({
    themeConfig: {
        outline: {
            level: [2, 3],
            label: "ページナビゲーション"
        },
        footer: {
            copyright: `<a href="https://github.com/HIllya51/LunaTranslator/blob/main/LICENSE">GPLv3</a> ライセンスに基づいて公開`
        },
        editLink: {
            pattern: 'https://github.com/HIllya51/LunaTranslator/edit/main/docs/:path',
            text: 'GitHubでこのページを編集'
        },

        docFooter: {
            prev: '前のページ',
            next: '次のページ'
        },

        lastUpdated: {
            text: '最終更新日',
            formatOptions: {
                dateStyle: 'short',
                timeStyle: 'medium'
            }
        },
        nav: [
            // { text: "公式サイト", link: "https://lunatranslator.org/" },
            { text: "Discord", link: "https://discord.com/invite/ErtDwVeAbB" },
            { text: "作者を支援する", link: "/ja/support" },
        ],
        sidebar: [
            {
                text: '基本的な',
                items: [
                    { text: 'ソフトウェアダウンロード & よくある質問', link: '/ja/README' },
                    { text: '基本の使い方', link: '/ja/basicuse' },
                    { text: '作者を支援する', link: '/ja/support' }
                ]
            },
            {
                text: '詳細な',
                items: [
                    {
                        text: 'HOOK関連設定', link: '/ja/hooksettings',
                        collapsed: true,
                        items: [
                            { text: 'HOOK設定', link: '/ja/hooksettings' },
                            { text: '埋め込み翻訳', link: '/ja/embedtranslate' },
                            { text: 'シミュレーターゲームサポート', link: '/ja/emugames' },
                        ]
                    },
                    {
                        text: 'OCR関連設定', link: '/ja/useapis/ocrapi',
                        collapsed: true,
                        items: [
                            { text: 'OCRインターフェース設定', link: '/ja/useapis/ocrapi' },
                            { text: 'OCR自動化実行方法', link: '/ja/ocrparam' },
                        ]
                    },
                    {
                        text: '翻訳インターフェース設定', link: '/ja/guochandamoxing',
                        collapsed: true,
                        items: [
                            { text: '大規模モデル翻訳インターフェース', link: '/ja/guochandamoxing' },
                            { text: '従来のオンライン翻訳インターフェース', link: '/ja/useapis/tsapi' },
                        ]
                    },
                    {
                        text: 'テキスト処理＆翻訳最適化', link: '/ja/textprocess',
                        collapsed: true,
                        items: [
                            { text: 'さまざまなテキスト処理方法の役割と使用方法', link: '/ja/textprocess' },
                            { text: 'さまざまな翻訳最適化の役割', link: '/ja/transoptimi' }
                        ]
                    },
                    {
                        text: '音声合成', link: '/ja/ttsengines',
                        collapsed: true,
                        items: [
                            { text: '音声合成エンジン', link: '/ja/ttsengines' },
                            { text: 'キャラクターごとに異なる声を使用した', link: '/ja/ttsofname' }
                        ]
                    },
                    {
                        text: '言語学習', link: '/ja/qa1',
                        collapsed: true,
                        items: [
                            { text: '日本語の分かち書きと仮名振り', link: '/ja/qa1' },
                            { text: '組み込み辞書ツールの使用方法', link: '/ja/internaldict' },
                            { text: 'Yomitanブラウザ拡張機能をインストールする', link: '/ja/yomitan' },
                            { text: 'Anki統合', link: '/ja/qa2' },
                            { text: '中国語分かち書きと振り仮名', link: '/ja/jiebapinyin' },
                        ]
                    },
                    { text: 'ツールボタン', link: '/ja/alltoolbuttons' },
                    { text: 'ショートカットキー', link: '/ja/fastkeys' },
                    { text: 'ネットワークサービス', link: '/ja/apiservice' },
                    { text: '音声認識', link: '/ja/sr' },
                    {
                        text: '実用テクニック', link: '/ja/gooduse/multiconfigs',
                        collapsed: true,
                        items: [
                            { text: '複数設定ファイルの作成', link: '/ja/gooduse/multiconfigs' },
                            { text: 'HOOKモードで一時的にOCRを使用する', link: '/ja/gooduse/useocrinhook' },
                            { text: 'OCRモードでゲームウィンドウをバインドする', link: '/ja/gooduse/gooduseocr' },
                        ]
                    },
                ]
            }
        ]
    }
})