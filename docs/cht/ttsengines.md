# 語音合成引擎

::: tabs

== Windows TTS

#### SAPI

對於Windows 7及以上，可以在系統的語言設置中，添加語言的語音合成包，即可使用。

#### 自然語音

在Windows 10和Windows 11上，可以使用Windows自然語音。

>[!WARNING]
>由於微軟更改了較新版本語言包的加密方法，系統中安裝的語言包和下載的較新版本語言包無法直接使用，欲使用請參閱[此文章](https://www.bilibili.com/read/cv42198812/)。

在Windows 11上，除了語言的語音合成包以外，還可以在`輔助功能`->`講述人`->`添加自然語音`處添加更高質量的語音包。

在Windows 10上，或不想在系統中添加，可以從[NVDA 中文站](https://www.nvdacn.com/index.php/tts.html)下載`Microsoft Natural Voice（自然語音）`，然後將其解壓到軟件目錄中，即可使用自然語音。

在Windows 10上，系統內缺少必要的運行時和識別模型；或者Windows 11的版本過低，系統自帶的運行時版本過低。除了需要下載語音包外，還需補充下載[自然語音運行時](https://lunatranslator.org/Resource/microsoft.cognitiveservices.speech)並解壓到軟件目錄中。

== VoiceRoid2

在資源下載中，可以下載到相關資源，然後選擇解壓的路徑即可。

但是請注意，對於**附加音源**，必須要先下載任意**整合包**，然後將其解壓到整合包中才能使用，因爲整合包包含了相對熱門的音源以及必要的運行時，僅下載附加音源將缺少VoiceRoid2的運行時。

== VOICEVOX

需要下載[VOICEVOX](https://github.com/VOICEVOX/voicevox/releases)並運行。

默認的端口號和VOICEVOX的默認端口號相同。如果你不修改雙方的設置，運行並激活即可使用。

== GPT-SoVITS

`API version`中的v2是GPT-SoVITS的API接口的版本，不是模型的版本，一般情況下，使用默認的v2即可。

其他參數中只添加了少量常用參數，如果需要其他參數，自己添加即可。

:::