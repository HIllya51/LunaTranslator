# LunaTranslator

<p align="left">
    <img src="https://img.shields.io/github/license/HIllya51/LunaTranslator"> 
    <a href="https://github.com/HIllya51/LunaTranslator/releases"><img  src="https://img.shields.io/github/v/release/HIllya51/LunaTranslator?color=ffa"></a> 
    <a href="https://github.com/HIllya51/LunaTranslator/releases/latest/download/LunaTranslator.zip"  target="_blank"><img src="https://img.shields.io/badge/download_64bit-blue"/></a>  <a href="https://github.com/HIllya51/LunaTranslator/releases/latest/download/LunaTranslator_x86.zip"  target="_blank"><img src="https://img.shields.io/badge/download_32bit-blue"/></a>  <img src="https://img.shields.io/badge/OS-windows  7--11 / wine-FF0000"/>
</p>

### [User Manual](https://docs.lunatranslator.org/#/zh/)  [Video Tutorial](https://space.bilibili.com/592120404/video)  <a href="https://qm.qq.com/q/I5rr3uEpi2"><img  src="https://img.shields.io/badge/QQ Group-963119821-FF007C"></a>  <a href="https://discord.com/invite/ErtDwVeAbB"><img  src="https://img.shields.io/discord/1262692128031772733?label=Discord&logo=discord&color=FF007C"></a> 

### Simplified Chinese | [Russian](README_ru.md) | [English](README_en.md) | [Other Language](otherlang.md) 

> **A galgame translation tool**

## Feature Support

#### Text Input

- **HOOK** Supports obtaining text using HOOK methods, supports the use of special codes, supports automatic saving of games and HOOKs, automatic loading of HOOKs, etc. For some engines, it also supports embedded translation. For games that are not supported or not well supported, please [submit feedback](https://lunatranslator.org/Resource/game_support) 

- **OCR** Supports **offline OCR** (in addition to the built-in OCR engine, it also supports WindowsOCR, Tessearact5, manga-ocr, WeChat/QQ OCR) and **online OCR** (Baidu OCR/picture translation, Youdao OCR/picture translation, Youdao OCR/picture translation, Lark OCR, iFlytek OCR, Google Lens, Google Cloud Vision, docsumo, ocrspace). It can also use **multimodal large models** for OCR (supports GeminiOCR, ChatGPT compatible interfaces)

- **Clipboard** Supports obtaining text from the clipboard for translation

- **Text Output** Extracted text can be output to the clipboard, Websocket, for use by other programs.

#### Translator

Supports almost all conceivable translation engines, including:

- **Free Online Translation** Supports Baidu, Bing, Google, Alibaba, Youdao, Caiyun, Sogou, iFlytek, Tencent, ByteDance, Volcano, DeepL/DeepLX, papago, yandex, lingva, reverso, TranslateCom, ModernMT

- **Registered Online Translation** Supports user-registered **traditional translation** (Baidu, Tencent, Youdao, Xiaoniu, Caiyun, Volcano, DeepL, yandex, google, ibm, Azure, Lark) and **large model translation** (ChatGPT compatible interface, claude, cohere, gemini, Baidu Qianfan, Tencent Hunyuan)

- **Offline Translation** Supports **traditional translation** (J Beijing 7, Kingsoft, Yidiantong, ezTrans, Sugoi, MT5) and offline deployed **large model translation** (ChatGPT compatible interface, Sakura large model)

- **Chrome Debug Translation** Supports **traditional translation** (deepl, yandex, youdao, baidu, tencent, bing, caiyun, xiaoniu, alibaba, google) and **large model translation** (chatgpt, deepseek, moonshot, qianwen, chatglm, Theb.ai, DuckDuckGo)

- **Pre-translation** Supports reading pre-translated files, supports translation caching

- **Support for Custom Translation Extensions** Supports extending other translation interfaces using the Python language

#### Text-to-Speech

- **Offline TTS** Supports WindowsTTS, VoiceRoid2/VoiceRoid+, NeoSpeech, VOICEVOX, VITS

- **Online TTS** Supports Volcano TTS, Youdao TTS, Edge TTS, Google TTS

#### Translation Optimization

- **Text Processing** Supports more than ten common text processing methods, and complex text processing can be achieved through the adjustment of combinations and execution order

- **Translation Optimization** Supports the use of custom proper noun translation, supports the import of VNR shared dictionaries

#### Japanese Learning

- **Japanese Word Segmentation and Kana Display** Supports word segmentation and kana display using Mecab, etc.

- **Vocabulary Lookup** Supports **offline dictionaries** (MDICT, Shougakukan, Lingoes Dictionary, EDICT/EDICT2) and **online dictionaries** (Youdao, weblio, Goo, Moji, jisho) for word lookup

- **Anki** Supports one-click addition of words to Anki

## Support author
 
If you feel that the software is helpful to you, welcome to become my [sponsor](https://patreon.com/HIllya51). Thank you ~ 
