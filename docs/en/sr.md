# Speech Recognition

On Windows 10 and Windows 11, you can use Windows Speech Recognition.

On Windows 11, the system can directly detect installed languages and their speech recognition models. In `Core Settings` -> `Others` -> `Speech Recognition`, select the language you want to recognize and activate the feature to start using it. If the desired language does not appear in the options, install the corresponding language in the system or find the recognition model for that language and extract it into the software directory.

On Windows 10, the system lacks the necessary runtime and recognition models. First, download the pre-packaged [runtime and Chinese/Japanese recognition models](https://1drv.ms/u/c/e598ac1f7a133b29/EaAWXcYACl9KnKHtuzMg2csB0XBGhR2d3-136PhM8B7B8Q?e=zE1dwj) and extract them into the software directory. The software will then detect the packaged runtime and recognition models, enabling the feature.

:::warning
If you are using Windows 10, do not place the software and the "runtime and CJL language recognition models" in a non-English path, otherwise it will fail to recognize.
:::

If you need speech recognition models for other languages, you can find the corresponding language models yourself. The method is as follows:
On https://store.rg-adguard.net/, search for `MicrosoftWindows.Speech.{LANGUAGE}.1_cw5n1h2txyewy` using `PacakgeFamilyName`, where `{LANGUAGE}` is the name of the language you need. For example, for English, it would be `MicrosoftWindows.Speech.en-US.1_cw5n1h2txyewy`. Then, download the latest version of the msix file below and extract it to the software directory.

![img](https://image.lunatranslator.org/zh/srpackage.png)