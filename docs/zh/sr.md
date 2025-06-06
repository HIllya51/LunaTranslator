# 语音识别

在Windows 10和Windows 11上，可以使用Windows语音识别。

在Windows 11上，可以直接检测到系统内已安装的语言及其语音识别模型，在`核心设置`->`其他`->`语音识别`中，选择要识别的语言，并将该功能激活，即可开始使用。如果需要识别的语言没有出现在选项中，请在系统内安装对应语言，或寻找对应语言的识别模型将其解压到软件目录中。

在Windows 10上，系统内缺少必要的运行时和识别模型，请先下载我打包好的[运行时和中日语言识别模型](https://1drv.ms/u/c/e598ac1f7a133b29/EaAWXcYACl9KnKHtuzMg2csB0XBGhR2d3-136PhM8B7B8Q?e=zE1dwj)，将其解压到软件目录中，软件即可识别到我打包好的运行时和识别模型，从而可以使用该功能。

:::warning
如果是Windows 10系统，请不要把软件和`运行时和中日语言识别模型`放到非英文路径中，否则会无法识别
:::

如果需要其他语言的识别模型，可以自行寻找对应语言的识别模型。方法为：
在 https://store.rg-adguard.net/ 上，用`PacakgeFamilyName`搜索`MicrosoftWindows.Speech.{LANGUAGE}.1_cw5n1h2txyewy`，其中`{LANGUAGE}`是你所需要的语言名，例如英文为`MicrosoftWindows.Speech.en-US.1_cw5n1h2txyewy`。然后，在下方下载最新版本的msix后，解压到软件目录中即可。

![img](https://image.lunatranslator.org/zh/srpackage.png)