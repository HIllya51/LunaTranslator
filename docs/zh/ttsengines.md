# 语音合成引擎

::: tabs

== Windows TTS

对于Windows 7及以上，可以在系统的语言设置中，添加语言的语音合成包，即可使用。

~~在Windows 11上，除了语言的语音合成包以外，还可以在`辅助功能`->`讲述人`->`添加自然语音`处添加更高质量的语音包。~~ 由于微软更改了自然语音包的加密方法，并静默推送升级，现已无法直接使用系统中安装的自然语音包，请使用以下方法，或参阅[此文章](https://www.bilibili.com/read/cv42198812/)。

在Windows 11上，可以从[NVDA 中文站](https://www.nvdacn.com/index.php/tts.html)下载`Microsoft Natural Voice（自然语音）`，然后将其解压到软件目录中，即可使用自然语音。在Windows 10上，除了需要下载语音包外，还需补充下载[自然语音运行时](https://lunatranslator.org/Resource/microsoft.cognitiveservices.speech)并解压到软件目录中。

== VoiceRoid2

在资源下载中，可以下载到相关资源，然后选择解压的路径即可。

但是请注意，对于**附加音源**，必须要先下载任意**整合包**，然后将其解压到整合包中才能使用，因为整合包包含了相对热门的音源以及必要的运行时，仅下载附加音源将缺少VoiceRoid2的运行时。

== VOICEVOX

需要下载[VOICEVOX](https://github.com/VOICEVOX/voicevox/releases)并运行。

默认的端口号和VOICEVOX的默认端口号相同。如果你不修改双方的设置，运行并激活即可使用。

== GPT-SoVITS

`API version`中的v2是GPT-SoVITS的API接口的版本，不是模型的版本，一般情况下，使用默认的v2即可。

其他参数中只添加了少量常用参数，如果需要其他参数，自己添加即可。

:::