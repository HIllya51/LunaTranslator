# OCRインターフェース設定

## オンラインOCR {#anchor-online}

::: tabs

== 百度

#### 百度智能云 OCR

https://ai.baidu.com/ai-doc/OCR/1k3h7y3db

#### 百度智能云 画像翻訳

https://ai.baidu.com/ai-doc/MT/dkifdqg54

#### 百度翻訳オープンプラットフォーム 画像翻訳

https://fanyi-api.baidu.com/product/22

== 腾讯

#### OCR 一般印刷体認識

https://cloud.tencent.com/document/product/866/33526

#### 画像翻訳

https://cloud.tencent.com/document/product/551/17232

== 有道辞書

https://www.patreon.com/posts/high-precision-133319068

== 有道

https://ai.youdao.com/doc.s#guide

== 火山

https://www.volcengine.com/docs/6790/116978

== 讯飞

https://www.xfyun.cn/doc/platform/quickguide.html

== Google Cloud Vision

https://cloud.google.com/vision/docs

== ocrspace

https://ocr.space/

== 大規模モデルの汎用インターフェース

[翻訳](/ja/guochandamoxing.html)と同じ

:::


## オフラインOCR {#anchor-offline}


::: tabs

== ローカルOCR

組み込みでは、中国語・日本語・英語の軽量認識モデルが含まれています。他の言語を認識する必要がある場合は、`リソースダウンロード`で対応する言語モデルを追加してください。

さらに、`リソースダウンロード`では、中国語・日本語・英語の高精度モデルも提供されています。Windows 10版のソフトウェアを使用している場合、またはシステムがWindows 11の場合、GPUを使用してモデルを実行するように設定することで、高精度モデルの認識効率を向上させることができます。

== SnippingTool

>[!WARNING]
> Windows 10およびWindows 11オペレーティングシステムのみをサポートしています。

最新版のWindows 11システムであれば直接使用できます。

それ以外の場合は、`リソースダウンロードで`このモジュールをインストールする必要があります。

== manga-ocr

>[!WARNING]
>このOCRエンジンは横書きテキストの認識に不向きです。

CPU統合パッケージ https://lunatranslator.org/Resource/IntegrationPack/manga_ocr/cpu

GPU統合パッケージ https://lunatranslator.org/Resource/IntegrationPack/manga_ocr/gpu

== WeChat/QQ OCR

WeChatまたは最新バージョンのQQのインストールが必要です

== WindowsOCR

>[!WARNING]
>性能が低すぎるため、使用は推奨されません。

>[!WARNING]
> Windows 10およびWindows 11オペレーティングシステムのみをサポートしています。

#### クエリ && インストール && OCR言語パックの削除  

https://learn.microsoft.com/ja-jp/windows/powertoys/text-extractor#supported-languages

== Tesseract5

>[!WARNING]
>性能が低すぎるため、使用は推奨されません。

https://github.com/tesseract-ocr/tesseract/releases

:::
