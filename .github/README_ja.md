# LunaTranslator

> **ビジュアルノベル翻訳ツール**

### [简体中文](README.md) | [English](README_en.md) | [繁體中文](README_cht.md) | [한국어](README_ko.md) | 日本語 | [Tiếng Việt](README_vi.md)

### ソフトウェア使用中に問題が発生した場合、[ユーザーガイド](https://docs.lunatranslator.org)を参照するか、[Discord](https://discord.com/invite/ErtDwVeAbB)に参加してください。

## 機能サポート

#### テキスト入力

- **HOOK** HOOKメソッドを使用したテキスト取得をサポート。一部のエンジンでは[埋め込み翻訳](https://docs.lunatranslator.org/embedtranslate.html)にも対応。[エミュレータ](https://docs.lunatranslator.org/emugames.html)上で動作するゲームからのテキスト抽出も可能。未対応または不完全対応のゲームについては[フィードバックを提出](https://github.com/HIllya51/LunaTranslator/issues/new?assignees=&labels=enhancement&projects=&template=01_game_request.yaml)してください。

- **OCR** **[オフラインOCR](https://docs.lunatranslator.org/useapis/ocrapi.html)**と**[オンラインOCR](https://docs.lunatranslator.org/useapis/ocrapi.html)**をサポート

- **クリップボード** クリップボードから翻訳用テキストを取得可能。抽出したテキストをクリップボードに出力することも可能。

- **その他** **[音声認識](https://docs.lunatranslator.org/sr.html)**と**ファイル翻訳**にも対応

#### 翻訳機能

考え得るほぼ全ての翻訳エンジンをサポート：

- **オンライン翻訳** 登録不要で使用可能な多数のオンライン翻訳インターフェースをサポート。ユーザー登録APIを使用した**[従来型翻訳](https://docs.lunatranslator.org/useapis/tsapi.html)**と**[大規模モデル翻訳](https://docs.lunatranslator.org/guochandamoxing.html)**にも対応

- **オフライン翻訳** 一般的な**従来型翻訳**エンジンとオフライン展開可能な**[大規模モデル翻訳](https://docs.lunatranslator.org/offlinellm.html)**をサポート

- **事前翻訳** 事前翻訳ファイルの読み込みをサポート、翻訳キャッシュに対応

- **カスタム翻訳拡張サポート** Python言語を使用した他の翻訳インターフェースの拡張が可能

#### その他の機能

- **テキスト読み上げ** **オフラインTTS**と**オンラインTTS**をサポート

- **日本語分かち書きと仮名表示** Mecab等を使用した単語分割と仮名表示をサポート

- **単語検索** **オフライン辞書**(MDICT)と**オンライン辞書**による単語検索をサポート

- **Anki** ワンクリックでAnkiに単語を追加可能

- **ブラウザ拡張機能の読み込み** Yomitanなどのブラウザ拡張機能をソフトウェア内で読み込み、追加機能の実装を補助可能。

## スポンサーシップ

ソフトウェアのメンテナンスは容易ではありません。本ソフトウェアが役立つと感じた方は、[Patreon](https://patreon.com/HIllya51)を通じてサポートをお願いします。皆様の支援がソフトウェアの長期的な維持に貢献します。ありがとうございます～

<a href="https://patreon.com/HIllya51" target='_blank'><img width="200" src="../docs/become_a_patron_4x1_black_logo_white_text_on_coral.svg"></a>

## オープンソースライセンス

LunaTranslatorは[GPLv3](../LICENSE)ライセンスを使用しています。

<details>
<summary>参照プロジェクト</summary>

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
* ![img](https://img.shields.io/github/license/gexgd0419/NaturalVoiceSAPIAdapter) [gexgd0419/NaturalVoiceSAPIAdapter](https://github.com/gexgd0419/NaturalVoiceSAPIAdapter)
* ![img](https://img.shields.io/github/license/microsoft/PowerToys) [microsoft/PowerToys](https://github.com/microsoft/PowerToys)
</details>
