# OCR interface settings

## Online OCR {#anchor-online}

::: tabs

== Baidu

#### Baidu Intelligent Cloud OCR

https://ai.baidu.com/ai-doc/OCR/1k3h7y3db

#### Baidu Intelligent Cloud Image Translation

https://ai.baidu.com/ai-doc/MT/dkifdqg54

#### Baidu Translation Open Platform Image Translation

https://fanyi-api.baidu.com/product/22

== Tencent

#### General Printed Text Recognition

https://cloud.tencent.com/document/product/866/33526

#### Image Translation

https://cloud.tencent.com/document/product/551/17232

== Youdao

https://ai.youdao.com/doc.s#guide

== Volcano Engine

https://www.volcengine.com/docs/6790/116978

== Xunfei

https://www.xfyun.cn/doc/platform/quickguide.html

== Google Cloud Vision

https://cloud.google.com/vision/docs

== Ocr.space

https://ocr.space/

== General Large Model Interface

Same as [Translation](/en/guochandamoxing.html)

:::

## Offline OCR {#anchor-offline}

### Built-in OCR {#anchor-localocr}

The built-in **PP-OCRv5_mobile** (lightweight recognition model for Chinese, Japanese, and English) is already included. If you need to recognize other languages or want to use other models, you need to download the models in the settings and configure them for use.

![img](https://image.lunatranslator.org/zh/localocr.png)

The settings also provide some high-precision models, such as PP-OCRv6_medium and PP-OCRv5_server, which can achieve extremely high recognition accuracy, but the recognition speed is relatively slower.

| Model | Detection Module Hmean(%) | Recognition Module Avg Accuracy(%) | Supported Languages | Size(MB) |
| - | - | - | - | - |
| PP-OCRv6_small | 84.1 | 81.3 | Any | 25.2 |
| PP-OCRv6_medium | 86.2 | 83.2 | Any | 99.7 |
| PP-OCRv6_tiny | 80.6 | 73.5 | Any | 5.45 |
| PP-OCRv5_mobile | 79.0 | 81.29 | Simplified Chinese, Traditional Chinese, English, Japanese | 17.7 |
| PP-OCRv5_server | 83.8 | 86.38 | Simplified Chinese, Traditional Chinese, English, Japanese | 148 |
| eslav_PP-OCRv5_mobile | 79.0 | 81.6 | East Slavic languages | 11.2 |
| korean_PP-OCRv5_mobile | 79.0 | 88.0 | Korean | 12.2 |
| latin_PP-OCRv5_mobile | 79.0 | 84.7 | Latin-script languages | 11.3 |

To improve the recognition efficiency of high-precision models, the following methods can be adopted:

1. Use GPU Inference

    If the software version being used is the Win10 version, or the system is Windows 11, the model can be set to run directly using the GPU.

    ![img](https://image.lunatranslator.org/zh/dml_gpu.png)

1. Use OpenVINO Inference

    If using an Intel CPU/NPU/GPU, the inference engine can be replaced with OpenVINO to accelerate recognition.
    
    Download [onnxruntime-openvino](https://globalcdn.nuget.org/packages/intel.ml.onnxruntime.openvino.1.23.0.nupkg). After extracting, overwrite all files in **runtimes/win-x64/native** to **LunaTranslator/files/DLL64**, and then select the device to use.

    ![img](https://image.lunatranslator.org/zh/ov_device.png)

### Other OCR

::: tabs

== SnippingTool

>[!WARNING]
>Only supports Windows 10 and Windows 11 operating systems.

If you are using the latest version of Windows 11, you can use it directly; otherwise, you need to install this module in Settings to use it.
![img](https://image.lunatranslator.org/zh/snip.png)

== Manga-OCR

>[!WARNING]
>This OCR engine performs poorly in recognizing horizontal text.

CPU Integration Package https://lunatranslator.org/Resource/IntegrationPack/manga_ocr/cpu

GPU Integration Package https://lunatranslator.org/Resource/IntegrationPack/manga_ocr/gpu

== WeChat/QQ OCR

Requires installation of WeChat or the latest version of QQ


== WindowsOCR

>[!WARNING]
>Poor performance, not recommended for use.

>[!WARNING]
>Only supports Windows 10 and Windows 11 operating systems.

#### Query && Install && Remove OCR Language Packs  

https://learn.microsoft.com/en-us/windows/powertoys/text-extractor#supported-languages

== Tesseract5

>[!WARNING]
>Poor performance, not recommended for use.

https://github.com/tesseract-ocr/tesseract/releases

:::