# 語音識別

在Windows 10和Windows 11上，可以使用Windows語音識別。

## 直接調用模式

該模式可以直接調用Windows語音識別模型，性能更好，且可以用於Windows 10。

::: warning
由於微軟更改了較新版本語言包的加密方法，系統中安裝的語言包和下載的較新版本語言包無法直接使用，欲使用請參閱[此文章](https://www.bilibili.com/read/cv42198812/)。
:::

在Windows 11上，可以直接檢測到系統內已安裝的語言及其語音識別模型，在`核心設置`->`其他`->`語音識別`中，選擇要識別的語言，並將該功能激活，即可開始使用。如果需要識別的語言沒有出現在選項中，請在系統內安裝對應語言，或尋找對應語言的識別模型將其解壓到軟件目錄中。

在Windows 10上，系統內缺少必要的運行時和識別模型；或者Windows 11的版本過低，系統自帶的運行時版本過低。請先下載我打包好的[運行時和中日英語言識別模型](https://lunatranslator.org/Resource/DirectLiveCaptions.zip)，將其解壓到軟件目錄中，軟件即可識別到我打包好的運行時和識別模型，從而可以使用該功能。

如果需要其他語言的識別模型，可以自行尋找對應語言的識別模型。方法爲：
在 https://store.rg-adguard.net/ 上，用`PacakgeFamilyName`搜索`MicrosoftWindows.Speech.{LANGUAGE}.1_cw5n1h2txyewy`，其中`{LANGUAGE}`是你所需要的語言名，例如法語爲`MicrosoftWindows.Speech.fr-FR.1_cw5n1h2txyewy`。然後，在下方下載最新版本的msix後，解壓到軟件目錄中即可。

::: details store.rg-adguard.net
![img](https://image.lunatranslator.org/zh/srpackage.png)
:::

## 間接讀取模式

該模式通過讀取**LiveCaptions**窗口文字來間接實現，僅能用於Windows 11。效能稍差，但不會有License和運行時相容性問題。

在Windows 11上，激活並切換到該模式後即可使用。