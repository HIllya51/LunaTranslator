
> **Транслятор для galgame**

## Поддержка функций

#### Ввод текста

- **HOOK** Поддерживает получение текста с использованием метода [HOOK](https://github.com/HIllya51/LunaHook), поддерживает использование специальных кодов, поддерживает автоматическое сохранение игр и HOOK, автоматическое загрузка HOOK и т.д. Для некоторых движков также поддерживается встроенная трансляция. Для игр, которые не поддерживаются или плохо поддерживаются, пожалуйста, [отправьте обратную связь](https://lunatranslator.org/Resource/game_support) 


- **OCR** поддерживает **офлайн OCR** (помимо [встроенного OCR-движка](https://github.com/HIllya51/LunaOCR), также поддерживает WindowsOCR, Tesseract5, manga-ocr, WeChat/QQ OCR) и **онлайн OCR** (Baidu, Youdao, Feishu, iFlytek, Google Lens, Google Cloud Vision, docsumo, ocrspace, Gemini, совместимые интерфейсы ChatGPT).

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

#### Изучение японского языка

- **Сегментация японских слов и отображение глифов** Поддерживает использование Mecab и других для сегментации и отображения глифов

- **Поиск слов** Поддерживает использование **оффлайн словарей** ( MDICT, Shougakukan, Lingoes Dictionary, EDICT/EDICT2 ) и **онлайн словарей** ( Youdao, weblio, Goo, Moji, jisho ) для поиска слов

- **Anki** Поддерживает добавление слов в Anki одним нажатием кнопки

