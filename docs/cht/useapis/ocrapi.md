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

== 有道詞典

https://www.patreon.com/posts/high-precision-133319068

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

== 本機 OCR

內建已包含中日英文的輕量級辨識模型。如果需要辨識其他語言，需要在`資源下載`中新增對應語言的辨識模型。


`資源下載`中還提供了中日英語的高精度模型，可以達到極高的識別準確率，但識別速度相對較慢。

為提高高精度模型的識別效率，可以採用以下手段：

1. 使用GPU推理

    如果使用的軟件版本為Win10版，或系統為Windows11，那麼可以直接設定使用GPU運行模型。

    ![img](https://image.lunatranslator.org/zh/dml_gpu.png)

1. 使用OpenVINO推理

    如果使用Intel的CPU/NPU/GPU，那麼可以替換推理引擎為OpenVINO來加速識別。
    
    下載[onnxruntime-openvino](https://globalcdn.nuget.org/packages/intel.ml.onnxruntime.openvino.1.23.0.nupkg)，解壓後將**runtimes/win-x64/native**中的所有檔案覆蓋到**LunaTranslator/files/DLL64**中，然後選擇使用的裝置即可。

    ![img](https://image.lunatranslator.org/zh/ov_device.png)

== Snipping Tool

>[!WARNING]
僅支援 Win10～Win11 作業系統

如果是最新版 Windows 11 系統則可以直接使用，否則需要在`資源下載`中安裝該模組以使用。

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
