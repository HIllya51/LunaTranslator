# Настройки OCR-интерфейса

## Онлайн OCR {#anchor-online}

::: tabs

== Baidu

#### Baidu Intelligent Cloud OCR

https://ai.baidu.com/ai-doc/OCR/1k3h7y3db

#### Baidu Intelligent Cloud Перевод изображений

https://ai.baidu.com/ai-doc/MT/dkifdqg54

#### Baidu Translate Open Platform Перевод изображений

https://fanyi-api.baidu.com/product/22

== Tencent

#### OCR Общее распознавание печатного текста

https://cloud.tencent.com/document/product/866/33526

#### Перевод изображений

https://cloud.tencent.com/document/product/551/17232

== Youdao

https://ai.youdao.com/doc.s#guide

== Volcano

https://www.volcengine.com/docs/6790/116978

== iFlytek

https://www.xfyun.cn/doc/platform/quickguide.html


== Google Cloud Vision

https://cloud.google.com/vision/docs

== ocrspace

https://ocr.space/

== Универсальный интерфейс для больших моделей

То же, что и [перевод](/zh/guochandamoxing.html)

:::


## Оффлайн OCR {#anchor-offline}


::: tabs

== Встроенный OCR

Встроенная модель **PP-OCRv5_mobile** (лёгкая модель распознавания для китайского, японского и английского языков) уже включена. Если вам нужно распознавать другие языки или вы хотите использовать другие модели, необходимо загрузить модели в настройках и настроить их использование.

![img](https://image.lunatranslator.org/zh/localocr.png)

В настройках также доступны некоторые высокоточные модели, например (PP-OCRv6_medium, PP-OCRv5_server), которые позволяют достичь чрезвычайно высокой точности распознавания, но скорость распознавания при этом относительно ниже.

Для повышения эффективности распознавания высокоточных моделей можно использовать следующие методы:

1. Использование GPU для вывода

    Если используется версия программного обеспечения для Win10 или система Windows 11, можно напрямую настроить использование GPU для запуска модели.

    ![img](https://image.lunatranslator.org/zh/dml_gpu.png)

1. Использование OpenVINO для вывода

    Если используется процессор Intel (CPU/NPU/GPU), механизм вывода можно заменить на OpenVINO для ускорения распознавания.
    
    Скачайте [onnxruntime-openvino](https://globalcdn.nuget.org/packages/intel.ml.onnxruntime.openvino.1.23.0.nupkg). После распаковки скопируйте все файлы из папки **runtimes/win-x64/native** в папку **LunaTranslator/files/DLL64**, затем выберите используемое устройство.

    ![img](https://image.lunatranslator.org/zh/ov_device.png)

== SnippingTool

>[!WARNING]
Поддерживается только ОС Win10-Win11

Если у вас установлена последняя версия Windows 11, вы можете использовать его напрямую; в противном случае вам необходимо установить этот модуль в настройках, чтобы использовать его.
![img](https://image.lunatranslator.org/zh/snip.png)

== manga-ocr

>[!WARNING]
> Этот OCR-движок плохо справляется с распознаванием горизонтального текста.

CPU сборка https://lunatranslator.org/Resource/IntegrationPack/manga_ocr/cpu

GPU сборка https://lunatranslator.org/Resource/IntegrationPack/manga_ocr/gpu

#### Что делать, если сборка mangaocr для Китая не запускается？

При первом запуске start.bat будет попытка загрузить модель с huggingface, но в Китае… вы понимаете.

![img](https://image.lunatranslator.org/zh/mangaocr/err1.png)

![img](https://image.lunatranslator.org/zh/mangaocr/err2.png)

Есть два решения:

1. Использовать VPN, возможно, потребуется включить TUN-прокси

1. Использовать VSCode, "Открыть папку" для открытия папки со сборкой.


![img](https://image.lunatranslator.org/zh/mangaocr/fix2.png)

Затем используйте функцию поиска и замените все вхождения «huggingface.co» на «hf-mirror.com». Поскольку замен будет много, потребуется немного подождать.

![img](https://image.lunatranslator.org/zh/mangaocr/fix.png)

Затем снова запустите start.bat, после чего модели будут загружаться с китайского зеркального сайта, без необходимости использования VPN.


![img](https://image.lunatranslator.org/zh/mangaocr/succ.png)


Подождите некоторое время при первом запуске для загрузки моделей и при каждом запуске для их загрузки. Сообщение «`* Running on http://127.0.0.1:5665`» означает, что сервис успешно запущен.

== WeChat/QQ OCR

Необходимо установить WeChat или новую версию QQ

== WindowsOCR

>[!WARNING]
>Эффективность слишком низкая, использование не рекомендуется.

>[!WARNING]
Поддерживаются только операционные системы Win10-Win11

#### Поиск && Установка && Удаление OCR языковых пакетов

https://learn.microsoft.com/zh-cn/windows/powertoys/text-extractor#supported-languages

== Tesseract5

>[!WARNING]
>Эффективность слишком низкая, использование не рекомендуется.

https://github.com/tesseract-ocr/tesseract/releases

:::
