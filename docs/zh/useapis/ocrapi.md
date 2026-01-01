# OCR接口设置

## 在线OCR {#anchor-online}

::: tabs

== 百度

#### 百度智能云 OCR

https://ai.baidu.com/ai-doc/OCR/1k3h7y3db

#### 百度智能云 图片翻译

https://ai.baidu.com/ai-doc/MT/dkifdqg54

#### 百度翻译开放平台 图片翻译

https://fanyi-api.baidu.com/product/22

== 腾讯

#### OCR 通用印刷体识别

https://cloud.tencent.com/document/product/866/33526

#### 图片翻译

https://cloud.tencent.com/document/product/551/17232

== 有道词典

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

== 大模型通用接口

和[翻译](/zh/guochandamoxing.html)相同

:::


## 离线OCR {#anchor-offline}


::: tabs

== 本地OCR

内置已包含中日英语的轻量级识别模型。如果需要识别其他语言，需要在`资源下载`中添加对应语言的识别模型。

`资源下载`中还提供了中日英语的高精度模型，可以达到极高的识别准确率，但识别速度相对较慢。

为提高高精度模型的识别效率，可以采用以下手段：

1. 使用GPU推理

    如果使用的软件版本为Win10版，或系统为Windows11，那么可以直接设置使用GPU运行模型。

    ![img](https://image.lunatranslator.org/zh/dml_gpu.png)

1. 使用OpenVINO推理

    如果使用Intel的CPU/NPU/GPU，那么可以替换推理引擎为OpenVINO来加速识别。
    
    下载[onnxruntime-openvino](https://globalcdn.nuget.org/packages/intel.ml.onnxruntime.openvino.1.23.0.nupkg)，解压后将**runtimes/win-x64/native**中的所有文件覆盖到**LunaTranslator/files/DLL64**中，然后选择使用的设备即可。

    ![img](https://image.lunatranslator.org/zh/ov_device.png)

== SnippingTool

>[!WARNING]
仅支持win10-win11操作系统

如果是最新版windows 11系统则可以直接使用，否则需要在`资源下载`中安装该模块以使用。

== manga-ocr

>[!WARNING]
>此OCR引擎对于横向文本识别不效果不佳。

CPU整合包 https://lunatranslator.org/Resource/IntegrationPack/manga_ocr/cpu

GPU整合包 https://lunatranslator.org/Resource/IntegrationPack/manga_ocr/gpu

#### 国内mangaocr整合包无法启动怎么办？

首次启动start.bat时，会尝试从huggingface上下载模型，但是国内你懂的。

![img](https://image.lunatranslator.org/zh/mangaocr/err1.png)

![img](https://image.lunatranslator.org/zh/mangaocr/err2.png)

解决方法有两种

1. 魔法上网，可能要开TUN代理

1. 使用vscode，“打开文件夹”打开整合包的文件夹。


![img](https://image.lunatranslator.org/zh/mangaocr/fix2.png)

然后使用搜索功能，将“huggingface.co”全部替换成“hf-mirror.com”。由于替换项较多，需要稍微等待一会儿。

![img](https://image.lunatranslator.org/zh/mangaocr/fix.png)

然后重新运行start.bat，之后会用国内镜像站下载模型，无须魔法上网。


![img](https://image.lunatranslator.org/zh/mangaocr/succ.png)


等待一会儿首次运行的下载模型和每次运行都需要的加载模型。显示“`* Running on http://127.0.0.1:5665`”表示服务已正常启动。

== WeChat/QQ OCR

需要安装微信或新版QQ

== WindowsOCR

>[!WARNING]
>效果太差，不推荐使用。

>[!WARNING]
仅支持win10-win11操作系统

#### 查询 && 安装 && 移除 OCR 语言包

https://learn.microsoft.com/zh-cn/windows/powertoys/text-extractor#supported-languages

== Tesseract5

>[!WARNING]
>效果太差，不推荐使用。

https://github.com/tesseract-ocr/tesseract/releases

:::
