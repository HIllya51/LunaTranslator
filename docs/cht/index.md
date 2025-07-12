---
# https://vitepress.dev/reference/default-theme-home-page
layout: home

hero:
  name: "LunaTranslator"
  # text: "Galgame翻譯器，支持HOOK、OCR、剪貼板等"
  # tagline: 💡 快速翻譯，輕鬆學習日語！
  # image:
  #   src: /assets/bg.jpg
  #   alt: LunaTranslator
  actions:
    - theme: brand
      text: 下載&啟動&更新
      link: ./README
    - theme: alt
      text: 基本用法
      link: ./basicuse
    - theme: alt
      text: Github
      link: https://github.com/HIllya51/LunaTranslator

features:
  - title: HOOK
    details: 主要使用HOOK提取遊戲文本，幾乎適配了所有的常見和冷門的視覺小說
    link: ./hooksettings
  - title: 內嵌翻譯
    details: 部分遊戲還可以直接內嵌翻譯到遊戲中，以獲取沉浸式體驗
    link: ./embedtranslate
  - title: HOOK模擬器
    details: 對NS/PSP/PSV/PS2上的大部分遊戲，支持HOOK模擬器直接讀取遊戲文本
    link: ./emugames
  - title: OCR
    details: 內置較高精度的OCR模型，並支持許多其他在線&離線OCR引擎，以便靈活的讀取任意文本
    link: ./useapis/ocrapi
  - title: 豐富的翻譯接口
    details: 支持幾乎所有翻譯引擎，包括大語言模型翻譯、離線翻譯等
    link: ./useapis/tsapi
  - title: 語言學習
    details: 支援日語分詞及假名注音，支援AnkiConnect，支援Yomitan插件
    link: ./qa1
  - title: 語音合成
    details: 支持大量在線&離線語音合成引擎
    link: ./ttsengines
  - title: 語音識別
    details: 在Windows 10和Windows 11上，可以使用Windows語音識別。
    link: ./sr

