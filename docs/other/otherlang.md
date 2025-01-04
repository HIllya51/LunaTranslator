#### Language Definition

All supported languages are Defined in [language.py](../../py/LunaTranslator/language.py). If you want to add a new language, you must first register it in the class `Languages`

#### UI Languages

Now this program's UI supports [简体中文]() | [日本語](../../py/files/lang/ja.json) | [繁體中文](../../py/files/lang/cht.json) | [English](../../py/files/lang/en.json) | [Русский язык](../../py/files/lang/ru.json) | [Español](../../py/files/lang/es.json) | [한국어](../../py/files/lang/ko.json) | [Français](../../py/files/lang/fr.json)  | [Tiếng Việt](../../py/files/lang/vi.json) | [Türkçe](../../py/files/lang/tr.json) | [Polski](../../py/files/lang/pl.json) | [Українська Мова](../../py/files/lang/uk.json) | [Italiano](../../py/files/lang/it.json) | [ภาษาไทย](../../py/files/lang/th.json) | [Deutsch](../../py/files/lang/de.json) | [Svenska](../../py/files/lang/sv.json) | [Nederlands](../../py/files/lang/nl.json) | [Čeština](../../py/files/lang/cs.json) | [Português](../../py/files/lang/pt.json)

Most of them are machine translated from Chinese. You can translate manually to get more accurate translation.

Of all Defined languages, only a portion are already designated as UI supported languages. To add new UI language support, you need to register it in `UILanguages` and add the translation file to `files/lang/*.json`

#### Translator Languages

`TransLanguages` lists all supported languages accepted as translation APIs. To add a new language, in addition to adding it here, you also need to search the documentations of all APIs to see the language code they actually accept, and add it to the langmap of each `LunaTranslator/translator/*.py`, which is very troublesome.