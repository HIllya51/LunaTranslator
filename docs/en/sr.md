# Speech Recognition

On Windows 10 and Windows 11, you can use Windows Speech Recognition.

On Windows 11, the system can directly detect installed languages and their speech recognition models. In `Core Settings` -> `Others` -> `Speech Recognition`, select the language you want to recognize and activate the feature to start using it. If the desired language does not appear in the options, install the corresponding language in the system or find the recognition model for that language and extract it into the software directory.

On Windows 10, the necessary runtime and recognition models are missing in the system. Please first download my packaged [runtime and Chinese-Japanese-English language recognition models](https://lunatranslator.org/Resource/DirectLiveCaptions.zip), extract them to the software directory, and the software will recognize the packaged runtime and recognition models, enabling this feature.

:::warning
If you are using Windows 10, do not place the software and the `runtime and Chinese-Japanese-English language recognition models` in a non-English path, as this will prevent recognition.
:::

If you need recognition models for other languages, you can find the corresponding language recognition models yourself. The method is as follows:
On https://store.rg-adguard.net/, search for `MicrosoftWindows.Speech.{LANGUAGE}.1_cw5n1h2txyewy` using `PacakgeFamilyName`, where `{LANGUAGE}` is the name of the language you need (for example, French is `MicrosoftWindows.Speech.fr-FR.1_cw5n1h2txyewy`). Then, download the latest version of the msix file and extract it to the software directory.

![img](https://image.lunatranslator.org/zh/srpackage.png)