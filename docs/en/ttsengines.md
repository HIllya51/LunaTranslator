# Speech Synthesis Engine

::: tabs

== Windows TTS

On Windows 11, you can add narrator natural voice libraries in the system settings.

However, currently, natural voice libraries cannot be recognized by SAPI, so they cannot be used directly in LunaTranslator. But, you can install [NaturalVoiceSAPIAdapter](https://github.com/gexgd0419/NaturalVoiceSAPIAdapter), which can convert natural voice libraries to a SAPI interface, allowing them to be used in LunaTranslator.

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