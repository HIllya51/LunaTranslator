# LunaTranslator

> **A Visual Novel translation tool**

### [简体中文](README.md) | English | [Other Language](otherlang.md) 

### [User Manual](https://docs.lunatranslator.org/) | [Software Download](https://docs.lunatranslator.org/README.html) | [![](https://img.shields.io/discord/1262692128031772733?label=Discord&logo=discord&color=FF007C&style=for-the-badge)](https://discord.com/invite/ErtDwVeAbB)

## Sponsorship
 
Software maintenance is not easy. If you find this software helpful, please consider becoming my [sponsor](https://patreon.com/HIllya51). Thank you~

## Feature Support

#### Text Input

- **HOOK** Supports obtaining text using HOOK methods. For some engines, it also supports [embedded translation](https://docs.lunatranslator.org/embedtranslate.html). And Extracting text from games running on some [Emulators](https://docs.lunatranslator.org/emugames.html) is also supported. For games that are not supported or not well supported, please [submit feedback](https://github.com/HIllya51/LunaTranslator/issues/new?assignees=&labels=enhancement&projects=&template=01_game_request.yaml) 

- **OCR** supports **[offline OCR](https://docs.lunatranslator.org/useapis/ocrapi.html)** and **[online OCR](https://docs.lunatranslator.org/useapis/ocrapi.html)**

- **Clipboard** Supports retrieving text from the clipboard for translation and can also output extracted text to the clipboard.

#### Translator

Supports almost all conceivable translation engines, including:

- **Online Translation** Supports many online translation interfaces that can be used without registration, and also supports **[traditional translation](https://docs.lunatranslator.org/useapis/tsapi.html)** and **[large model translation](https://docs.lunatranslator.org/guochandamoxing.html)** using user-registered APIs

- **Offline translation** Supports common **traditional translation** engines and **[large model translation](https://docs.lunatranslator.org/offlinellm.html)** for offline deployment

- **Pre-translation** Supports reading pre-translated files, supports translation caching

- **Support for Custom Translation Extensions** Supports extending other translation interfaces using the Python language

#### Other Functions

- **Text-to-Speech** supports **Offline TTS** and **Online TTS**

- **Japanese Word Segmentation and Kana Display** Supports word segmentation and kana display using Mecab, etc.

- **Vocabulary Lookup** Supports **offline dictionaries** (MDICT) and **online dictionaries** for word lookup

- **Anki** Supports one-click addition of words to Anki

- **Load Browser Extensions** Browser extensions like Yomitan can be loaded within the software to assist in implementing additional features.

## Open Source License

LunaTranslator uses [GPLv3](../LICENSE) license.

<details>
<summary>Referenced Projects</summary>

* ![img](https://img.shields.io/github/license/opencv/opencv) [opencv/opencv](https://github.com/opencv/opencv)
* ![img](https://img.shields.io/github/license/microsoft/onnxruntime) [microsoft/onnxruntime](https://github.com/microsoft/onnxruntime)
* ![img](https://img.shields.io/github/license/Artikash/Textractor) [Artikash/Textractor](https://github.com/Artikash/Textractor)
* ![img](https://img.shields.io/github/license/RapidAI/RapidOcrOnnx) [RapidAI/RapidOcrOnnx](https://github.com/RapidAI/RapidOcrOnnx)
* ![img](https://img.shields.io/github/license/PaddlePaddle/PaddleOCR) [PaddlePaddle/PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)
* ![img](https://img.shields.io/github/license/Blinue/Magpie) [Blinue/Magpie](https://github.com/Blinue/Magpie)
* ![img](https://img.shields.io/github/license/nanokina/ebyroid) [nanokina/ebyroid](https://github.com/nanokina/ebyroid)
* ![img](https://img.shields.io/github/license/xupefei/Locale-Emulator) [xupefei/Locale-Emulator](https://github.com/xupefei/Locale-Emulator)
* ![img](https://img.shields.io/github/license/InWILL/Locale_Remulator) [InWILL/Locale_Remulator](https://github.com/InWILL/Locale_Remulator)
* ![img](https://img.shields.io/github/license/zxyacb/ntlea) [zxyacb/ntlea](https://github.com/zxyacb/ntlea)
* ![img](https://img.shields.io/github/license/Chuyu-Team/YY-Thunks) [Chuyu-Team/YY-Thunks](https://github.com/Chuyu-Team/YY-Thunks)
* ![img](https://img.shields.io/github/license/Chuyu-Team/VC-LTL5) [Chuyu-Team/VC-LTL5](https://github.com/Chuyu-Team/VC-LTL5)
* ![img](https://img.shields.io/github/license/uyjulian/AtlasTranslate) [uyjulian/AtlasTranslate](https://github.com/uyjulian/AtlasTranslate)
* ![img](https://img.shields.io/github/license/ilius/pyglossary) [ilius/pyglossary](https://github.com/ilius/pyglossary)
* ![img](https://img.shields.io/github/license/ikegami-yukino/mecab) [ikegami-yukino/mecab](https://github.com/ikegami-yukino/mecab)
* ![img](https://img.shields.io/github/license/AngusJohnson/Clipper2) [AngusJohnson/Clipper2](https://github.com/AngusJohnson/Clipper2)
* ![img](https://img.shields.io/github/license/rapidfuzz/rapidfuzz-cpp) [rapidfuzz/rapidfuzz-cpp](https://github.com/rapidfuzz/rapidfuzz-cpp)
* ![img](https://img.shields.io/github/license/TsudaKageyu/minhook) [TsudaKageyu/minhook](https://github.com/TsudaKageyu/minhook)
* ![img](https://img.shields.io/github/license/lobehub/lobe-icons) [lobehub/lobe-icons](https://github.com/lobehub/lobe-icons)
* ![img](https://img.shields.io/github/license/kokke/tiny-AES-c) [kokke/tiny-AES-c](https://github.com/kokke/tiny-AES-c)
* ![img](https://img.shields.io/github/license/TPN-Team/OCR) [TPN-Team/OCR](https://github.com/TPN-Team/OCR)
* ![img](https://img.shields.io/github/license/AuroraWright/owocr) [AuroraWright/owocr](https://github.com/AuroraWright/owocr)
* ![img](https://img.shields.io/github/license/b1tg/win11-oneocr) [b1tg/win11-oneocr](https://github.com/b1tg/win11-oneocr)
* ![img](https://img.shields.io/github/license/mity/md4c) [mity/md4c](https://github.com/mity/md4c)
* ![img](https://img.shields.io/github/license/swigger/wechat-ocr) [swigger/wechat-ocr](https://github.com/swigger/wechat-ocr)
* ![img](https://img.shields.io/github/license/rupeshk/MarkdownHighlighter) [rupeshk/MarkdownHighlighter](https://github.com/rupeshk/MarkdownHighlighter)
* ![img](https://img.shields.io/github/license/sindresorhus/github-markdown-css) [sindresorhus/github-markdown-css](https://github.com/sindresorhus/github-markdown-css)
</details>
