# 다운로드 & 실행 & 업데이트

## 다운로드

| 운영 체제 | 64비트 |
| - | - |
| Windows 10 & 11 | <downloadbtn href="https://lunatranslator.org/Resource/DownloadLuna/x64_win10?doc=1"/> |

::: details 구형 운영체제 호환 버전  

>[!WARNING]  
이러한 버전은 성능이 더 낮고, 실행이 더 불안정하며, 일부 기능과 특징이 부족하고, 바이러스 백신 소프트웨어에 의해 오탐지되기 쉽습니다. 특별한 필요가 없는 경우 사용하지 않는 것이 좋습니다.

| 운영 체제 | 32비트 | 64비트 |
| - | - | - |
| Windows 7 이상 | <downloadbtn href="https://lunatranslator.org/Resource/DownloadLuna/x86_win7?doc=1"/> | <downloadbtn href="https://lunatranslator.org/Resource/DownloadLuna/x64_win7?doc=1"/> |
| Windows XP & Vista | <downloadbtn href="https://lunatranslator.org/Resource/DownloadLuna/x86_winxp?doc=1"/> | |

:::

## 실행

다운로드 후 임의의 디렉토리에 압축 해제

::: warning
하지만 소프트웨어를 **C:\Program Files** 등의 특수 경로에 두지 마십시오. 그렇지 않으면 관리자 권한을 사용하더라도 설정 및 캐시 파일을 저장할 수 없거나 실행조차 되지 않을 수 있습니다.
:::

**LunaTranslator.exe** 는 일반 모드로 실행됩니다. 

**LunaTranslator_admin.exe** 는 관리자 권한으로 실행되며, 일부 게임은 후킹을 위해 관리자 권한이 필요합니다. 이 경우에만 사용하고, 다른 경우에는 일반 모드로 실행하십시오.

**LunaTranslator_debug.bat** 은 커맨드 라인 창을 표시합니다.

## 업데이트

기본적으로 자동 업데이트가 수행됩니다. 자동 업데이트가 실패한 경우 수동으로 업데이트할 수 있습니다.

수동으로 업데이트하려면 새 버전을 다운로드한 후 이전 디렉토리에 덮어쓰기 해제하면 됩니다.

삭제 후 재다운로드하려면 userconfig 폴더를 삭제하지 마십시오. 그렇지 않으면 이전 설정이 모두 사라집니다!!!

## 일반적인 오류 {#anchor-commonerros}

### 중요 구성 요소를 찾을 수 없음

::: danger
때때로 바이러스 백신 프로그램에 의해 삭제될 수 있으니, 신뢰할 수 있는 항목으로 추가 후 다시 다운로드하여 압축 해제하십시오
:::

![img](https://image.lunatranslator.org/zh/cantstart/2.jpg) 

해결 방법: 바이러스 백신 프로그램을 종료하거나, 종료할 수 없는 경우(예: Windows Defender) 신뢰할 수 있는 항목에 추가한 후 다시 다운로드하십시오.

참고: 게임 텍스트를 HOOK 방식으로 추출하기 위해 Dll을 게임에 주입해야 합니다. shareddllproxy32.exe/LunaHost32.dll 등의 파일에서 이 내용이 구현되어 있어 특히 바이러스로 오인되기 쉽습니다. 본 소프트웨어는 현재 [Github Actions](https://github.com/HIllya51/LunaTranslator/actions)에서 자동 빌드되며, Github 서버가 감염되지 않는 한 바이러스를 포함할 가능성이 없으므로 안심하고 신뢰할 수 있는 항목에 추가하셔도 됩니다.

::: details Windows Defender의 경우 방법은 다음과 같습니다: "바이러스 및 위협 방지" -> "제외 항목" -> "제외 항목 추가 또는 제거" -> "제외 항목 추가" -> "폴더", Luna 폴더를 추가합니다
![img](https://image.lunatranslator.org/zh/cantstart/4.png) 
![img](https://image.lunatranslator.org/zh/cantstart/3.png) 
::: 

### Error/FileNotFoundError

미리 신뢰할 수 있는 항목을 추가하지 않으면, 소프트웨어 실행 중 일부 필수 구성 요소가 바이러스 백신 프로그램에 의해 삭제될 수 있습니다. 이후 HOOK 모드에서 프로세스를 선택한 후 이 오류가 발생할 수 있습니다. 해결 방법은 위와 동일합니다.

<img src="https://image.lunatranslator.org/zh/notfound.png" width=400>

### Error/PermissionError

소프트웨어가 `C:\Program Files` 등의 특수 폴더에 위치한 경우 정상적으로 작동하지 않을 수 있습니다.

<img src="https://image.lunatranslator.org/zh/cantstart/6.png" width=400>
