# OCR接口設置

## 在線OCR {#anchor-online}

::: tabs

== 百度

#### 百度智能雲 OCR

https://ai.baidu.com/ai-doc/OCR/1k3h7y3db

#### 百度智能雲 圖片翻譯

https://ai.baidu.com/ai-doc/MT/dkifdqg54

#### 百度翻譯開放平臺 圖片翻譯

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

== ocrspace

https://ocr.space/

== 大模型通用接口

和[翻譯](/zh/guochandamoxing.html)相同

:::


## 離線OCR {#anchor-offline}


::: tabs

== 本地OCR

內置已包含中日英語的輕量級識別模型。如果需要識別其他語言，需要在`資源下載`中添加對應語言的識別模型。

`資源下載`中還提供了中日英語的高精度模型。如果使用的軟件版本爲Win10版，或系統爲Windows11，還可以設置使用GPU運行模型，來提高高精度模型的識別效率。

== SnippingTool

>[!WARNING]
僅支持win10-win11操作系統

如果是最新版windows 11系統則可以直接使用，否則需要在`資源下載`中安裝該模塊以使用。

== manga-ocr

>[!WARNING]
>此OCR引擎對於橫向文本識別不效果不佳。

CPU整合包 https://lunatranslator.org/Resource/IntegrationPack/manga_ocr/cpu

GPU整合包 https://lunatranslator.org/Resource/IntegrationPack/manga_ocr/gpu

== WeChat/QQ OCR

需要安裝微信或新版QQ

== WindowsOCR

>[!WARNING]
僅支持win10-win11操作系統

#### 查詢 && 安裝 && 移除 OCR 語言包

https://learn.microsoft.com/zh-cn/windows/powertoys/text-extractor#supported-languages

== Tesseract5

>[!WARNING]
>效果太差，不推薦使用。

https://github.com/tesseract-ocr/tesseract/releases

:::
