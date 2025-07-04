# Speech Synthesis Engine

::: tabs

== Windows TTS

1. SAPI

    For Windows 7 and above, you can add the text-to-speech package for a language in the system's language settings to use it.

1. Natural Voice

    On Windows 10 and Windows 11, you can use Windows Natural Voice.

    ::: warning
    Due to Microsoft's changes in the encryption method for newer version language packs, the language packs installed in the system and the downloaded newer version language packs cannot be used directly. Please refer to [this article](https://www.patreon.com/posts/fixing-use-of-on-133196054) for usage instructions.
    :::

    On Windows 11, in addition to the language's speech synthesis package, you can also add higher-quality natural voices via `Accessibility` -> `Narrator` -> `Add natural voices`.

    On Windows 10, or if you don't want to add it to the system, you can download `Microsoft Natural Voice` from [NVDA Chinese Website](https://www.nvdacn.com/index.php/tts.html) and extract it to the software directory to use natural voices. 

    On Windows 10, in addition to downloading the voice package, you also need to download the [Natural Voice Runtime](https://lunatranslator.org/Resource/microsoft.cognitiveservices.speech) and extract it to the software directory. 

    ::: warning
    Do not place the software, `runtime`, and `language pack` in non-English paths, otherwise they will not be recognized.
    :::
    
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