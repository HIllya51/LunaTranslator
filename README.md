# LunaTranslator 
  
<p align="left">
    <img src="https://img.shields.io/github/license/HIllya51/LunaTranslator">
    <a href="https://github.com/HIllya51/LunaTranslator/releases"><img src="https://img.shields.io/github/v/release/HIllya51/LunaTranslator?color=ffa"></a>
    <a href="https://github.com/HIllya51/LunaTranslator/releases/latest/download/LunaTranslator.zip" target="_blank"><img src="https://img.shields.io/badge/download_64bit-blue"/></a> <a href="https://github.com/HIllya51/LunaTranslator/releases/latest/download/LunaTranslator_x86.zip" target="_blank"><img src="https://img.shields.io/badge/download_32bit-blue"/></a>
</p>

### [使用说明](https://docs.lunatranslator.org/#/zh/) [视频教程](https://space.bilibili.com/592120404/video) <a href="https://qm.qq.com/q/I5rr3uEpi2"><img src="https://img.shields.io/badge/QQ群-963119821-FF007C"></a> <a href="https://discord.com/invite/ErtDwVeAbB"><img src="https://img.shields.io/discord/1262692128031772733?label=Discord&logo=discord&color=FF007C"></a>

 
### 简体中文  | [English](docs/other/README_en.md) | [Other Language](docs/other/otherlang.md) 

> **一款galgame翻译器**

## 功能支持

#### 文本输入

- **HOOK** 支持使用HOOK方式获取文本，支持使用特殊码，支持自动保存游戏及HOOK、自动加载HOOK等。对于部分引擎，还支持内嵌翻译。对于不支持或支持不好的游戏，请[提交反馈](https://github.com/HIllya51/LunaTranslator/issues/new?assignees=&labels=enhancement&projects=&template=01_game_request.yaml)


- **OCR** 支持 **离线OCR** ( 除内置OCR引擎外，还支持WindowsOCR、Tessearact5、manga-ocr、WeChat/QQ OCR ) 和 **在线OCR** ( 百度、有道、讯飞、Google Lens、Google Cloud Vision、docsumo、ocrspace、Gemini、ChatGPT兼容接口 )

- **剪贴板** 支持从剪贴板中获取文本进行翻译

- **文本输出** 提取的文本可以输出到剪贴板、Websocket，以供其他程序使用。

#### 翻译器

支持几乎所有能想得到的翻译引擎，包括： 

- **免费在线翻译** 支持使用百度、必应、谷歌、阿里、有道、彩云、搜狗、讯飞、腾讯、字节、火山、DeepL/DeepLX、papago、yandex、lingva、reverso、TranslateCom、ModernMT

- **注册在线翻译** 支持使用用户注册的 **传统翻译** ( 百度、腾讯、有道、小牛、彩云、火山、DeepL、yandex、google、ibm、Azure ) 和 **大模型翻译** ( ChatGPT兼容接口、claude、cohere、gemini、百度千帆、腾讯混元 ) 

- **离线翻译** 支持 **传统翻译** ( J北京7、金山快译、译典通、ezTrans、Sugoi、Atlas、LEC ) 和离线部署的 **大模型翻译** ( ChatGPT兼容接口、Sakura大模型 ) 

- **预翻译** 支持读取预翻译文件，支持翻译缓存

- **支持自定义翻译扩展** 支持使用python语言扩展其他翻译接口
 

#### 语音合成

- **离线TTS** 支持WindowsTTS、VoiceRoid2/VoiceRoid+、NeoSpeech、VOICEVOX、VITS

- **在线TTS** 支持火山TTS、有道TTS、EdgeTTS、谷歌TTS


#### 日语学习

- **日语分词及假名显示** 支持使用 Mecab 等分词和显示假名

- **查词** 支持使用 **离线辞书** ( MDICT、小学馆、灵格斯词典、EDICT/EDICT2 ) 和 **在线辞书** ( 有道、weblio、Goo、Moji、jisho、JapanDict ) 进行单词查询

- **Anki** 支持使用一键添加单词到anki中

## 引用

<details>
<summary>点击查看</summary>

* [RapidAI/RapidOcrOnnx](https://github.com/RapidAI/RapidOcrOnnx)

* [PaddlePaddle/PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)

* [UlionTse/translators](https://github.com/UlionTse/translators)

* [Blinue/Magpie](https://github.com/Blinue/Magpie)

* [nanokina/ebyroid](https://github.com/nanokina/ebyroid)

* [xupefei/Locale-Emulator](https://github.com/xupefei/Locale-Emulator)

* [InWILL/Locale_Remulator](https://github.com/InWILL/Locale_Remulator)

* [zxyacb/ntlea](https://github.com/zxyacb/ntlea)

* [Chuyu-Team/YY-Thunks](https://github.com/Chuyu-Team/YY-Thunks)

* [@KirpichKrasniy](https://github.com/KirpichKrasniy)

* [uyjulian/AtlasTranslate](https://github.com/uyjulian/AtlasTranslate)

</details>


 
## 支持作者

如果你感觉该软件对你有帮助，欢迎微信扫码赞助，谢谢，么么哒~

<img src='.\\py\\files\\zan.jpg' style="height: 400px !important;">

