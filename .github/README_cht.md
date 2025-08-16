### [简体中文](README.md) | [English](README_en.md) | 繁體中文 | [한국어](README_ko.md) | [日本語](README_ja.md) | [Tiếng Việt](README_vi.md) | [Русский язык](README_ru.md)

# LunaTranslator [下載＆啟動＆更新](https://docs.lunatranslator.org/cht/README.html)  

> **一款視覺小說翻譯器**

### 若使用中遇到困難，可以查閱[使用說明](https://docs.lunatranslator.org/cht)、觀看[我的 B 站影片](https://space.bilibili.com/592120404/video)，也歡迎加入 [Discord](https://discord.com/invite/ErtDwVeAbB)／[QQ 群](https://qm.qq.com/q/I5rr3uEpi2)。

## 功能支援

#### 文字輸入

- **HOOK** 支援使用 HOOK 方式取得文字。對於部份遊戲引擎，還支援[內嵌翻譯](https://docs.lunatranslator.org/cht/embedtranslate.html)。還支援擷取部份[模擬器](https://docs.lunatranslator.org/cht/emugames.html)上執行的遊戲的文字。對於不支援或支援不佳的遊戲，請[提交回饋](https://github.com/HIllya51/LunaTranslator/issues/new?assignees=&labels=enhancement&projects=&template=01_game_request.yaml)

- **OCR** 支援 **[離線 OCR](https://docs.lunatranslator.org/cht/useapis/ocrapi.html)** 和 **[線上 OCR](https://docs.lunatranslator.org/cht/useapis/ocrapi.html)**

- **剪貼簿** 支援從剪貼簿中取得文字進行翻譯，也可以將擷取的文字輸出到剪貼簿

- **其他** 還支援 **[語音識別](https://docs.lunatranslator.org/cht/sr.html)** 和 **檔案翻譯**

#### 翻譯器

支援幾乎所有能想到的翻譯引擎，包括：

- **線上翻譯** 支援大量免註冊開箱即用的線上翻譯介面，也支援使用使用者註冊的 API 的 **[傳統翻譯](https://docs.lunatranslator.org/cht/useapis/tsapi.html)** 和 **[大模型翻譯](https://docs.lunatranslator.org/cht/guochandamoxing.html)**

- **離線翻譯** 支援常見 **傳統翻譯** 引擎和離線部署的 **[大模型翻譯](https://docs.lunatranslator.org/cht/offlinellm.html)**

- **預先翻譯** 支援讀取預先翻譯檔案，支援翻譯快取

- **支援自訂翻譯擴展** 支援使用 Python 語言擴展其他翻譯介面

#### 其他功能

- **[語音合成](https://docs.lunatranslator.org/cht/ttsengines.html)** 支援 **離線 TTS** 和 **線上 TTS**

- **[日語分詞及假名讀音標註](https://docs.lunatranslator.org/cht/qa1.html)** 支援使用 Mecab 等分詞和顯示假名

- **[查詞](https://docs.lunatranslator.org/cht/internaldict.html)** 支援使用 **離線辭書**（MDict） 和 **線上辭書** 進行單字查詢

- **[Anki](https://docs.lunatranslator.org/cht/qa2.html)** 支援一鍵新增單字到 Anki 中

- **[載入瀏覽器擴充功能](https://docs.lunatranslator.org/cht/yomitan.html)** 可以在軟體內載入 Yomitan 等瀏覽器擴充功能以輔助實現一些其他功能

## 支持作者

軟體維護不易，若您覺得此軟體對您有所幫助，歡迎透過 [Patreon](https://patreon.com/HIllya51) 支持我，您的支持將成為軟體長期維護的動力，謝謝～

<a href="https://patreon.com/HIllya51" target='_blank'><img width="200" src="../docs/become_a_patron_4x1_black_logo_white_text_on_coral.svg"></a>

## 開源授權

LunaTranslator 使用 [GPLv3](../LICENSE) 授權條款。
