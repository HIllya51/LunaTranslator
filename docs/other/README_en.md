# LunaTranslator

<p align="left">
    <img src="https://img.shields.io/github/license/HIllya51/LunaTranslator">
    <a href="https://github.com/HIllya51/LunaTranslator/releases"><img src="https://img.shields.io/github/v/release/HIllya51/LunaTranslator?color=ffa"></a>
    <a href="https://github.com/HIllya51/LunaTranslator/releases/latest/download/LunaTranslator.zip" target="_blank"><img src="https://img.shields.io/badge/download_64bit-blue"/></a> <a href="https://github.com/HIllya51/LunaTranslator/releases/latest/download/LunaTranslator_x86.zip" target="_blank"><img src="https://img.shields.io/badge/download_32bit-blue"/></a>
</p>

### [User Manual](https://docs.lunatranslator.org/#/zh/)  <a href="https://discord.com/invite/ErtDwVeAbB"><img  src="https://img.shields.io/discord/1262692128031772733?label=Discord&logo=discord&color=FF007C"></a> 


### [简体中文](../../README.md) | English | [Other Language](otherlang.md) 


> **A galgame translation tool**

## Feature Support

#### Text Input

- **HOOK** Supports obtaining text using HOOK methods, supports the use of special codes, supports automatic saving of games and HOOKs, automatic loading of HOOKs, etc. For some engines, it also supports embedded translation. For games that are not supported or not well supported, please [submit feedback](https://github.com/HIllya51/LunaTranslator/issues/new?assignees=&labels=enhancement&projects=&template=01_game_request.yaml) 

- **OCR** supports **offline OCR** (in addition to the built-in OCR engine, it also supports WindowsOCR, Tesseract5, manga-ocr, WeChat/QQ OCR) and **online OCR** (Baidu, Youdao, iFlytek, Google Lens, Google Cloud Vision, docsumo, ocrspace, Gemini, ChatGPT-compatible interfaces).

- **Clipboard** Supports obtaining text from the clipboard for translation

- **Text Output** Extracted text can be output to the clipboard, Websocket, for use by other programs.

#### Translator

Supports almost all conceivable translation engines, including:

- **Free Online Translation** Supports Baidu, Bing, Google, Alibaba, Youdao, Caiyun, Sogou, iFlytek, Tencent, ByteDance, Volcano, DeepL/DeepLX, papago, yandex, lingva, reverso, TranslateCom, ModernMT

- **Registered Online Translation** Supports user-registered **traditional translation** (Baidu, Tencent, Youdao, Xiaoniu, Caiyun, Volcano, DeepL, yandex, google, ibm, Azure) and **large model translation** (ChatGPT compatible interface, claude, cohere, gemini, Baidu Qianfan, Tencent Hunyuan)

- **Offline Translation** Supports **traditional translation** (J Beijing 7, Kingsoft, Yidiantong, ezTrans, Sugoi, MT5) and offline deployed **large model translation** (ChatGPT compatible interface, Sakura large model)

- **Pre-translation** Supports reading pre-translated files, supports translation caching

- **Support for Custom Translation Extensions** Supports extending other translation interfaces using the Python language

#### Text-to-Speech

- **Offline TTS** Supports WindowsTTS, VoiceRoid2/VoiceRoid+, NeoSpeech, VOICEVOX, VITS

- **Online TTS** Supports Volcano TTS, Youdao TTS, Edge TTS, Google TTS

#### Japanese Learning

- **Japanese Word Segmentation and Kana Display** Supports word segmentation and kana display using Mecab, etc.

- **Vocabulary Lookup** Supports **offline dictionaries** (MDICT, Shougakukan, Lingoes Dictionary, EDICT/EDICT2) and **online dictionaries** (Youdao, weblio, Goo, Moji, jisho, JapanDict) for word lookup

- **Anki** Supports one-click addition of words to Anki

## Support author
 
If you feel that the software is helpful to you, welcome to become my [sponsor](https://patreon.com/HIllya51). Thank you ~ 
