# OCR 介面設定

## 線上 OCR {#anchor-online}

::: tabs

== 百度

#### 百度智能雲 OCR

https://ai.baidu.com/ai-doc/OCR/1k3h7y3db

#### 百度智能雲 圖片翻譯

https://ai.baidu.com/ai-doc/MT/dkifdqg54

#### 百度翻譯開放平台 圖片翻譯

https://fanyi-api.baidu.com/product/22

== 騰訊

#### OCR 通用印刷體識別

https://cloud.tencent.com/document/product/866/33526

#### 圖片翻譯

https://cloud.tencent.com/document/product/551/17232

== 有道

https://ai.youdao.com/doc.s#guide

== 火山

https://www.volcengine.com/docs/6790/116978

== 訊飛

https://www.xfyun.cn/doc/platform/quickguide.html


== Google Cloud Vision

https://cloud.google.com/vision/docs

== OCRSpace

https://ocr.space/

== 大模型通用介面

和[翻譯](/zh/guochandamoxing.html)相同

:::


## 離線 OCR {#anchor-offline}


::: tabs

== 內建 OCR

內建已包含**PP-OCRv5_mobile**（中日英語的輕量級辨識模型）。如果需要辨識其他語言，或想要使用其他模型，需要在設定中下載模型並設定使用。

![img](https://image.lunatranslator.org/zh/localocr.png)

設定中還提供了一些高精度模型，例如（PP-OCRv6_medium、PP-OCRv5_server），可以達到極高的辨識準確率，但辨識速度相對較慢。

為提高高精度模型的辨識效率，可以採用以下手段：

1. 使用 GPU 推理

    如果使用的軟體版本為 Win10 版，或系統為 Windows 11，那麼可以直接設定使用 GPU 執行模型。

    ![img](https://image.lunatranslator.org/zh/dml_gpu.png)

1. 使用 OpenVINO 推理

    如果使用 Intel 的 CPU/NPU/GPU，那麼可以將推理引擎替換為 OpenVINO 來加速辨識。
    
    下載 [onnxruntime-openvino](https://globalcdn.nuget.org/packages/intel.ml.onnxruntime.openvino.1.23.0.nupkg)，解壓縮後將 **runtimes/win-x64/native** 中的所有檔案覆蓋到 **LunaTranslator/files/DLL64** 中，然後選擇使用的裝置即可。

    ![img](https://image.lunatranslator.org/zh/ov_device.png)

== SnippingTool

>[!WARNING]
僅支援 Win10～Win11 作業系統

如果是最新版的 Windows 11 系統則可以直接使用，否則需要在設定中安裝該模組以使用。
![img](https://image.lunatranslator.org/zh/snip.png)

== Manga OCR

>[!WARNING]
>此 OCR 引擎對於橫向文字辨識效果不佳。

CPU 整合包 https://lunatranslator.org/Resource/IntegrationPack/manga_ocr/cpu

GPU 整合包 https://lunatranslator.org/Resource/IntegrationPack/manga_ocr/gpu

== WeChat/QQ OCR

需要安裝微信或新版 QQ

== WindowsOCR

>[!WARNING]
>效果太差，不推薦使用。

>[!WARNING]
僅支援 Win10～Win11 作業系統

#### 查詢＆＆安裝＆＆移除 OCR 語言包

https://learn.microsoft.com/zh-cn/windows/powertoys/text-extractor#supported-languages

== Tesseract 5

>[!WARNING]
>效果太差，不推薦使用。

https://github.com/tesseract-ocr/tesseract/releases

:::
