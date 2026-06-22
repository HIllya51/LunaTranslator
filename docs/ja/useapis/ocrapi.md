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

### ローカルOCR {#anchor-localocr}

内蔵済みの**PP-OCRv5_mobile**（中日英語の軽量認識モデル）が含まれています。他の言語を認識したい場合、または他のモデルを使用したい場合は、設定でモデルをダウンロードして使用するように設定する必要があります。

![img](https://image.lunatranslator.org/zh/localocr.png)

設定では、高精度モデル（例：PP-OCRv6_medium、PP-OCRv5_server）も提供されており、非常に高い認識精度を達成できますが、認識速度は比較的遅くなります。

| モデル | 検出モジュール Hmean(%) | 認識モジュール Avg Accuracy(%) | 対応言語 | サイズ(MB) |
| - | - | - | - | - |
| PP-OCRv6_small | 84.1 | 81.3 | 任意 | 25.2 |
| PP-OCRv6_medium | 86.2 | 83.2 | 任意 | 99.7 |
| PP-OCRv6_tiny | 80.6 | 73.5 | 任意 | 5.45 |
| PP-OCRv5_mobile | 79.0 | 81.29 | 簡体字中国語、繁体字中国語、英語、日本語 | 17.7 |
| PP-OCRv5_server | 83.8 | 86.38 | 簡体字中国語、繁体字中国語、英語、日本語 | 148 |
| eslav_PP-OCRv5_mobile | 79.0 | 81.6 | 東スラヴ語群 | 11.2 |
| korean_PP-OCRv5_mobile | 79.0 | 88.0 | 韓国語 | 12.2 |
| latin_PP-OCRv5_mobile | 79.0 | 84.7 | ラテン文字言語 | 11.3 |

高精度モデルの認識効率を向上させるためには、以下の方法を採用できます：

1. GPU推論の使用

   使用しているソフトウェアのバージョンがWin10版、またはシステムがWindows11の場合、直接GPUを使用してモデルを実行するよう設定できます。

    ![img](https://image.lunatranslator.org/zh/dml_gpu.png)

1. OpenVINO推論の使用

   IntelのCPU/NPU/GPUを使用している場合、推論エンジンをOpenVINOに置き換えて認識を高速化できます。
    
   [onnxruntime-openvino](https://globalcdn.nuget.org/packages/intel.ml.onnxruntime.openvino.1.23.0.nupkg)をダウンロードし、解凍後、**runtimes/win-x64/native**内のすべてのファイルを**LunaTranslator/files/DLL64**に上書きコピーし、使用するデバイスを選択します。

    ![img](https://image.lunatranslator.org/zh/ov_device.png)

### その他のOCR

::: tabs


== SnippingTool

>[!WARNING]
> Windows 10およびWindows 11オペレーティングシステムのみをサポートしています。

最新版のWindows 11システムであればそのまま使用できますが、それ以外の場合は設定からこのモジュールをインストールして使用する必要があります。
![img](https://image.lunatranslator.org/zh/snip.png)

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
