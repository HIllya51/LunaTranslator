# LunaTranslator 
  
<p align="left">
    <a href="./LICENSE"><img src="https://img.shields.io/badge/license-GPL%203.0-dfd.svg"></a>
    <a href="https://github.com/HIllya51/LunaTranslator/releases"><img src="https://img.shields.io/github/v/release/HIllya51/LunaTranslator?color=ffa"></a>
    <a href="https://github.com/HIllya51/LunaTranslator/stargazers"><img src="https://img.shields.io/github/stars/HIllya51/LunaTranslator?color=ccf"></a>
    <a id="downloadlink" href="https://github.com/HIllya51/LunaTranslator/releases/download/v1.37.0/LunaTranslator.zip"><img src="https://img.shields.io/badge/download-%E4%B8%8B%E8%BD%BD-red"></a>
</p>
 
## 简体中文 | [Русский язык](README_ru.md) 

> **一款galgame翻译器**

## <a href="http://hillya51.github.io/" target="_blank">使用说明</a> 
 

## 功能支持

#### 文本源

&emsp;&emsp;**剪贴板** 支持从剪贴板中获取文本进行翻译

&emsp;&emsp;**OCR** 支持离线OCR(已部署)、WindowsOCR、百度OCR、有道OCR、ocrspace、docsumo，支持绑定截图窗口，避免窗口重叠。

&emsp;&emsp;**HOOK** 支持使用HOOK方式获取文本，支持使用特殊码，支持自动保存游戏及HOOK、自动加载HOOK


#### 翻译器

支持几乎所有能想得到的翻译引擎，包括： 

&emsp;&emsp;**离线翻译** 支持使用J北京7、金山快译、译典通进行离线翻译 

&emsp;&emsp;**免费在线翻译** 支持使用百度、必应、谷歌、阿里、有道、彩云、搜狗、DeepL、金山、讯飞、腾讯、字节、火山、papago、yeekit进行翻译

&emsp;&emsp;**注册在线翻译** 支持使用用户注册的百度、腾讯、有道、小牛、彩云、火山、deepl翻译密钥翻译

&emsp;&emsp;**预翻译** 支持读取人工翻译和聚合机器预翻译文件

&emsp;&emsp;**支持自定义翻译扩展** 支持使用python语言扩展其他我不知道的翻译接口

 


#### 语音合成

&emsp;&emsp;**离线TTS** 支持windowsTTS，支持VoiceRoid2，支持VOICEVOX

&emsp;&emsp;**在线TTS** 支持AzureTTS，支持火山TTS

#### 翻译优化

&emsp;&emsp;**文本处理** 支持文本去重、过滤HTML标签、过滤换行符、过滤字符及数字等简单处理；支持自定义简单文本替换和正则表达式替换

&emsp;&emsp;**翻译优化** 支持使用自定义专有名词翻译，支持导入VNR共享辞书

#### 日语学习

&emsp;&emsp;**日语分词及假名显示** 支持使用内置免下载分词及假名显示工具，支持使用Mecab优化分词及假名显示

&emsp;&emsp;**查词** 支持使用小学馆、灵格斯词典、EDICT(日英)词典进行单词查询

## 资源下载


<details>
<summary>点击查看</summary>

<table>
<tr><td>OCR-简体中文</td><td><a href="https://github.com/HIllya51/LunaTranslator/releases/download/v1.34.5/zh.zip">zh.zip</a></td></tr>
<tr><td>OCR-繁体中文</td><td><a href="https://github.com/HIllya51/LunaTranslator/releases/download/v1.34.5/cht.zip">cht.zip</a></td></tr>
<tr><td>OCR-韩语</td><td><a href="https://github.com/HIllya51/LunaTranslator/releases/download/v1.34.5/ko.zip">ko.zip</a></td></tr>
<tr><td>辞书-MeCab</td><td><a href="https://github.com/HIllya51/LunaTranslator/releases/download/v1.0/Mecab.zip">Mecab.zip</a></td></tr>
<tr><td>辞书-小学馆</td><td><a href="https://github.com/HIllya51/LunaTranslator/releases/download/v1.0/xiaoxueguan.db">xiaoxueguan.db</a></td></tr>
<tr><td>辞书-EDICT</td><td><a href="https://github.com/HIllya51/LunaTranslator/releases/download/v1.0/edict.db">edict.db</a></td></tr>
<tr><td>辞书-EDICT2</td><td><a href="https://github.com/HIllya51/LunaTranslator/releases/download/v1.1.2/edict2">edict2</a></td></tr>
<tr><td>辞书-JMdict</td><td><a href="https://github.com/HIllya51/LunaTranslator/releases/download/v1.1.2/JMdict.xml">JMdict.xml</a></td></tr>
<tr><td>辞书-灵格斯词典</td><td><a href="https://github.com/HIllya51/LunaTranslator/releases/download/v1.0/Lingoes.zip">Lingoes.zip</a></td></tr>
<tr><td>翻译-J北京7</td><td><a href="https://github.com/HIllya51/LunaTranslator/releases/download/v1.0/JBeijing7.zip">JBeijing7.zip</a></td></tr>
<tr><td>翻译-金山快译</td><td><a href="https://github.com/HIllya51/LunaTranslator/releases/download/v1.0/FastAIT09_Setup.25269.4101.zip">FastAIT09_Setup.25269.4101.zip</a></td></tr>
<tr><td>翻译-快译通</td><td><a href="https://github.com/HIllya51/LunaTranslator/releases/download/v1.0/DR.eye.zip">DR.eye.zip</a></td></tr>
<tr><td>转区-Locale-Emulator</td><td><a href="https://github.com/xupefei/Locale-Emulator/releases/download/v2.5.0.1/Locale.Emulator.2.5.0.1.zip">Locale.Emulator.2.5.0.1.zip</a></td></tr>
<tr><td>转区-Locale_Remulator</td><td><a href="https://github.com/InWILL/Locale_Remulator/releases/download/v1.4.6/Locale_Remulator.1.4.6.zip">Locale_Remulator.1.4.6.zip</a></td></tr>
<tr><td>语音-VoiceRoid2</td><td><a href="https://github.com/HIllya51/LunaTranslator/releases/download/v1.0/Yukari2.zip">Yukari2.zip</a></td></tr>
<tr><td>语音-VOICEVOX</td><td><a href="https://github.com/VOICEVOX/voicevox/releases/download/0.13.3/voicevox-windows-cpu-0.13.3.zip">voicevox-windows-cpu-0.13.3.zip</a></td></tr>
</table>  

</details>



## References

<details>
<summary>点击查看</summary>

* [Artikash/Textractor](https://github.com/Artikash/Textractor)

* [RapidAI/RapidOcrOnnx](https://github.com/RapidAI/RapidOcrOnnx)

* [PaddlePaddle/PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)

* [UlionTse/translators](https://github.com/UlionTse/translators)

* [Blinue/Magpie](https://github.com/Blinue/Magpie)

* [nanokina/ebyroid](https://github.com/nanokina/ebyroid)

* [@KirpichKrasniy](https://github.com/KirpichKrasniy)

</details>


 
## 支持作者

如果你感觉该软件对你有帮助，欢迎前往[爱发电](https://afdian.net/a/HIllya51)赞助我，谢谢，么么哒~