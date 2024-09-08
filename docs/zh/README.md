
> **一款galgame翻译器**

## 功能支持

#### 文本源

- **剪贴板** 支持从剪贴板中获取文本进行翻译

- **OCR** 支持 **离线OCR** ( 内置OCR引擎外，还支持WindowsOCR、Tessearact5、manga-ocr、WeChat/QQ OCR ) 和 **在线OCR** ( 百度OCR/图片翻译、有道OCR/图片翻译、有道OCR/图片翻译、飞书OCR、讯飞OCR、Google Lens、Google Cloud Vision、docsumo、ocrspace ) 。还可以使用**多模态大模型**进行OCR ( 支持GeminiOCR、ChatGPT兼容接口 )

- **HOOK** 支持使用HOOK方式获取文本，支持使用特殊码，支持自动保存游戏及HOOK、自动加载HOOK等。对于部分引擎，还支持内嵌翻译。


#### 翻译器

支持几乎所有能想得到的翻译引擎，包括： 

- **免费在线翻译** 支持使用百度、必应、谷歌、阿里、有道、彩云、搜狗、讯飞、腾讯、字节、火山、DeepL/DeepLX、papago、yandex、lingva、reverso、TranslateCom、ModernMT

- **注册在线翻译** 支持使用用户注册的 **传统翻译** ( 百度、腾讯、有道、小牛、彩云、火山、DeepL、yandex、google、ibm、Azure、飞书 ) 和 **大模型翻译** ( ChatGPT兼容接口、claude、cohere、gemini、百度千帆、腾讯混元 ) 

- **离线翻译** 支持 **传统翻译** ( J北京7、金山快译、译典通、ezTrans、Sugoi、MT5 ) 和离线部署的 **大模型翻译** ( ChatGPT兼容接口、Sakura大模型 ) 

- **Chrome调试翻译** 支持 **传统翻译** ( deepl、yandex、有道、百度、腾讯、必应、彩云、小牛、阿里、谷歌 ) 和 **大模型翻译** ( chatgpt、deepseek、moonshot、qianwen、chatglm、Theb.ai ) 

- **预翻译** 支持读取预翻译文件，支持翻译缓存

- **支持自定义翻译扩展** 支持使用python语言扩展其他翻译接口
 

#### 语音合成

- **离线TTS** 支持WindowsTTS、VoiceRoid2/VoiceRoid+、NeoSpeech、VOICEVOX、VITS

- **在线TTS** 支持火山TTS、有道TTS、EdgeTTS、谷歌TTS

#### 翻译优化

- **文本处理** 支持十余种常见文本处理方式，并可以通过组合和执行顺序的调整，实现复杂的文本处理

- **翻译优化** 支持使用自定义专有名词翻译，支持导入VNR共享辞书

#### 日语学习

- **日语分词及假名显示** 支持使用 Mecab 等分词和显示假名

- **查词** 支持使用 **离线辞书** ( MDICT、小学馆、灵格斯词典、EDICT/EDICT2 ) 和 **在线辞书** ( 有道、weblio、Goo、Moji、jisho ) 进行单词查询

- **Anki** 支持使用一键添加单词到anki中
