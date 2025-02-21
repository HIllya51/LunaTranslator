#### Language Definition

All supported languages are Defined in [language.py](../src/LunaTranslator/language.py). If you want to add a new language, you must first register it in the class `Languages`

#### UI Languages

Now this program's UI supports [简体中文]() | [日本語](../src/files/lang/ja.json) | [繁體中文](../src/files/lang/cht.json) | [English](../src/files/lang/en.json) | [Русский язык](../src/files/lang/ru.json) | [Español](../src/files/lang/es.json) | [한국어](../src/files/lang/ko.json) | [Français](../src/files/lang/fr.json)  | [Tiếng Việt](../src/files/lang/vi.json) | [Türkçe](../src/files/lang/tr.json) | [Polski](../src/files/lang/pl.json) | [Українська Мова](../src/files/lang/uk.json) | [Italiano](../src/files/lang/it.json) | [ภาษาไทย](../src/files/lang/th.json) | [Deutsch](../src/files/lang/de.json) | [Svenska](../src/files/lang/sv.json) | [Nederlands](../src/files/lang/nl.json) | [Čeština](../src/files/lang/cs.json) | [Português](../src/files/lang/pt.json)

Most of them are machine translated from Chinese. You can translate manually to get more accurate translation.

Of all Defined languages, only a portion are already designated as UI supported languages. To add new UI language support, you need to register it in `UILanguages` and add the translation file to `files/lang/*.json`

#### Translator Languages

`TransLanguages` lists all supported languages accepted as translation APIs. To add a new language, in addition to adding it here, you also need to search the documentations of all APIs to see the language code they actually accept, and add it to the langmap of each `LunaTranslator/translator/*.py`, which is very troublesome.