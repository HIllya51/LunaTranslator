# Textractor

![How it looks](screenshot.png)

[English](README.md) ● [Español](README_ES.md) ● [简体中文](README_SC.md) ● [Русский](README_RU.md) ● [한국어](README_KR.md) ● [ภาษาไทย](README_TH.md) ● [Français](README_FR.md) ● [Italiano](README_IT.md) ● [日本語](README_JP.md) ● [Bahasa Indonesia](README_ID.md) ● [Português](README_PT.md)

**Textractor** (a.k.a. NextHooker)는 Windows/Wine에서 작동하는 [ITHVNR](https://web.archive.org/web/20160202084144/http://www.hongfire.com/forum/showthread.php/438331-ITHVNR-ITH-with-the-VNR-engine)을 기반으로 한 오픈소스 x86/x64 비디오게임 텍스트 후커 입니다.<br>
빠른 사용법의 이해를 위해 [tutorial video](docs/TUTORIAL.md) 를 참고하세요.

## 다운로드

[여기](https://github.com/Artikash/Textractor/releases)에서 Textractor 최신버전을 받으실 수 있습니다.<br>
최신버전의 ITHVNR은 [여기](https://drive.google.com/open?id=13aHF4uIXWn-3YML_k2YCDWhtGgn5-tnO)서 받을 수 있습니다.

## 특징

- 높은 확장성과 커스터마이즈
- 많은 게임엔진의 자동 후킹이 가능 (몇몇의 VNR로 후킹 불가능한 경우도 포함)
- /H "hook" 코드를 통한 후킹 (많은 AGTH 코드가 지원됨)
- /R "read" 코드를 통해 직접적으로 텍스트 추출이 가능

## 지원

버그나, 후킹에 문제가 있는 게임이나, 기능요청 혹은 제안들을 알려주시기 바랍니다.<br>
특정 게임의 문제해결을 위하여 해당게임을 무료로 받을 수 있는 링크나 [Steam](https://steamcommunity.com/profiles/76561198097566313/)을 통한 제공을 받고 있습니다.

## 확장기능

어떻게 확장기능을 만드는지 [Example Extension project](https://github.com/Artikash/ExampleExtension) 을 확인해 보시기 바랍니다.<br>
확장기능 폴더를 확인해 확장기능들이 어떤 역할들을 하는지 알아보세요.

## 기여

모든 기여자들에게 감사하고 있습니다! 코드베이스에 궁금한 점이 있다면 akashmozumdar@gmail.com 에 이메일 해 주시기 바랍니다.

## 컴파일링

*Textractor*를 컴파일링 하기 전에, Qt version 5.13과 CMake를 포함한 Visual Studio가 있어야 합니다.<br>
그 이후로는, 단순히 Visual Studio를 통해 폴더를 열고 빌드하는 것으로 실행이 가능합니다.

## 프로젝트 아키텍쳐

The host (see host folder) injects texthook.dll (created from the texthook folder) into the target process and connects to it via 2 pipe files.<br>
Host writes to hostPipe, texthook writes to hookPipe.<br>
texthook waits for the pipe to be connected, then injects a few instructions into any text outputting functions (e.g. TextOut, GetGlyphOutline) that cause their input to be sent through the pipe.<br>
Additional information about hooks is exchanged via shared memory.<br>
The text that the host receives through the pipe is then processed a little before being dispatched back to the GUI.<br>
Finally, the GUI dispatches the text to extensions before displaying it.

## [개발자들](docs/CREDITS.md)
