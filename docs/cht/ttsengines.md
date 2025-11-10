# 語音合成引擎

::: tabs

== Windows TTS

#### SAPI

對於 Windows 7 及以上版本，可以在系統的語言設定中，新增對應語言的語音合成包，即可使用。

#### 自然語音

在 Windows 10 和 Windows 11 上，可以使用 Windows 自然語音。

>[!WARNING]
>由於微軟更改了較新版本語言包的加密方法，系統中安裝的語言包和下載的較新版本語言包無法直接使用，欲使用請參閱[此文章](https://www.bilibili.com/read/cv42198812/)。

在 Windows 11 上，除了對應語言的語音合成包以外，還可以在 Windows 系統設定中的`協助工具`->`視覺`的`朗讀程式`->`朗讀程式的語音`的`新增自然語音`處新增更高品質的語音包。

在 Windows 10 上，或不想在系統中新增，可以從 [NVDA 中文站](https://www.nvdacn.com/index.php/tts.html)下載`Microsoft Natural Voice（自然語音）`，然後將其解壓縮到軟體目錄中，即可使用自然語音。

在 Windows 10 上，系統內缺少必要的執行環境和辨識模型；或者 Windows 11 的版本過低，系統內建的執行環境版本過低。除了需要下載語音包外，還需補充下載[自然語音執行環境](https://lunatranslator.org/Resource/microsoft.cognitiveservices.speech)並解壓縮到軟體目錄中。

== VoiceRoid2

在資源下載中，可以下載到相關資源，然後選擇解壓縮的路徑即可。

但是請注意，對於**附加音源**，必須要先下載任意**整合包**，然後將其解壓縮到整合包中才能使用，因為整合包包含了相對熱門的音源以及必要的執行環境，僅下載附加音源將缺少 VoiceRoid2 的執行環境。

== VOICEVOX

需要下載 [VOICEVOX](https://github.com/VOICEVOX/voicevox/releases) 並執行。

預設的連接埠編號和 VOICEVOX 的預設連接埠編號相同。如果你不修改雙方的設定，執行並啟用後即可使用。

== GPT-SoVITS

`API version`中的`v2`是 GPT-SoVITS 的 API 介面的版本，不是模型的版本，一般情況下，使用預設的`v2`即可。

其他參數中只新增了少量常用參數，如果需要其他參數，自己新增即可。

:::