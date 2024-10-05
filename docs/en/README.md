
> **A galgame translation tool**

## Feature Support

#### Text Input

- **HOOK** Supports obtaining text using [HOOK](https://github.com/HIllya51/LunaHook) methods, supports the use of special codes, supports automatic saving of games and HOOKs, automatic loading of HOOKs, etc. For some engines, it also supports embedded translation. For games that are not supported or not well supported, please [submit feedback](https://lunatranslator.org/Resource/game_support) 

- **OCR** supports **offline OCR** (in addition to the [built-in OCR engine](https://github.com/HIllya51/LunaOCR), it also supports WindowsOCR, Tesseract5, manga-ocr, WeChat/QQ OCR) and **online OCR** (Baidu, Youdao, Feishu, iFlytek, Google Lens, Google Cloud Vision, docsumo, ocrspace, Gemini, ChatGPT-compatible interfaces).

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

#### Japanese Learning

- **Japanese Word Segmentation and Kana Display** Supports word segmentation and kana display using Mecab, etc.

- **Vocabulary Lookup** Supports **offline dictionaries** (MDICT, Shougakukan, Lingoes Dictionary, EDICT/EDICT2) and **online dictionaries** (Youdao, weblio, Goo, Moji, jisho) for word lookup

- **Anki** Supports one-click addition of words to Anki
