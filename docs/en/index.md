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
      text: Download and Start  
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
    details: Supports HOOK emulators to directly extract text from most games on NS/PSP/PSV/PS3.
    link: ./emugames
  - title: OCR  
    details: Built-in high-precision OCR model, supporting many other online & offline OCR engines for flexible text extraction.  
    link: ./useapis/ocrapi
  - title: Rich Translation APIs  
    details: Supports almost all translation engines, including large language model translation, offline translation, and more.
    link: ./useapis/tsapi
  - title: Dictionary & Anki Integration  
    details: Supports Mecab, MDict, online dictionaries, and AnkiConnect.
    link: ./qa1
  - title: Text-to-Speech  
    details: Supports a wide range of online & offline text-to-speech engines.  
  - title: Highly Configurable  
    details: Offers extensive configuration options to tailor the translation experience to your needs.  