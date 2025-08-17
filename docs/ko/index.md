---
# https://vitepress.dev/reference/default-theme-home-page
layout: home

hero:
  name: "LunaTranslator"
  # text: "Galgame 번역기, HOOK, OCR, 클립보드 등 지원"
  # tagline: 💡 빠른 번역으로 일본어를 쉽게 배우자!
  # image:
  #   src: /assets/bg.jpg
  #   alt: LunaTranslator
  actions:
    - theme: brand
      text: 다운로드 & 실행 & 업데이트
      link: ./README
    - theme: alt
      text: 기본 사용법
      link: ./basicuse
    - theme: alt
      text: Github
      link: https://github.com/HIllya51/LunaTranslator

features:
  - title: HOOK
    details: 주로 HOOK을 통해 게임 텍스트를 추출하며, 대부분의 유명/마이너 비주얼 노벨에 적용 가능
    link: ./hooksettings
  - title: 내장 번역
    details: 일부 게임은 번역을 게임 내에 직접 삽입하여 몰입형 경험 제공
    link: ./embedtranslate
  - title: HOOK 에뮬레이터
    details: NS/PSP/PSV/PS2의 대부분 게임 지원, HOOK 에뮬레이터로 직접 게임 텍스트 읽기 가능
    link: ./emugames
  - title: OCR
    details: 고정밀 OCR 모델 내장 및 다양한 온라인&오프라인 OCR 엔진 지원으로 유연한 텍스트 추출 가능
    link: ./useapis/ocrapi
  - title: 풍부한 번역 인터페이스
    details: 대언어모델 번역, 오프라인 번역 등 거의 모든 번역 엔진 지원
    link: ./useapis/guochandamoxing
  - title: 일본어 단어 분할 및 가나 주석 지원, AnkiConnect 지원, Yomitan 플러그인 지원
    link: ./qa1
  - title: 음성 합성
    details: 다양한 온라인&오프라인 음성 합성 엔진 지원
    link: ./ttsengines
  - title: 음성 인식
    details: Windows 10 및 Windows 11에서는 Windows 음성 인식 기능 사용 가능
    link: ./sr

