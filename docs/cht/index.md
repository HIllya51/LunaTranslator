---
# https://vitepress.dev/reference/default-theme-home-page
layout: home

hero:
  name: "LunaTranslator"
  # text: "Galgame 翻譯器，支援 HOOK、OCR、剪貼簿等"
  # tagline: 💡 快速翻譯，輕鬆學習日文！
  # image:
  #   src: /assets/bg.jpg
  #   alt: LunaTranslator
  actions:
    - theme: brand
      text: 軟體下載 & 常見問題
      link: ./README
    - theme: alt
      text: 基本用法
      link: ./basicuse
    - theme: alt
      text: 支持作者
      link: ./support
    - theme: alt
      text: Github
      link: https://github.com/HIllya51/LunaTranslator

features:
  - title: HOOK
    details: 主要使用 HOOK 擷取遊戲文字，幾乎支援了所有的常見和冷門的視覺小說
    link: ./hooksettings
  - title: 內嵌翻譯
    details: 部份遊戲還可以直接內嵌翻譯到遊戲中，以獲得沉浸式體驗
    link: ./embedtranslate
  - title: HOOK 模擬器
    details: 對 NS/PSP/PSV/PS2 上的大部份遊戲，支援 HOOK 模擬器以直接讀取遊戲文字
    link: ./emugames
  - title: OCR
    details: 內建較高精度的 OCR 模型，並支援許多其他線上＆離線 OCR 引擎，以便靈活的讀取任意文字
    link: ./useapis/ocrapi
  - title: 豐富的翻譯介面
    details: 支援幾乎所有翻譯引擎，包括大語言模型翻譯、離線翻譯等
    link: ./guochandamoxing
  - title: 語言學習
    details: 支援日文分詞及假名讀音標註，支援 AnkiConnect，支援 Yomitan 擴充功能
    link: ./qa1
  - title: 語音合成
    details: 支援大量線上＆離線語音合成引擎
    link: ./ttsengines
  - title: 語音辨識
    details: 在 Windows 10 和 Windows 11 上，可以使用 Windows 語音辨識
    link: ./sr

