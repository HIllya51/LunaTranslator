# LunaTranslator

<p align="left">
    <img src="https://img.shields.io/github/license/HIllya51/LunaTranslator">
    <a href="https://github.com/HIllya51/LunaTranslator/releases"><img src="https://img.shields.io/github/v/release/HIllya51/LunaTranslator?color=ffa"></a>
    <a href="https://github.com/HIllya51/LunaTranslator/releases/latest/download/LunaTranslator.zip" target="_blank"><img src="https://img.shields.io/badge/download_64bit-blue"/></a> <a href="https://github.com/HIllya51/LunaTranslator/releases/latest/download/LunaTranslator_x86.zip" target="_blank"><img src="https://img.shields.io/badge/download_32bit-blue"/></a> <img src="https://img.shields.io/badge/OS-windows 7--11 / wine-FF0000"/>
</p>

### [Инструкция по использованию](https://docs.lunatranslator.org/#/ru/)   <a href="https://discord.com/invite/ErtDwVeAbB"><img  src="https://img.shields.io/discord/1262692128031772733?label=Discord&logo=discord&color=FF007C"></a> 

### Упрощенный китайский | [Русский язык](README_ru.md) | [Английский](README_en.md) | [Другие языки](otherlang.md) 

> **Транслятор для galgame**

## Поддержка функций

#### Ввод текста

- **HOOK** Поддерживает получение текста с использованием метода HOOK, поддерживает использование специальных кодов, поддерживает автоматическое сохранение игр и HOOK, автоматическое загрузка HOOK и т.д. Для некоторых движков также поддерживается встроенная трансляция. Для игр, которые не поддерживаются или плохо поддерживаются, пожалуйста, [отправьте обратную связь](https://lunatranslator.org/Resource/game_support) 


- **OCR** Поддерживает **оффлайн OCR** ( помимо встроенного движка OCR, также поддерживает WindowsOCR, Tessearact5, manga-ocr, WeChat/QQ OCR ) и **онлайн OCR** ( Baidu OCR/перевод изображений, Youdao OCR/перевод изображений, Youdao OCR/перевод изображений, Lark OCR, iFlytek OCR, Google Lens, Google Cloud Vision, docsumo, ocrspace ). Также можно использовать **многомодальные большие модели** для OCR ( поддерживает GeminiOCR, интерфейс совместимый с ChatGPT )

- **Буфер обмена** Поддерживает получение текста из буфера обмена для перевода

- **Вывод текста** Извлеченный текст может быть выведен в буфер обмена, Websocket для использования другими программами.

#### Транслятор

Поддерживает почти все представимые системы перевода, включая: 

- **Бесплатные онлайн переводы** Поддерживает использование Baidu, Bing, Google, Alibaba, Youdao, Caiyun, Sogou, iFlytek, Tencent, ByteDance, Volcano, DeepL/DeepLX, papago, yandex, lingva, reverso, TranslateCom, ModernMT

- **Зарегистрированные онлайн переводы** Поддерживает использование зарегистрированных пользователем **традиционных переводов** ( Baidu, Tencent, Youdao, Xiaoniu, Caiyun, Volcano, DeepL, yandex, google, ibm, Azure, Lark ) и **больших моделей перевода** ( интерфейс совместимый с ChatGPT, claude, cohere, gemini, Baidu Qianfan, Tencent Hunyuan )

- **Оффлайн перевод** Поддерживает **традиционный перевод** ( J Beijing 7, Kingsoft, Yidiantong, ezTrans, Sugoi, MT5 ) и оффлайн развернутый **большой модельный перевод** ( интерфейс совместимый с ChatGPT, Sakura большой модель )

- **Chrome отладочный перевод** Поддерживает **традиционный перевод** ( deepl, yandex, youdao, baidu, tencent, bing, caiyun, xiaoniu, alibaba, google ) и **большой модельный перевод** ( chatgpt, deepseek, moonshot, qianwen, chatglm, Theb.ai, DuckDuckGo )

- **Предварительный перевод** Поддерживает чтение предварительно переведенных файлов, поддерживает кэширование переводов

- **Поддержка пользовательских расширений перевода** Поддерживает расширение других интерфейсов перевода с использованием языка Python
 
 
#### Синтез речи

- **Оффлайн TTS** Поддерживает WindowsTTS, VoiceRoid2/VoiceRoid+, NeoSpeech, VOICEVOX, VITS

- **Онлайн TTS** Поддерживает Volcano TTS, Youdao TTS, Edge TTS, Google TTS

#### Оптимизация перевода

- **Обработка текста** Поддерживает более десяти распространенных методов обработки текста, и с помощью комбинирования и изменения порядка выполнения можно выполнять сложную обработку текста

- **Оптимизация перевода** Поддерживает использование пользовательских переводов собственных названий, поддерживает импорт общих словарей VNR

#### Изучение японского языка

- **Сегментация японских слов и отображение глифов** Поддерживает использование Mecab и других для сегментации и отображения глифов

- **Поиск слов** Поддерживает использование **оффлайн словарей** ( MDICT, Shougakukan, Lingoes Dictionary, EDICT/EDICT2 ) и **онлайн словарей** ( Youdao, weblio, Goo, Moji, jisho ) для поиска слов

- **Anki** Поддерживает добавление слов в Anki одним нажатием кнопки

## Поддержка автора

Если вы считаете, что программа вам полезна, приглашаю вас стать моим [спонсором](https://patreon.com/HIllya51). Спасибо ~