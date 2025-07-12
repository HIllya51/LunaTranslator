### 简体中文  | [English](README_en.md) | [繁體中文](README_cht.md) | [한국어](README_ko.md) | [日本語](README_ja.md) | [Tiếng Việt](README_vi.md) | [Русский язык](README_ru.md)

# LunaTranslator [软件下载](https://docs.lunatranslator.org/zh/README.html)

> **一款视觉小说翻译器**

### 如果使用中遇到困难，可以查阅[使用说明](https://docs.lunatranslator.org/zh)、观看[我的B站视频](https://space.bilibili.com/592120404/video)，也欢迎加入[QQ群](https://qm.qq.com/q/I5rr3uEpi2)。

## 功能支持

#### 文本输入

- **HOOK** 支持使用HOOK方式获取文本。对于部分游戏引擎，还支持[内嵌翻译](https://docs.lunatranslator.org/zh/embedtranslate.html)。还支持提取部分[模拟器](https://docs.lunatranslator.org/zh/emugames.html)上运行的游戏的文本。对于不支持或支持不好的游戏，请[提交反馈](https://github.com/HIllya51/LunaTranslator/issues/new?assignees=&labels=enhancement&projects=&template=01_game_request.yaml)

- **OCR** 支持 **[离线OCR](https://docs.lunatranslator.org/zh/useapis/ocrapi.html)** 和 **[在线OCR](https://docs.lunatranslator.org/zh/useapis/ocrapi.html)** 

- **剪贴板** 支持从剪贴板中获取文本进行翻译，也可以将提取的文本输出到剪贴板

- **其他** 还支持 **[语音识别](https://docs.lunatranslator.org/zh/sr.html)** 和**文件翻译**

#### 翻译器

支持几乎所有能想得到的翻译引擎，包括： 

- **在线翻译** 支持大量免注册开箱即用的在线翻译接口，也支持使用用户注册的API的 **[传统翻译](https://docs.lunatranslator.org/zh/useapis/tsapi.html)** 和 **[大模型翻译](https://docs.lunatranslator.org/zh/guochandamoxing.html)** 

- **离线翻译** 支持常见 **传统翻译** 引擎和离线部署的 **[大模型翻译](https://docs.lunatranslator.org/zh/offlinellm.html)**

- **预翻译** 支持读取预翻译文件，支持翻译缓存

- **支持自定义翻译扩展** 支持使用python语言扩展其他翻译接口

#### 其他功能

- **语音合成** 支持 **离线TTS** 和 **在线TTS**

- **日语分词及假名注音** 支持使用 Mecab 等分词和显示假名

- **查词** 支持使用 **离线辞书** ( MDICT ) 和 **在线辞书** 进行单词查询

- **Anki** 支持使用一键添加单词到anki中

- **加载浏览器插件** 可以在软件内加载Yomitan等浏览器插件以辅助实现一些其他功能

## 支持作者

软件维护不易，如果您感觉该软件对你有帮助，欢迎通过[爱发电](https://afdian.com/a/HIllya51)，或微信扫码赞助，您的支持将成为软件长期维护的助力，谢谢~

<a href="https://afdian.com/a/HIllya51"><img width="200" src="https://pic1.afdiancdn.com/static/img/welcome/button-sponsorme.png" alt=""></a>

<img src='../src/files/static/zan.jpg' style="height: 350px !important;">

## 开源许可

LunaTranslator使用 [GPLv3](../LICENSE) 许可证。
