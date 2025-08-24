# Speech Recognition

On Windows 10 and Windows 11, you can use Windows Speech Recognition.

## Direct Call Mode

This mode can directly call the Windows speech recognition model with better performance, and can be used on Windows 10.

::: danger
**Due to Microsoft's changes in the encryption method for newer version language packs, the language packs installed in the system and the downloaded newer version language packs cannot be used directly. Please refer to [this article](https://www.patreon.com/posts/fixing-use-of-on-133196054) for usage instructions.**
:::

On Windows 11, the system can directly detect installed languages and their speech recognition models. In `Core Settings` -> `Others` -> `Speech Recognition`, select the language you want to recognize and activate the feature to start using it. If the desired language does not appear in the options, install the corresponding language in the system or find the recognition model for that language and extract it into the software directory.

On Windows 10, the necessary runtime and recognition models are missing in the system; or the Windows 11 version is too low, and the built-in runtime version is outdated. Please first download my packaged [runtime and Chinese-Japanese-English language recognition models](https://lunatranslator.org/Resource/DirectLiveCaptions.zip), extract them to the software directory, and the software will recognize the packaged runtime and recognition models, enabling this feature.

If you need recognition models for other languages, you can find the corresponding language recognition models yourself. The method is as follows:
On https://store.rg-adguard.net/, search for `MicrosoftWindows.Speech.{LANGUAGE}.1_cw5n1h2txyewy` using `PacakgeFamilyName`, where `{LANGUAGE}` is the name of the language you need (for example, French is `MicrosoftWindows.Speech.fr-FR.1_cw5n1h2txyewy`). Then, download the latest version of the msix file and extract it to the software directory.

::: details store.rg-adguard.net
![img](https://image.lunatranslator.org/zh/srpackage.png)
:::

## Indirect Read Mode

This mode works indirectly by reading text from the **LiveCaptions** window and is only available on Windows 11. The performance is slightly worse, but there are no license or runtime compatibility issues.

On Windows 11, you can use it by simply activating and switching to this mode.