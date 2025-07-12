### [简体中文](README.md) | [English](README_en.md) | [繁體中文](README_cht.md) | [한국어](README_ko.md) | 日本語 | [Tiếng Việt](README_vi.md) | [Русский язык](README_ru.md)

# LunaTranslator [ソフトウェアのダウンロード](https://docs.lunatranslator.org/ja/README.html)  

> **ビジュアルノベル翻訳ツール**

### ソフトウェア使用中に問題が発生した場合、[ユーザーガイド](https://docs.lunatranslator.org/ja)を参照するか、[Discord](https://discord.com/invite/ErtDwVeAbB)に参加してください。

## 機能サポート

#### テキスト入力

- **HOOK** HOOKメソッドを使用したテキスト取得をサポート。一部のエンジンでは[埋め込み翻訳](https://docs.lunatranslator.org/ja/embedtranslate.html)にも対応。[エミュレータ](https://docs.lunatranslator.org/ja/emugames.html)上で動作するゲームからのテキスト抽出も可能。未対応または不完全対応のゲームについては[フィードバックを提出](https://github.com/HIllya51/LunaTranslator/issues/new?assignees=&labels=enhancement&projects=&template=01_game_request.yaml)してください。

- **OCR** **[オフラインOCR](https://docs.lunatranslator.org/ja/useapis/ocrapi.html)**と**[オンラインOCR](https://docs.lunatranslator.org/ja/useapis/ocrapi.html)**をサポート

- **クリップボード** クリップボードから翻訳用テキストを取得可能。抽出したテキストをクリップボードに出力することも可能。

- **その他** **[音声認識](https://docs.lunatranslator.org/ja/sr.html)**と**ファイル翻訳**にも対応

#### 翻訳機能

考え得るほぼ全ての翻訳エンジンをサポート：

- **オンライン翻訳** 登録不要で使用可能な多数のオンライン翻訳インターフェースをサポート。ユーザー登録APIを使用した**[従来型翻訳](https://docs.lunatranslator.org/ja/useapis/tsapi.html)**と**[大規模モデル翻訳](https://docs.lunatranslator.org/ja/guochandamoxing.html)**にも対応

- **オフライン翻訳** 一般的な**従来型翻訳**エンジンとオフライン展開可能な**[大規模モデル翻訳](https://docs.lunatranslator.org/ja/offlinellm.html)**をサポート

- **事前翻訳** 事前翻訳ファイルの読み込みをサポート、翻訳キャッシュに対応

- **カスタム翻訳拡張サポート** Python言語を使用した他の翻訳インターフェースの拡張が可能

#### その他の機能

- **テキスト読み上げ** **オフラインTTS**と**オンラインTTS**をサポート

- **日本語の分かち書きと仮名振り** Mecab等を使用した単語分割と仮名表示をサポート

- **単語検索** **オフライン辞書**(MDICT)と**オンライン辞書**による単語検索をサポート

- **Anki** ワンクリックでAnkiに単語を追加可能

- **ブラウザ拡張機能の読み込み** Yomitanなどのブラウザ拡張機能をソフトウェア内で読み込み、追加機能の実装を補助可能。

## スポンサーシップ

ソフトウェアのメンテナンスは容易ではありません。本ソフトウェアが役立つと感じた方は、[Patreon](https://patreon.com/HIllya51)を通じてサポートをお願いします。皆様の支援がソフトウェアの長期的な維持に貢献します。ありがとうございます～

<a href="https://patreon.com/HIllya51" target='_blank'><img width="200" src="../docs/become_a_patron_4x1_black_logo_white_text_on_coral.svg"></a>

## オープンソースライセンス

LunaTranslatorは[GPLv3](../LICENSE)ライセンスを使用しています。
