# 음성 합성 엔진

::: tabs

== Windows TTS

#### SAPI

Windows 7 이상에서는 시스템의 언어 설정에서 언어의 음성 합성 팩을 추가하면 사용할 수 있습니다.

#### 자연 음성

Windows 10과 Windows 11에서는 Windows 자연 음성을 사용할 수 있습니다.

>[!WARNING]
>마이크로소프트가 최신 버전 언어 팩의 암호화 방법을 변경했기 때문에 시스템에 설치된 언어 팩과 다운로드한 최신 버전 언어 팩은 직접 사용할 수 없으며, 사용하려면 [이 글](https://www.bilibili.com/read/cv42198812/)을 참조하십시오.

Windows 11에서는 언어의 음성 합성 팩 외에도 `접근성`->`내레이터`->`자연 음성 추가`에서 더 높은 품질의 음성 팩을 추가할 수 있습니다.

Windows 10에서, 또는 시스템에 추가하고 싶지 않은 경우 [NVDA 중국 사이트](https://www.nvdacn.com/index.php/tts.html)에서 `Microsoft Natural Voice(자연 음성)`을 다운로드한 후 소프트웨어 디렉토리에 압축을 풀면 자연 음성을 사용할 수 있습니다.

Windows 10에서는 시스템에 필요한 런타임과 인식 모델이 부족하거나, Windows 11의 버전이 너무 낮아 시스템에 내장된 런타임 버전이 낮을 수 있습니다. 음성 팩을 다운로드하는 것 외에도 [자연 음성 런타임](https://lunatranslator.org/Resource/microsoft.cognitiveservices.speech)을 추가로 다운로드하여 소프트웨어 디렉토리에 압축을 풀어야 합니다.

== VoiceRoid2

자원 다운로드에서 관련 자원을 다운로드한 후 압축을 풀 경로를 선택하면 됩니다.

그러나 **추가 음원**의 경우 반드시 먼저 **통합 팩**을 다운로드한 후 통합 팩에 압축을 풀어야 사용할 수 있습니다. 통합 팩에는 비교적 인기 있는 음원과 필요한 런타임이 포함되어 있으며, 추가 음원만 다운로드하면 VoiceRoid2의 런타임이 부족할 수 있습니다.

== VOICEVOX

[VOICEVOX](https://github.com/VOICEVOX/voicevox/releases)를 다운로드하여 실행해야 합니다.

기본 포트 번호는 VOICEVOX의 기본 포트 번호와 동일합니다. 양쪽 설정을 수정하지 않으면 실행 후 활성화하면 사용할 수 있습니다.

== GPT-SoVITS

`API version`의 v2는 GPT-SoVITS의 API 인터페이스 버전이며 모델 버전이 아닙니다. 일반적으로 기본값인 v2를 사용하면 됩니다.

기타 매개변수에는 소량의 일반적으로 사용되는 매개변수만 추가되었습니다. 다른 매개변수가 필요한 경우 직접 추가하면 됩니다.

:::
