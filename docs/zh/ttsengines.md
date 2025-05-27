# 语音合成引擎

::: tabs

== Windows TTS

对于Windows 7及以上，可以在系统的语言设置中，添加语言的语音合成包，即可使用。

对于Windows 11，除了语言的语音合成包以外，还可以在系统设置内添加讲述人自然语音库。但目前自然语音库无法被SAPI识别，因此无法直接在LunaTranslator中使用。但是，你可以安装[NaturalVoiceSAPIAdapter](https://github.com/gexgd0419/NaturalVoiceSAPIAdapter)，该程序可以将自然语音库转换为SAPI接口，从而在LunaTranslator中使用。

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