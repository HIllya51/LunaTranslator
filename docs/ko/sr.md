# 음성 인식

Windows 10과 Windows 11에서는 Windows 음성 인식을 사용할 수 있습니다.

## 직접 호출 모드

이 모드는 Windows 음성 인식 모델을 직접 호출할 수 있으며 성능이 더 우수하고 Windows 10에서도 사용 가능합니다.

::: danger
**마이크로소프트가 최신 버전 언어 패키지의 암호화 방식을 변경했기 때문에, 시스템에 설치된 언어 패키지와 다운로드한 최신 버전 언어 패키지는 직접 사용할 수 없습니다. 사용하려면 [이 글](https://www.bilibili.com/read/cv42198812/)을 참조하세요.**
:::

Windows 11에서는 시스템에 설치된 언어 및 해당 음성 인식 모델을 직접 감지할 수 있습니다. `핵심 설정` -> `기타` -> `음성 인식`에서 인식할 언어를 선택하고 해당 기능을 활성화하면 사용을 시작할 수 있습니다. 인식하려는 언어가 옵션에 나타나지 않는 경우, 시스템에 해당 언어를 설치하거나 해당 언어의 인식 모델을 찾아 소프트웨어 디렉토리에 압축을 해제하세요.

Windows 10에서는 시스템에 필요한 런타임과 인식 모델이 부족할 수 있습니다. 또는 Windows 11의 버전이 너무 낮아 시스템에 포함된 런타임 버전이 낮을 수 있습니다. 먼저 제가 패키징한 [런타임 및 중/일/영어 음성 인식 모델](https://lunatranslator.org/Resource/DirectLiveCaptions.zip)을 다운로드하여 소프트웨어 디렉토리에 압축을 해제하면, 소프트웨어가 패키징된 런타임과 인식 모델을 인식하여 해당 기능을 사용할 수 있습니다.

다른 언어의 인식 모델이 필요한 경우, 해당 언어의 인식 모델을 직접 찾을 수 있습니다. 방법은 다음과 같습니다:
https://store.rg-adguard.net/ 에서 `PacakgeFamilyName`으로 `MicrosoftWindows.Speech.{LANGUAGE}.1_cw5n1h2txyewy`를 검색하세요. 여기서 `{LANGUAGE}`는 필요한 언어명입니다(예: 프랑스어는 `MicrosoftWindows.Speech.fr-FR.1_cw5n1h2txyewy`). 그런 다음 최신 버전의 msix를 다운로드하여 압축을 풀고 소프트웨어 디렉토리에 넣으면 됩니다.

::: details store.rg-adguard.net
![img](https://image.lunatranslator.org/zh/srpackage.png)
:::

## 간접 읽기 모드

이 모드는 **LiveCaptions** 창의 텍스트를 읽어 간접적으로 구현되며 Windows 11에서만 사용할 수 있습니다. 성능이 약간 떨어지지만 라이선스 및 런타임 호환성 문제가 없습니다.

Windows 11에서 이 모드를 활성화하고 전환하면 사용할 수 있습니다.
