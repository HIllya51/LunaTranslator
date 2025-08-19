# 語音識別

在 Windows 10 和 Windows 11 上，可以使用 Windows 語音辨識。

## 直接調用模式

該模式可以直接調用 Windows 語音辨識模型，效能更好，且可以用於 Windows 10。

::: warning
由於微軟更改了較新版本語言包的加密方法，系統中安裝的語言包和下載的較新版本語言包無法直接使用，欲使用請參閱[此文章](https://www.bilibili.com/read/cv42198812/)。
:::

在 Windows 11 上，可以直接偵測到系統內已安裝的語言及其語音識別模型，在`核心設定`->`其他`->`語音識別`中，選擇要識別的語言，並將該功能啟用，即可開始使用。如果需要識別的語言沒有出現在選項中，請在系統內安裝對應語言，或尋找對應語言的識別模型將其解壓縮到軟體目錄中。

在 Windows 10 上，系統內缺少必要的執行環境和識別模型；或者 Windows 11 的版本過低，系統內建的執行環境版本過低。請先下載我打包好的[執行環境和中日英語言識別模型](https://lunatranslator.org/Resource/DirectLiveCaptions.zip)，將其解壓縮到軟體目錄中，軟體即可識別到我打包好的執行環境和識別模型，從而可以使用該功能。

如果需要其他語言的識別模型，可以自行尋找對應語言的識別模型。方法為：
在 https://store.rg-adguard.net/ 上，用`PacakgeFamilyName`搜尋`MicrosoftWindows.Speech.{LANGUAGE}.1_cw5n1h2txyewy`，其中`{LANGUAGE}`是你所需要的語言代碼，例如法語為`MicrosoftWindows.Speech.fr-FR.1_cw5n1h2txyewy`。然後，在下方下載最新版本的 MSIX 後，解壓縮到軟體目錄中即可。

::: details store.rg-adguard.net
![img](https://image.lunatranslator.org/zh/srpackage.png)
:::

## 間接讀取模式

該模式透過讀取 **LiveCaptions** 視窗文字來間接實現，僅能用於 Windows 11。效能稍差，但不會有 License 和執行環境相容性問題。

在 Windows 11 上，啟用並切換到該模式後即可使用。