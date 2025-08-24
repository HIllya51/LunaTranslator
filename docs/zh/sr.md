# 语音识别

在Windows 10和Windows 11上，可以使用Windows语音识别。

## 直接调用模式

该模式可以直接调用Windows语音识别模型，性能更好，且可以用于Windows 10。

::: danger
**由于微软更改了较新版本语言包的加密方法，系统中安装的语言包和下载的较新版本语言包无法直接使用，欲使用请参阅[此文章](https://www.bilibili.com/read/cv42198812/)。**
:::

在Windows 11上，可以直接检测到系统内已安装的语言及其语音识别模型，在`核心设置`->`其他`->`语音识别`中，选择要识别的语言，并将该功能激活，即可开始使用。如果需要识别的语言没有出现在选项中，请在系统内安装对应语言，或寻找对应语言的识别模型将其解压到软件目录中。

在Windows 10上，系统内缺少必要的运行时和识别模型；或者Windows 11的版本过低，系统自带的运行时版本过低。请先下载我打包好的[运行时和中日英语言识别模型](https://lunatranslator.org/Resource/DirectLiveCaptions.zip)，将其解压到软件目录中，软件即可识别到我打包好的运行时和识别模型，从而可以使用该功能。

如果需要其他语言的识别模型，可以自行寻找对应语言的识别模型。方法为：
在 https://store.rg-adguard.net/ 上，用`PacakgeFamilyName`搜索`MicrosoftWindows.Speech.{LANGUAGE}.1_cw5n1h2txyewy`，其中`{LANGUAGE}`是你所需要的语言名，例如法语为`MicrosoftWindows.Speech.fr-FR.1_cw5n1h2txyewy`。然后，在下方下载最新版本的msix后，解压到软件目录中即可。

::: details store.rg-adguard.net
![img](https://image.lunatranslator.org/zh/srpackage.png)
:::

## 间接读取模式

该模式通过读取**LiveCaptions**窗口文字来间接实现，仅能用于Windows 11。性能稍差，但不会有License和运行时兼容性问题。

在Windows 11上，激活并切换到该模式后即可使用。
