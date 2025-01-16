import { defineConfig } from 'vitepress'

export const en = defineConfig({

    themeConfig: {
        footer: {
            message: "<a href='support'>Support the author</a>",
            copyright: `Released under the GPLv3 license`
        },
        nav: [
            { text: "HomePage", link: "https://lunatranslator.org/" },
            { text: "Vedio Tutorial", link: "https://www.youtube.com/results?search_query=LunaTranslator" },
            { text: "Discord", link: "https://discord.com/invite/ErtDwVeAbB" }
        ],
        editLink: {
            pattern: 'https://github.com/vuejs/vitepress/edit/main/docs/:path',
            text: 'Edit this page on GitHub'
        },
        sidebar: [
            {
                text: 'Basic',
                items: [
                    { text: 'Download and Launch', link: '/en/README' },
                    { text: 'Unable to Start the Software', link: '/en/cantstart' },
                    { text: 'Basic Usage', link: '/en/basicuse' },
                    { text: 'Software Update', link: '/en/update' },
                    { text: 'Support the Author', link: '/en/support' }
                ]
            },
            {
                text: 'Detailed',
                items: [
                    {
                        text: 'HOOK Related Settings', link: '/en/hooksettings',
                        collapsed: true,
                        items: [
                            { text: 'HOOK Settings', link: '/en/hooksettings' },
                            { text: 'Embedded Translation', link: '/en/embedtranslate' },
                            { text: 'Playing Old Games on XP Virtual Machine and Extracting Text for Translation', link: '/en/playonxp' }
                        ]
                    },
                    {
                        text: 'OCR Related Settings', link: '/en/useapis/ocrapi',
                        collapsed: true,
                        items: [
                            { text: 'OCR interface settings', link: '/en/useapis/ocrapi' },
                            { text: 'OCR Automation Execution Methods', link: '/en/ocrparam' },
                            { text: 'Binding Game Window in OCR Mode', link: '/en/gooduseocr' }
                        ]
                    },
                    {
                        text: 'Translation interface settings', link: '/en/useapis/tsapi',
                        collapsed: true,
                        items: [
                            { text: 'Traditional online translation interface', link: '/en/useapis/tsapi' },
                            { text: 'Large Model API for Translation', link: '/en/guochandamoxing' },
                            { text: 'Large Model Offline Translation', link: '/en/offlinellm' }
                        ]
                    },
                    {
                        text: 'Text Processing & Translation Optimization', link: '/en/textprocess',
                        collapsed: true,
                        items: [
                            { text: 'Functions and Usage of Various Text Processing Methods', link: '/en/textprocess' },
                            { text: 'Functions of Various Translation Optimizations', link: '/en/transoptimi' }
                        ]
                    },
                    { text: 'Speech Synthesis', link: '/en/ttsofname' },
                    {
                        text: 'Tokenization & Dictionary', link: '/en/qa1',
                        collapsed: true,
                        items: [
                            { text: 'Using Mecab for Tokenization & Part-of-Speech Color Annotation', link: '/en/qa1' },
                            { text: 'Anki Integration', link: '/en/qa2' }
                        ]
                    },
                    { text: 'Tool Buttons', link: '/en/alltoolbuttons' },
                    { text: 'Shortcut Keys', link: '/en/fastkeys' }
                ]
            }
        ]
    }
})