import { defineConfig } from 'vitepress'

export const en = defineConfig({

    themeConfig: {
        footer: {
            copyright: `Released under the <a href="https://github.com/HIllya51/LunaTranslator/blob/main/LICENSE">GPLv3</a> license`
        },
        nav: [
            { text: "HomePage", link: "https://lunatranslator.org/" },
            { text: "Discord", link: "https://discord.com/invite/ErtDwVeAbB" },
            { text: "Sponsorship", link: "/en/support" },
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
                    { text: 'Basic Usage', link: '/en/basicuse' },
                    { text: 'Software Update', link: '/en/update' },
                    { text: 'Sponsorship', link: '/en/support' }
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
                            { text: 'Emulator Game Support', link: '/en/emugames' },
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
                            { text: 'Large Model Translation Interface', link: '/en/guochandamoxing' },
                            { text: 'Traditional online translation interface', link: '/en/useapis/tsapi' },
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
                    {
                        text: 'Tổng hợp giọng nói', link: '/en/ttsengines',
                        collapsed: true,
                        items: [
                            { text: 'Công cụ Tổng hợp Giọng nói', link: '/en/ttsengines' },
                            { text: 'Using Different Voices for Different Characters', link: '/en/ttsofname' }
                        ]
                    },
                    {
                        text: 'Tokenization & Dictionary & Anki', link: '/en/qa1',
                        collapsed: true,
                        items: [
                            { text: 'Using Mecab for Tokenization & Part-of-Speech Color Annotation', link: '/en/qa1' },
                            { text: 'Anki Integration', link: '/en/qa2' }
                        ]
                    },
                    { text: 'Tool Buttons', link: '/en/alltoolbuttons' },
                    { text: 'Shortcut Keys', link: '/en/fastkeys' },
                    { text: 'Network Service', link: '/en/apiservice' },
                ]
            }
        ]
    }
})