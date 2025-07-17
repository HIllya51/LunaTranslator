### [简体中文](README.md) | [English](README_en.md) | [繁體中文](README_cht.md) | [한국어](README_ko.md) | [日本語](README_ja.md) | [Tiếng Việt](README_vi.md) | Русский язык

# LunaTranslator [Скачать & Запустить & Обновить](https://docs.lunatranslator.org/ru/README.html)

> **Переводчик визуальных новелл**

### Если у вас возникли трудности при использовании, вы можете обратиться к [инструкции](https://docs.lunatranslator.org/ru), а также присоединиться к нашему [Discord](https://discord.com/invite/ErtDwVeAbB).

## Поддерживаемые функции

#### Ввод текста

- **HOOK** Поддержка получения текста через HOOK. Для некоторых игровых движков также поддерживается [встроенный перевод](https://docs.lunatranslator.org/ru/embedtranslate.html). Также поддерживается извлечение текста из игр, работающих на некоторых [эмуляторах](https://docs.lunatranslator.org/ru/emugames.html). Для игр, которые не поддерживаются или поддерживаются плохо, пожалуйста, [отправьте отзыв](https://github.com/HIllya51/LunaTranslator/issues/new?assignees=&labels=enhancement&projects=&template=01_game_request.yaml).

- **OCR** Поддержка **[оффлайн OCR](https://docs.lunatranslator.org/ru/useapis/ocrapi.html)** и **[онлайн OCR](https://docs.lunatranslator.org/ru/useapis/ocrapi.html)**.

- **Буфер обмена** Поддержка получения текста из буфера обмена для перевода, а также вывода извлеченного текста в буфер обмена.

- **Другое** Также поддерживается **[распознавание речи](https://docs.lunatranslator.org/ru/sr.html)** и **перевод файлов**.

#### Переводчик

Поддерживает практически все мыслимые движки перевода, включая:

- **Онлайн-перевод** Поддержка множества онлайн-переводчиков, готовых к использованию без регистрации, а также **[традиционные переводчики](https://docs.lunatranslator.org/ru/useapis/tsapi.html)** и **[переводчики на основе больших моделей](https://docs.lunatranslator.org/ru/guochandamoxing.html)**, использующие API, зарегистрированные пользователем.

- **Оффлайн-перевод** Поддержка распространенных **традиционных переводчиков** и **[больших моделей перевода](https://docs.lunatranslator.org/ru/offlinellm.html)**, развернутых оффлайн.

- **Предварительный перевод** Поддержка чтения файлов предварительного перевода и кэширования переводов.

- **Поддержка пользовательских расширений перевода** Поддержка расширения других интерфейсов перевода с использованием языка Python.

#### Другие функции

- **[Синтез речи](https://docs.lunatranslator.org/ru/ttsengines.html)** Поддержка **оффлайн TTS** и **онлайн TTS**.

- **[Японская сегментация слов и произношение каной](https://docs.lunatranslator.org/ru/qa1.html)** Поддержка использования Mecab и других инструментов для токенизации и отображения каны.

- **[Поиск слов](https://docs.lunatranslator.org/ru/internaldict.html)** Поддержка использования **оффлайн-словарей** (MDICT) и **онлайн-словарей** для поиска слов.

- **[Anki](https://docs.lunatranslator.org/ru/qa2.html)** Поддержка добавления слов в Anki одним кликом.

- **[Загрузка расширений браузера](https://docs.lunatranslator.org/ru/yomitan.html)** Возможность загрузки расширений браузера, таких как Yomitan, для реализации дополнительных функций.

## Поддержка автора

Поддержка программного обеспечения требует усилий. Если вы считаете, что этот софт вам полезен, буду рад вашей поддержке через [Patreon](https://patreon.com/HIllya51). Ваша помощь станет стимулом для долгосрочного развития проекта. Спасибо!

<a href="https://patreon.com/HIllya51" target='_blank'><img width="200" src="../docs/become_a_patron_4x1_black_logo_white_text_on_coral.svg"></a>

## Лицензия

LunaTranslator использует лицензию [GPLv3](../LICENSE).