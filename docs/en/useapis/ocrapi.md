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

== Youdao Dictionary

https://www.patreon.com/posts/high-precision-133319068

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

::: tabs

== Local OCR

The built-in system includes lightweight recognition models for Chinese, Japanese, and English. If you need to recognize other languages, you can download the corresponding language models from the `Resource Download` section.


`Resource Downloads` also provide high-precision models for Chinese, Japanese, and English, which can achieve extremely high recognition accuracy, but the recognition speed is relatively slow.

To improve the recognition efficiency of high-precision models, the following methods can be adopted:

1. Use GPU Inference

    If the software version being used is the Win10 version, or the system is Windows 11, the model can be set to run directly using the GPU.

    ![img](https://image.lunatranslator.org/zh/dml_gpu.png)

1. Use OpenVINO Inference

    If using an Intel CPU/NPU/GPU, the inference engine can be replaced with OpenVINO to accelerate recognition.
    
    Download [onnxruntime-openvino](https://globalcdn.nuget.org/packages/intel.ml.onnxruntime.openvino.1.23.0.nupkg). After extracting, overwrite all files in **runtimes/win-x64/native** to **LunaTranslator/files/DLL64**, and then select the device to use.

    ![img](https://image.lunatranslator.org/zh/ov_device.png)

== SnippingTool

>[!WARNING]
>Only supports Windows 10 and Windows 11 operating systems.

If you are using the latest version of Windows 11, you can use it directly. 

Otherwise, you need to install this module from `Resource Download` to enable its functionality.

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