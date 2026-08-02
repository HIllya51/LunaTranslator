---
# https://vitepress.dev/reference/default-theme-home-page
layout: home

hero:
  name: "LunaTranslator"
  # text: "Galgame翻译器，支持HOOK、OCR、剪贴板等"
  # tagline: 💡 快速翻译，轻松学习日语！
  # image:
  #   src: /assets/bg.jpg
  #   alt: LunaTranslator
  actions:
    - theme: brand
      text: 软件下载 & 常见问题
      link: ./README
    - theme: alt
      text: 基本用法
      link: ./basicuse
    - theme: alt
      text: 支持作者
      link: ./README#anchor-support
    - theme: alt
      text: Github
      link: https://github.com/HIllya51/LunaTranslator

features:
  - title: HOOK
    details: 主要使用HOOK提取游戏文本，几乎适配了所有的常见和冷门的视觉小说
    link: ./hooksettings
  - title: 内嵌翻译
    details: 部分游戏还可以直接内嵌翻译到游戏中，以获取沉浸式体验
    link: ./embedtranslate
  - title: HOOK模拟器
    details: 对NS/PSP/PSV/PS2上的大部分游戏，支持HOOK模拟器直接读取游戏文本
    link: ./emugames
  - title: OCR
    details: 内置较高精度的OCR模型，并支持许多其他在线&离线OCR引擎，以便灵活的读取任意文本
    link: ./useapis/ocrapi
  - title: 丰富的翻译接口
    details: 支持几乎所有翻译引擎，包括大语言模型翻译、离线翻译等
    link: ./guochandamoxing
  - title: 语言学习
    details: 支持日语分词及假名注音，支持AnkiConnect，支持Yomitan插件
    link: ./qa1
  - title: 语音合成
    details: 支持大量在线&离线语音合成引擎
    link: ./ttsengines
  - title: 语音识别
    details: 在Windows 10和Windows 11上，可以使用Windows语音识别。
    link: ./sr

