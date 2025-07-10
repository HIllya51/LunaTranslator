### [简体中文](README.md) | [English](README_en.md) | 繁體中文 | [한국어](README_ko.md) | [日本語](README_ja.md) | [Tiếng Việt](README_vi.md)

# LunaTranslator

> **一款視覺小說翻譯器**

### 若使用中遇到困難，可以查閱[使用說明](https://docs.lunatranslator.org)、觀看[我的B站影片](https://space.bilibili.com/592120404/video)，也歡迎加入[Discord](https://discord.com/invite/ErtDwVeAbB)。

## 功能支援

#### 文字輸入

- **HOOK** 支援使用HOOK方式獲取文字。對於部分遊戲引擎，還支援[內嵌翻譯](https://docs.lunatranslator.org/embedtranslate.html)。還支援提取部分[模擬器](https://docs.lunatranslator.org/emugames.html)上運行的遊戲的文字。對於不支援或支援不佳的遊戲，請[提交反饋](https://github.com/HIllya51/LunaTranslator/issues/new?assignees=&labels=enhancement&projects=&template=01_game_request.yaml)

- **OCR** 支援 **[離線OCR](https://docs.lunatranslator.org/useapis/ocrapi.html)** 和 **[線上OCR](https://docs.lunatranslator.org/useapis/ocrapi.html)**

- **剪貼簿** 支援從剪貼簿中獲取文字進行翻譯，也可以將提取的文字輸出到剪貼簿

- **其他** 還支援 **[語音識別](https://docs.lunatranslator.org/sr.html)** 和**檔案翻譯**

#### 翻譯器

支援幾乎所有能想到的翻譯引擎，包括：

- **線上翻譯** 支援大量免註冊開箱即用的線上翻譯接口，也支援使用用戶註冊的API的 **[傳統翻譯](https://docs.lunatranslator.org/useapis/tsapi.html)** 和 **[大模型翻譯](https://docs.lunatranslator.org/guochandamoxing.html)**

- **離線翻譯** 支援常見 **傳統翻譯** 引擎和離線部署的 **[大模型翻譯](https://docs.lunatranslator.org/offlinellm.html)**

- **預翻譯** 支援讀取預翻譯檔案，支援翻譯緩存

- **支援自訂翻譯擴展** 支援使用python語言擴展其他翻譯接口

#### 其他功能

- **語音合成** 支援 **離線TTS** 和 **線上TTS**

- **日語分詞及假名顯示** 支援使用 Mecab 等分詞和顯示假名

- **查詞** 支援使用 **離線辭書** ( MDICT ) 和 **線上辭書** 進行單詞查詢

- **Anki** 支援一鍵添加單詞到anki中

- **載入瀏覽器插件** 可以在軟體內載入Yomitan等瀏覽器插件以輔助實現一些其他功能

## 支援作者

軟體維護不易，若您覺得此軟體對您有所幫助，歡迎透過[patreon](https://patreon.com/HIllya51)支持我，您的支持將成為軟體長期維護的動力，謝謝～

<a href="https://patreon.com/HIllya51" target='_blank'><img width="200" src="../docs/become_a_patron_4x1_black_logo_white_text_on_coral.svg"></a>

## 開源許可

LunaTranslator使用 [GPLv3](../LICENSE) 許可證。
