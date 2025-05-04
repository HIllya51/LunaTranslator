# LunaTranslator

> **一款galgame翻译器**
 
### 简体中文  | [English](README_en.md) | [Other Language](otherlang.md)

### [使用说明](https://docs.lunatranslator.org/) | [视频教程](https://space.bilibili.com/592120404/video) | [软件下载](https://docs.lunatranslator.org/README.html) | [![](https://img.shields.io/badge/QQ群-963119821-FF007C?style=for-the-badge)](https://qm.qq.com/q/I5rr3uEpi2) [![](https://img.shields.io/discord/1262692128031772733?label=Discord&logo=discord&color=FF007C&style=for-the-badge)](https://discord.com/invite/ErtDwVeAbB)

## 功能支持

#### 文本输入

- **HOOK** 支持使用HOOK方式获取文本。对于部分游戏引擎，还支持[内嵌翻译](https://docs.lunatranslator.org/embedtranslate.html)。还支持提取部分[模拟器](https://docs.lunatranslator.org/emugames.html)上运行的游戏的文本。对于不支持或支持不好的游戏，请[提交反馈](https://github.com/HIllya51/LunaTranslator/issues/new?assignees=&labels=enhancement&projects=&template=01_game_request.yaml)

- **OCR** 支持 **[离线OCR](https://docs.lunatranslator.org/useapis/ocrapi.html)** 和 **[在线OCR](https://docs.lunatranslator.org/useapis/ocrapi.html)** 

- **剪贴板** 支持从剪贴板中获取文本进行翻译，也可以将提取的文本输出到剪贴板

#### 翻译器

支持几乎所有能想得到的翻译引擎，包括： 

- **在线翻译** 支持大量免注册开箱即用的在线翻译接口，也支持使用用户注册的API的 **[传统翻译](https://docs.lunatranslator.org/useapis/tsapi.html)** 和 **[大模型翻译](https://docs.lunatranslator.org/guochandamoxing.html)** 

- **离线翻译** 支持常见 **传统翻译** 引擎和离线部署的 **[大模型翻译](https://docs.lunatranslator.org/offlinellm.html)**

- **预翻译** 支持读取预翻译文件，支持翻译缓存

- **支持自定义翻译扩展** 支持使用python语言扩展其他翻译接口

#### 其他功能

- **语音合成** 支持 **离线TTS** 和 **在线TTS**

- **日语分词及假名显示** 支持使用 Mecab 等分词和显示假名

- **查词** 支持使用 **离线辞书** ( MDICT ) 和 **在线辞书** 进行单词查询

- **Anki** 支持使用一键添加单词到anki中

- **加载浏览器插件** 可以在软件内加载Yomitan等浏览器插件以辅助实现一些其他功能

## 支持作者

如果你感觉该软件对你有帮助，欢迎微信扫码赞助，谢谢，么么哒~
<img src='../src/files/static/zan.jpg' style="height: 400px !important;">

## 开源许可

LunaTranslator使用 [GPLv3](../LICENSE) 许可证。

<details>
<summary>引用的项目</summary>

* ![img](https://img.shields.io/github/license/opencv/opencv) [opencv/opencv](https://github.com/opencv/opencv)
* ![img](https://img.shields.io/github/license/microsoft/onnxruntime) [microsoft/onnxruntime](https://github.com/microsoft/onnxruntime)
* ![img](https://img.shields.io/github/license/Artikash/Textractor) [Artikash/Textractor](https://github.com/Artikash/Textractor)
* ![img](https://img.shields.io/github/license/RapidAI/RapidOcrOnnx) [RapidAI/RapidOcrOnnx](https://github.com/RapidAI/RapidOcrOnnx)
* ![img](https://img.shields.io/github/license/PaddlePaddle/PaddleOCR) [PaddlePaddle/PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)
* ![img](https://img.shields.io/github/license/Blinue/Magpie) [Blinue/Magpie](https://github.com/Blinue/Magpie)
* ![img](https://img.shields.io/github/license/nanokina/ebyroid) [nanokina/ebyroid](https://github.com/nanokina/ebyroid)
* ![img](https://img.shields.io/github/license/xupefei/Locale-Emulator) [xupefei/Locale-Emulator](https://github.com/xupefei/Locale-Emulator)
* ![img](https://img.shields.io/github/license/InWILL/Locale_Remulator) [InWILL/Locale_Remulator](https://github.com/InWILL/Locale_Remulator)
* ![img](https://img.shields.io/github/license/zxyacb/ntlea) [zxyacb/ntlea](https://github.com/zxyacb/ntlea)
* ![img](https://img.shields.io/github/license/Chuyu-Team/YY-Thunks) [Chuyu-Team/YY-Thunks](https://github.com/Chuyu-Team/YY-Thunks)
* ![img](https://img.shields.io/github/license/Chuyu-Team/VC-LTL5) [Chuyu-Team/VC-LTL5](https://github.com/Chuyu-Team/VC-LTL5)
* ![img](https://img.shields.io/github/license/uyjulian/AtlasTranslate) [uyjulian/AtlasTranslate](https://github.com/uyjulian/AtlasTranslate)
* ![img](https://img.shields.io/github/license/ilius/pyglossary) [ilius/pyglossary](https://github.com/ilius/pyglossary)
* ![img](https://img.shields.io/github/license/ikegami-yukino/mecab) [ikegami-yukino/mecab](https://github.com/ikegami-yukino/mecab)
* ![img](https://img.shields.io/github/license/AngusJohnson/Clipper2) [AngusJohnson/Clipper2](https://github.com/AngusJohnson/Clipper2)
* ![img](https://img.shields.io/github/license/rapidfuzz/rapidfuzz-cpp) [rapidfuzz/rapidfuzz-cpp](https://github.com/rapidfuzz/rapidfuzz-cpp)
* ![img](https://img.shields.io/github/license/TsudaKageyu/minhook) [TsudaKageyu/minhook](https://github.com/TsudaKageyu/minhook)
* ![img](https://img.shields.io/github/license/lobehub/lobe-icons) [lobehub/lobe-icons](https://github.com/lobehub/lobe-icons)
* ![img](https://img.shields.io/github/license/kokke/tiny-AES-c) [kokke/tiny-AES-c](https://github.com/kokke/tiny-AES-c)
* ![img](https://img.shields.io/github/license/TPN-Team/OCR) [TPN-Team/OCR](https://github.com/TPN-Team/OCR)
* ![img](https://img.shields.io/github/license/AuroraWright/owocr) [AuroraWright/owocr](https://github.com/AuroraWright/owocr)
* ![img](https://img.shields.io/github/license/b1tg/win11-oneocr) [b1tg/win11-oneocr](https://github.com/b1tg/win11-oneocr)
* ![img](https://img.shields.io/github/license/mity/md4c) [mity/md4c](https://github.com/mity/md4c)
* ![img](https://img.shields.io/github/license/swigger/wechat-ocr) [swigger/wechat-ocr](https://github.com/swigger/wechat-ocr)
* ![img](https://img.shields.io/github/license/rupeshk/MarkdownHighlighter) [rupeshk/MarkdownHighlighter](https://github.com/rupeshk/MarkdownHighlighter)
* ![img](https://img.shields.io/github/license/sindresorhus/github-markdown-css) [sindresorhus/github-markdown-css](https://github.com/sindresorhus/github-markdown-css)
</details>
