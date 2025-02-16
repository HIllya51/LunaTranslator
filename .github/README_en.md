# LunaTranslator

### [简体中文](README.md) | English | [Other Language](otherlang.md) 

### [User Manual](https://docs.lunatranslator.org/) | [Software Download](https://docs.lunatranslator.org/README.html) | [![](https://img.shields.io/discord/1262692128031772733?label=Discord&logo=discord&color=FF007C&style=for-the-badge)](https://discord.com/invite/ErtDwVeAbB)


> **A galgame translation tool**

## Feature Support

#### Text Input

- **HOOK** Supports obtaining text using HOOK methods, supports the use of special codes, supports automatic saving of games and HOOKs, automatic loading of HOOKs, etc. For some engines, it also supports embedded translation. For games that are not supported or not well supported, please [submit feedback](https://github.com/HIllya51/LunaTranslator/issues/new?assignees=&labels=enhancement&projects=&template=01_game_request.yaml) 

- **OCR** supports **offline OCR** (in addition to the built-in OCR engine, it also supports WindowsOCR, Tesseract5, manga-ocr, WeChat/QQ OCR) and **online OCR**

- **Clipboard** Supports obtaining text from the clipboard for translation

- **Text Output** Extracted text can be output to the clipboard, Websocket, for use by other programs.

#### Translator

Supports almost all conceivable translation engines, including:

- **Free Online Translation** Supports a large number of online translation interfaces that can be used without registration

- **Registered Online Translation** Supports user-registered **traditional translation** and **large model translation**

- **Offline Translation** Supports **traditional translation** (J Beijing 7, Kingsoft, Yidiantong, ezTrans, Sugoi, Atlas, LEC) and offline deployed **large model translation**

- **Pre-translation** Supports reading pre-translated files, supports translation caching

- **Support for Custom Translation Extensions** Supports extending other translation interfaces using the Python language

#### Text-to-Speech

- **Offline TTS** Supports WindowsTTS, VoiceRoid2/VoiceRoid+, NeoSpeech, VOICEVOX, VITS

- **Online TTS** Supports Volcano TTS, Youdao TTS, Edge TTS, Google TTS, OpenAI

#### Japanese Learning

- **Japanese Word Segmentation and Kana Display** Supports word segmentation and kana display using Mecab, etc.

- **Vocabulary Lookup** Supports **offline dictionaries** (MDICT) and **online dictionaries** for word lookup

- **Anki** Supports one-click addition of words to Anki

- **Browser Extensions like Yomitan** Browser extensions like Yomitan can be loaded within the software to assist in implementing additional features.

## Sponsorship
 
If you feel that the software is helpful to you, welcome to become my [sponsor](https://patreon.com/HIllya51). Thank you ~ 
