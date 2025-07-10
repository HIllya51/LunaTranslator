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

== Youdao Dictionary

https://www.patreon.com/posts/high-precision-133319068

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

== Локальный OCR

Встроенная легкая модель распознавания для китайского, японского и английского языков. Для распознавания других языков необходимо добавить соответствующие языковые модели в разделе `Загрузка ресурсов`.

В `Загрузке ресурсов` также представлены высокоточные модели для китайского, японского и английского языков. Если используется версия ПО для Win10 или система Windows11, можно настроить использование GPU для работы моделей, что повысит эффективность распознавания высокоточных моделей.

== SnippingTool

>[!WARNING]
Поддерживается только ОС Win10-Win11

Если у вас последняя версия Windows 11, можно использовать сразу, в противном случае необходимо установить этот модуль через `Загрузку ресурсов`.

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
Поддерживаются только операционные системы Win10-Win11

#### Поиск && Установка && Удаление OCR языковых пакетов

https://learn.microsoft.com/zh-cn/windows/powertoys/text-extractor#supported-languages

== Tesseract5

>[!WARNING]
>Эффективность слишком низкая, использование не рекомендуется.

https://github.com/tesseract-ocr/tesseract/releases

:::
