import { defineConfig } from 'vitepress'

export const ruSearch = {
    ru: {
        placeholder: 'Поиск документов',
        translations: {
            button: {
                buttonText: 'Поиск документов',
                buttonAriaLabel: 'Поиск документов'
            },
            modal: {
                searchBox: {
                    resetButtonTitle: 'Очистить условия поиска',
                    resetButtonAriaLabel: 'Очистить условия поиска',
                    cancelButtonText: 'Отмена',
                    cancelButtonAriaLabel: 'Отмена'
                },
                startScreen: {
                    recentSearchesTitle: 'История поиска',
                    noRecentSearchesText: 'Нет истории поиска',
                    saveRecentSearchButtonTitle: 'Сохранить в историю поиска',
                    removeRecentSearchButtonTitle: 'Удалить из истории поиска',
                    favoriteSearchesTitle: 'Избранное',
                    removeFavoriteSearchButtonTitle: 'Удалить из избранного'
                },
                errorScreen: {
                    titleText: 'Не удалось получить результаты',
                    helpText: 'Проверьте подключение к интернету'
                },
                footer: {
                    selectText: 'Выбрать',
                    navigateText: 'Переключить',
                    closeText: 'Закрыть',
                    searchByText: 'Поиск предоставлен'
                },
                noResultsScreen: {
                    noResultsText: 'Не найдено соответствующих результатов',
                    suggestedQueryText: 'Попробуйте запрос',
                    reportMissingResultsText: 'Должны ли быть результаты по этому запросу?',
                    reportMissingResultsLinkText: 'Нажмите для обратной связи'
                }
            }
        }
    }
}

export const ru = defineConfig({
    themeConfig: {
        outline: {
            level: [2, 3],
            label: "Навигация по странице"
        },
        footer: {
            copyright: `Опубликовано под лицензией <a href="https://github.com/HIllya51/LunaTranslator/blob/main/LICENSE">GPLv3</a>`
        },

        editLink: {
            pattern: 'https://github.com/HIllya51/LunaTranslator/edit/main/docs/:path',
            text: 'Редактировать эту страницу на GitHub'
        },

        docFooter: {
            prev: 'Предыдущая',
            next: 'Следующая'
        },

        lastUpdated: {
            text: 'Последнее обновление',
            formatOptions: {
                dateStyle: 'short',
                timeStyle: 'medium'
            }
        },
        nav: [
            // { text: "Официальный сайт", link: "https://lunatranslator.org/" },
            { text: "Discord", link: "https://discord.com/invite/ErtDwVeAbB" },
            { text: "Поддержать автора", link: "/ru/support" },
        ],
        sidebar: [
            {
                text: 'Основное',
                items: [
                    { text: 'Загрузка программного обеспечения & Часто задаваемые вопросы', link: '/ru/README' },
                    { text: 'Основное использование', link: '/ru/basicuse' },
                    { text: 'Поддержать автора', link: '/ru/support' }
                ]
            },
            {
                text: 'Подробное',
                items: [
                    {
                        text: 'Настройки HOOK', link: '/ru/hooksettings',
                        collapsed: true,
                        items: [
                            { text: 'Настройки HOOK', link: '/ru/hooksettings' },
                            { text: 'Встроенный перевод', link: '/ru/embedtranslate' },
                            { text: 'Поддержка игр на эмуляторах', link: '/ru/emugames' },
                        ]
                    },
                    {
                        text: 'Настройки OCR', link: '/ru/useapis/ocrapi',
                        collapsed: true,
                        items: [
                            { text: 'Настройки интерфейса OCR', link: '/ru/useapis/ocrapi' },
                            { text: 'Методы автоматизации OCR', link: '/ru/ocrparam' },
                        ]
                    },
                    {
                        text: 'Настройки интерфейса перевода', link: '/ru/guochandamoxing',
                        collapsed: true,
                        items: [
                            { text: 'Интерфейсы перевода на больших моделях', link: '/ru/guochandamoxing' },
                            { text: 'Традиционные онлайн-интерфейсы перевода', link: '/ru/useapis/tsapi' },
                        ]
                    },
                    {
                        text: 'Обработка текста и оптимизация перевода', link: '/ru/textprocess',
                        collapsed: true,
                        items: [
                            { text: 'Методы обработки текста и их применение', link: '/ru/textprocess' },
                            { text: 'Оптимизации перевода и их функции', link: '/ru/transoptimi' }
                        ]
                    },
                    {
                        text: 'Синтез речи', link: '/ru/ttsengines',
                        collapsed: true,
                        items: [
                            { text: 'Движки синтеза речи', link: '/ru/ttsengines' },
                            { text: 'Использование разных голосов для разных персонажей', link: '/ru/ttsofname' }
                        ]
                    },
                    {
                        text: 'Изучение языков', link: '/ru/qa1',
                        collapsed: true,
                        items: [
                            { text: 'Японская сегментация слов и произношение каной', link: '/ru/qa1' },
                            { text: 'Использование встроенного инструмента для поиска слов', link: '/ru/internaldict' },
                            { text: 'Установите расширение для браузера Yomitan', link: '/ru/yomitan' },
                            { text: 'Интеграция с Anki', link: '/ru/qa2' },
                        ]
                    },
                    { text: 'Инструментальные кнопки', link: '/ru/alltoolbuttons' },
                    { text: 'Горячие клавиши', link: '/ru/fastkeys' },
                    { text: 'Сетевые сервисы', link: '/ru/apiservice' },
                    { text: 'Распознавание речи', link: '/ru/sr' },
                    {
                        text: 'Практические советы', link: '/ru/gooduse/multiconfigs',
                        collapsed: true,
                        items: [
                            { text: 'Создание нескольких конфигурационных файлов', link: '/ru/gooduse/multiconfigs' },
                            { text: 'Временное использование OCR в режиме HOOK  ', link: '/ru/gooduse/useocrinhook' },
                            { text: 'OCR Привязка к игровому окну', link: '/ru/gooduse/gooduseocr' },
                        ]
                    },
                ]
            }
        ]
    }
})