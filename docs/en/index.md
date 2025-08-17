---  
# https://vitepress.dev/reference/default-theme-home-page  
layout: home  

hero:  
  name: "LunaTranslator"  
  # text: "Galgame Translator, supporting HOOK, OCR, Clipboard, and more"  
  # tagline: 💡 Quick translation, easy Japanese learning!  
  # image:  
  #   src: /assets/bg.jpg  
  #   alt: LunaTranslator  
  actions:  
    - theme: brand  
      text: Download & Launch & Update
      link: ./README  
    - theme: alt  
      text: Basic Usage  
      link: ./basicuse  
    - theme: alt  
      text: Github  
      link: https://github.com/HIllya51/LunaTranslator  

features:  
  - title: HOOK  
    details: Primarily uses HOOK to extract game text, compatible with almost all popular and niche visual novels.  
    link: ./hooksettings
  - title: Embedded Translation  
    details: Some games also support directly embedding translations into the game for an immersive experience.
    link: ./embedtranslate
  - title: HOOK Emulator  
    details: Supports HOOK emulators to directly extract text from most games on NS/PSP/PSV/PS2.
    link: ./emugames
  - title: OCR  
    details: Built-in high-precision OCR model, supporting many other online & offline OCR engines for flexible text extraction.  
    link: ./useapis/ocrapi
  - title: Rich Translation APIs  
    details: Supports almost all translation engines, including large language model translation, offline translation, and more.
    link: ./guochandamoxing
  - title: Language Learning
    details: Supports Japanese word segmentation and kana annotation, supports AnkiConnect, supports Yomitan plugin
    link: ./qa1
  - title: Text-to-Speech  
    details: Supports a wide range of online & offline text-to-speech engines.  
    link: ./ttsengines
  - title: Speech Recognition
    details: On Windows 10 and Windows 11, you can use Windows Speech Recognition.
    link: ./sr