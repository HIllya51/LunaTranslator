# Speech Synthesis Engine

::: tabs

== Windows TTS

For Windows 7 and above, you can add the text-to-speech package for a language in the system's language settings to use it.

~~On Windows 11, in addition to the language's speech synthesis package, you can also add higher-quality natural voices via `Accessibility` -> `Narrator` -> `Add natural voices`.~~ Due to Microsoft's changes to the encryption method of natural voice packages and their silent push updates, it is no longer possible to directly use the natural voice packages installed in the system. Please use the following method instead.

On Windows 10 & 11, in addition to the language speech synthesis packages, you can download the [NVDA Natural Voices Add-on Package](https://nvda.groups.io/g/nvda/topic/question_about_nvda_2025_and/112554082) and extract it into the software directory to enable natural voices.

== VoiceRoid2

In resource downloads, you can download related resources, then select the extraction path.

However, please note that for **additional voice sources**, you must first download any **integration pack**, then extract it into the integration pack to use it. This is because the integration pack contains relatively popular voice sources and necessary runtimes; downloading only additional voice sources will lack the VoiceRoid2 runtime.

== VOICEVOX

You need to download [VOICEVOX](https://github.com/VOICEVOX/voicevox/releases) and run it.

The default port number is the same as VOICEVOX's default port number. If you do not modify the settings on either side, you can run and activate it for use.

== GPT-SoVITS

v2 in `API version` is the version of GPT-SoVITS's API interface, not the model version. Generally, using the default v2 is sufficient.

Only a few commonly used parameters have been added to other parameters. If you need other parameters, you can add them yourself.

:::