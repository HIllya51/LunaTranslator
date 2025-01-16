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
                    { text: 'Download and Launch', link: './README' },
                    { text: 'Unable to Start the Software', link: './cantstart' },
                    { text: 'Basic Usage', link: './basicuse' },
                    { text: 'Software Update', link: './update' },
                    { text: 'Support the Author', link: './support' }
                ]
            },
            {
                text: 'Detailed',
                items: [
                    {
                        text: 'HOOK Related Settings', link: './hooksettings',
                        collapsed: true,
                        items: [
                            { text: 'HOOK Settings', link: './hooksettings' },
                            { text: 'Embedded Translation', link: './embedtranslate' },
                            { text: 'Playing Old Games on XP Virtual Machine and Extracting Text for Translation', link: './playonxp' }
                        ]
                    },
                    {
                        text: 'OCR Related Settings', link: './useapis/ocrapi',
                        collapsed: true,
                        items: [
                            { text: 'OCR interface settings', link: './useapis/ocrapi' },
                            { text: 'OCR Automation Execution Methods', link: './ocrparam' },
                            { text: 'Binding Game Window in OCR Mode', link: './gooduseocr' }
                        ]
                    },
                    {
                        text: 'Translation interface settings', link: './useapis/tsapi',
                        collapsed: true,
                        items: [
                            { text: 'Traditional online translation interface', link: './useapis/tsapi' },
                            { text: 'Large Model API for Translation', link: './guochandamoxing' },
                            { text: 'Large Model Offline Translation', link: './offlinellm' }
                        ]
                    },
                    {
                        text: 'Text Processing & Translation Optimization', link: './textprocess',
                        collapsed: true,
                        items: [
                            { text: 'Functions and Usage of Various Text Processing Methods', link: './textprocess' },
                            { text: 'Functions of Various Translation Optimizations', link: './transoptimi' }
                        ]
                    },
                    { text: 'Speech Synthesis', link: './ttsofname' },
                    {
                        text: 'Tokenization & Dictionary', link: './qa1',
                        collapsed: true,
                        items: [
                            { text: 'Using Mecab for Tokenization & Part-of-Speech Color Annotation', link: './qa1' },
                            { text: 'Anki Integration', link: './qa2' }
                        ]
                    },
                    { text: 'Tool Buttons', link: './alltoolbuttons' },
                    { text: 'Shortcut Keys', link: './fastkeys' }
                ]
            }
        ]
    }
})