### [简体中文](README.md) | [English](README_en.md) | [繁體中文](README_cht.md) | 한국어 | [日本語](README_ja.md) | [Tiếng Việt](README_vi.md) | [Русский язык](README_ru.md)

# LunaTranslator [소프트웨어 다운로드](https://docs.lunatranslator.org/ko/README.html)  

> **비주얼 노벨 번역기**
 
### 사용 중 어려움이 있으면 [사용 설명서](https://docs.lunatranslator.org/ko)를 참고하거나 [Discord](https://discord.com/invite/ErtDwVeAbB)에 가입해 주세요.

## 기능 지원

#### 텍스트 입력

- **HOOK** HOOK 방식을 사용하여 텍스트를 추출할 수 있습니다. 일부 게임 엔진의 경우 [내장 번역](https://docs.lunatranslator.org/ko/embedtranslate.html)도 지원합니다. 또한 일부 [에뮬레이터](https://docs.lunatranslator.org/ko/emugames.html)에서 실행되는 게임의 텍스트 추출도 지원합니다. 지원되지 않거나 지원이 미흡한 게임은 [피드백 제출](https://github.com/HIllya51/LunaTranslator/issues/new?assignees=&labels=enhancement&projects=&template=01_game_request.yaml) 부탁드립니다.

- **OCR** **[오프라인 OCR](https://docs.lunatranslator.org/ko/useapis/ocrapi.html)** 및 **[온라인 OCR](https://docs.lunatranslator.org/ko/useapis/ocrapi.html)** 지원

- **클립보드** 클립보드에서 텍스트를 가져와 번역할 수 있으며, 추출한 텍스트를 클립보드로 출력할 수도 있습니다.

- **기타** **[음성 인식](https://docs.lunatranslator.org/ko/sr.html)** 및 **파일 번역**도 지원합니다.

#### 번역기

생각할 수 있는 거의 모든 번역 엔진을 지원합니다:

- **온라인 번역** 많은 즉시 사용 가능한 온라인 번역 인터페이스를 지원하며, 사용자가 등록한 API를 사용하는 **[전통 번역](https://docs.lunatranslator.org/ko/useapis/tsapi.html)** 및 **[대형 모델 번역](https://docs.lunatranslator.org/ko/guochandamoxing.html)**도 지원합니다.

- **오프라인 번역** 일반적인 **전통 번역** 엔진과 오프라인 배포된 **[대형 모델 번역](https://docs.lunatranslator.org/ko/offlinellm.html)**을 지원합니다.

- **사전 번역** 사전 번역 파일 읽기를 지원하며, 번역 캐시도 지원합니다.

- **사용자 정의 번역 확장** Python 언어를 사용하여 다른 번역 인터페이스를 확장할 수 있습니다.

#### 기타 기능

- **음성 합성** **오프라인 TTS** 및 **온라인 TTS** 지원

- **일본어 단어 분할 및 가나 표시** Mecab 등을 사용한 단어 분할 및 가나 표시 지원

- **단어 검색** **오프라인 사전** (MDICT) 및 **온라인 사전**을 사용한 단어 검색 지원

- **Anki** Anki에 단어를 한 번에 추가하는 기능 지원

- **브라우저 확장 프로그램 로드** 소프트웨어 내에서 Yomitan 등의 브라우저 확장 프로그램을 로드하여 다른 기능을 보조할 수 있습니다.

## 저자 지원

소프트웨어 유지보수는 쉽지 않습니다. 만약 이 소프트웨어가 도움이 되셨다면, [patreon](https://patreon.com/HIllya51)을 통해 저를 후원해 주세요. 여러분의 후원은 소프트웨어의 장기적인 유지보수에 큰 힘이 될 것입니다. 감사합니다~

<a href="https://patreon.com/HIllya51" target='_blank'><img width="200" src="../docs/become_a_patron_4x1_black_logo_white_text_on_coral.svg"></a>

## 오픈 소스 라이선스

LunaTranslator는 [GPLv3](../LICENSE) 라이선스를 사용합니다.
