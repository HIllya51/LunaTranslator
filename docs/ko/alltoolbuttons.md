# 도구 버튼

::: info
모든 버튼은 `표시 설정`->`도구 버튼`에서 숨기거나 표시할 수 있습니다.

모든 버튼은 자유롭게 위치를 조정할 수 있습니다. 버튼은 정렬 그룹 `좌측` `중앙` `우측`을 설정할 수 있으며, 상대적 위치 조정은 정렬 그룹 내에서 제한됩니다.

버튼 색상은 '색상'을 클릭하여 사용자 정의할 수 있습니다.

버튼 아이콘은 '아이콘'을 클릭하여 사용자 정의할 수 있습니다.

일부 버튼에는 두 가지 상태를 나타내는 두 개의 아이콘이 있습니다. 일부 버튼에는 하나의 아이콘만 있지만 다른 색상으로 다른 상태를 표시합니다.
:::

<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.6.0/css/all.min.css">


<style>
    i{
        color:blue;
        width:20px;
    }
    .fa-icon {
  visibility: hidden;
}
.btnstatus2{
    color:deeppink;
}
</style>

1. #### <i class="fa fa-rotate-right"></i> <i class="fa fa-icon fa-rotate-right"></i> 수동 실행 {#anchor-retrans}
    실제 의미는 현재의 텍스트 입력 소스에서 입력을 한 번 읽고 번역을 실행하는 것입니다.

    예를 들어 현재 OCR 모드인 경우, OCR을 다시 한 번 실행합니다.

1. #### <i class="fa fa-forward"></i> <i class="btnstatus2 fa fa-forward"></i> 자동 모드 {#anchor-automodebutton}
    실제 의미는 현재의 텍스트 입력 소스에서 자동으로 텍스트를 읽는 것을 일시 중지/재개하는 것입니다.

    예를 들어 현재 HOOK 모드인 경우 게임 텍스트 읽기를 일시 중지합니다; 현재 OCR 모드인 경우 이미지 자동 인식을 일시 중지합니다; 현재 클립보드 모드인 경우 클립보드 자동 읽기를 일시 중지합니다.

1. #### <i class="fa fa-gear"></i> <i class="fa fa-icon fa-rotate-right"></i> 설정 열기 {#anchor-setting}
    생략
1. #### <i class="fa fa-file"></i> <i class="fa fa-icon fa-rotate-right"></i> 클립보드 읽기 {#anchor-copy_once}
    이것의 실제 의미는 현재 기본 텍스트 입력 소스가 무엇이든 클립보드에서 텍스트를 한 번 읽어 온 후 번역/TTS/… 등의 프로세스로 전달한다는 것입니다.

    버튼을 우클릭하면 읽어온 텍스트를 현재 텍스트 뒤에 추가합니다.
1. #### <i class="fa fa-futbol"></i> <i class="fa fa-icon fa-rotate-right"></i> 게임 설정 {#anchor-open_game_setting}
    HOOK 모드로 게임에 연결하거나 OCR 모드로 게임 창을 바인딩한 경우, 이 버튼을 통해 현재 게임의 설정 창을 직접 열 수 있습니다.
1. #### <i class="fa fa-mouse-pointer"></i> <i class="btnstatus2 fa fa-mouse-pointer"></i> 마우스 윈도우 투과 {#anchor-mousetransbutton}
    이 버튼을 활성화하면 번역 창을 클릭할 때 번역 창이 마우스 클릭에 반응하지 않고 클릭 이벤트를 하위 창으로 전달합니다.

    번역 창을 게임 창의 텍스트 상자 위에 위치시켰을 때, 이 버튼을 활성화하면 번역 창이 아닌 게임의 텍스트 상자를 직접 클릭할 수 있습니다.

    마우스를 **마우스 창 투과 버튼 및 그 좌우 한 버튼 영역**으로 이동하면 자동으로 투과 모드를 해제하여 도구 버튼을 사용할 수 있으며, 영역 밖으로 이동하면 자동으로 투과 모드가 복구됩니다.

1. #### <i class="fa fa-lightbulb"></i> <i class="btnstatus2 fa fa-lightbulb"></i> 창 배경 투명 {#anchor-backtransbutton}
    이 버튼은 번역 창의 불투명도를 0으로 전환하는 기능만 수행합니다. 이 전환은 원래의 불투명도 설정을 잊어버리게 하지 않습니다.

1. #### <i class="fa fa-lock"></i> <i class="btnstatus2 fa fa-unlock"></i> 툴바 잠금 {#anchor-locktoolsbutton}
    활성화 시 도구 모음이 항상 표시됩니다.

    도구 모음이 잠금 해제된 상태에서 마우스가 창 밖으로 이동하면 도구 모음이 자동으로 숨겨지며, 창 안으로 마우스가 들어오면 도구 모음이 다시 표시됩니다. 만약 마우스 오른쪽 버튼으로 도구 모음 잠금을 해제한 경우, **잠금 버튼 및 그 좌우 한 개의 버튼 영역**으로 마우스가 들어올 때만 도구 모음이 다시 표시됩니다.

    도구 모음이 잠금 해제된 상태에서 `마우스 창 투과`가 활성화된 경우, **마우스 창 투과 버튼 및 그 좌우 한 개의 버튼 영역**으로 마우스가 이동할 때만 도구 모음이 표시됩니다. 그렇지 않으면 마우스가 번역 창 안으로 들어오기만 하면 도구 모음이 표시됩니다.

    현재 창 효과(Aero/아크릴)를 사용 중이고 도구 모음을 잠그지 않은 경우, 도구 모음은 텍스트 영역의 z축 위쪽 영역에 위치하게 됩니다. 이는 Windows의 특성상 창 효과 사용 시 도구 모음을 단순히 숨기고 창 높이를 줄이지 않으면 숨겨진 도구 모음이 아크릴/Aero 배경으로 계속 렌더링되어 도구 모음 영역에 공백이 생기기 때문입니다.

1. #### <i class="fa fa-link"></i> <i class="fa fa-icon fa-rotate-right"></i> 게임 선택 {#anchor-selectgame}
    **이 버튼은 HOOK 모드에서만 사용 가능**

    버튼을 클릭하면 게임 프로세스 선택 창이 나타나며, HOOK할 게임 프로세스를 선택할 수 있습니다.
1. #### <i class="fa fa-tasks"></i> <i class="fa fa-icon fa-rotate-right"></i> 텍스트 선택 {#anchor-selecttext}
    **이 버튼은 HOOK 모드에서만 사용 가능**

    버튼을 클릭하면 게임 텍스트 선택 창이 나타나며, 번역할 HOOK된 텍스트를 선택할 수 있습니다.

    다만, 프로세스 선택 후 텍스트 선택 창이 자동으로 나타나며, 이 버튼은 실제로 선택한 텍스트를 변경하거나 일부 설정을 수정하는 데 사용됩니다.
1. #### <i class="fa fa-crop"></i> <i class="fa fa-icon fa-rotate-right"></i> OCR 범위 선택 {#anchor-selectocrrange}
    **이 버튼은 OCR 모드에서만 사용 가능**

    OCR 모드에서 OCR 영역을 선택하거나 변경하거나, `OCR 설정`->`기타`->`다중 영역 모드`가 활성화된 경우 새로운 OCR 영역을 추가할 수 있습니다.

    오른쪽 버튼을 누르면 모든 선택된 범위가 먼저 지워진 후 새로운 영역이 추가됩니다.
1. #### <i class="fa fa-square"></i> <i class="fa fa-icon fa-rotate-right"></i> 범위 프레임 표시/숨기기 {#anchor-hideocrrange}
    **이 버튼은 OCR 모드에서만 사용 가능**

    OCR 범위를 선택하지 않은 상태에서 이 버튼을 사용하면 OCR 범위가 표시되며, 자동으로 마지막으로 선택한 OCR 범위로 설정됩니다.

    오른쪽 버튼을 누르면 모든 선택된 범위가 지워집니다.
1. #### <i class="fa fa-crop"></i> <i class="fa fa-icon fa-rotate-right"></i> OCR 실행 {#anchor-ocr_once}
    이 버튼은 '클립보드 읽기'와 유사하며, 현재의 기본 텍스트 입력 소스와 관계없이 먼저 OCR 범위를 선택하고 OCR을 실행한 후 번역 프로세스를 진행합니다.

    이 버튼은 일반적으로 HOOK 모드에서 선택지가 나타났을 때 일시적으로 OCR을 사용해 선택지를 번역하거나, OCR 모드에서 가끔 나타나는 새로운 위치를 일시적으로 인식할 때 사용합니다.

1. #### <i class="fa fa-spinner"></i> <i class="fa fa-icon fa-rotate-right"></i> OCR 다시 실행 {#anchor-ocr_once_follow}
    'OCR 실행하기'를 한 번 사용한 후, 이 버튼을 사용하면 인식 영역을 다시 선택하지 않고도 원래 위치에서 OCR을 다시 실행할 수 있습니다.

1. #### <i class="fa fa-book"></i> <i class="fa fa-icon fa-rotate-right"></i> 번역 전 대체 {#anchor-noundict_direct}
1. #### <i class="fa fa-book"></i> <i class="fa fa-icon fa-rotate-right"></i> 고유 명사 번역 {#anchor-noundict}
1. #### <i class="fa fa-won"></i> <i class="fa fa-icon fa-rotate-right"></i> 번역 결과 수정 {#anchor-fix}
    위의 세 버튼은 효과가 유사하며, 번역 최적화 설정 창을 빠르게 열어 새로운 지정 항목을 추가하는 데 사용됩니다.

    마우스 왼쪽 버튼으로 클릭할 때, 연결된 게임(HOOK 연결 게임/클립보드, OCR 연결 창)이 있으면 해당 게임의 전용 사전 설정을 열고, 그렇지 않으면 전역 사전 설정을 엽니다.

    마우스 오른쪽 버튼을 클릭하면 반드시 전역 사전 설정이 열립니다.
1. #### <i class="fa fa-minus"></i> <i class="fa fa-icon fa-rotate-right"></i> 트레이로 최소화 {#anchor-minmize}
    생략
1. #### <i class="fa fa-times"></i> <i class="fa fa-icon fa-rotate-right"></i> 종료 {#anchor-quit}
    생략
1. #### <i class="fa fa-hand-paper"></i> <i class="fa fa-icon fa-rotate-right"></i> 이동 {#anchor-move}
    번역 창을 드래그합니다.

    실제로 버튼 바에 버튼이 없는 추가 빈 공간이 있을 경우, 자유롭게 드래그할 수 있습니다. 이 버튼은 드래그 위치를 예약하기 위한 용도입니다.
1. #### <i class="fa fa-compress"></i> <i class="fa fa-expand"></i> 창 확대/축소 {#anchor-fullscreen}
    게임 창에 내장된 Magpie를 사용하여 한 번의 클릭으로 크기 조절이 가능합니다.

    왼쪽 버튼은 창 모드 조절, 오른쪽 버튼은 전체 화면 조절입니다.

1. #### <i class="fa fa-camera"></i> <i class="fa fa-icon fa-rotate-right"></i> 창 스크린샷 {#anchor-grabwindow}
    바인딩된 창의 스크린샷을 찍을 수 있습니다 (기본적으로 GDI와 Winrt 방식으로 각각 한 장씩 총 두 장을 찍으며, 둘 다 실패할 가능성이 있습니다). 가장 좋은 점은 현재 Magpie로 확대 중인 창일 경우, 확대된 창의 스크린샷도 찍을 수 있다는 것입니다.

    왼쪽 버튼 클릭 시 스크린샷을 파일로 저장하고, 오른쪽 버튼 클릭 시 스크린샷을 클립보드에 저장합니다.
1. #### <i class="fa fa-volume-off"></i> <i class="btnstatus2 fa fa-volume-up"></i> 게임 음소거 {#anchor-muteprocess}
    게임 창을 바인딩한 후, 게임 음소거를 한 번의 클릭으로 수행할 수 있어 시스템 볼륨 믹서에서 게임 음소거를 하는 번거로움을 덜 수 있습니다.
1. #### <i class="fa fa-eye"></i> <i class="btnstatus2 fa fa-eye-slash"></i> 원문 표시/숨기기 {#anchor-showraw}
    원문 표시 여부를 전환하면 즉시 적용됩니다.

1. #### <i class="fa fa-toggle-on"></i> <i class="btnstatus2 fa fa-toggle-off"></i> 번역 표시/숨기기 {#anchor-showtrans}
    번역 사용 여부를 전환하는 것으로, 번역의 총괄 스위치 역할을 하며, 끄면 어떠한 번역도 수행되지 않습니다.

    이미 번역이 수행된 경우, 끄면 번역 결과가 숨겨지고 다시 열면 이번 번역 결과가 다시 표시됩니다.

    번역이 수행되지 않은 상태에서 숨김에서 표시로 전환하면 현재 문장에 대한 번역이 트리거됩니다.

1. #### <i class="fa fa-music"></i> <i class="fa fa-icon fa-rotate-right"></i> 음성 읽기 {#anchor-langdu}
    왼쪽 클릭으로 현재 텍스트에 대한 음성 합성이 수행됩니다.

    오른쪽 클릭으로 재생이 중단됩니다.

    이 음성 재생은 '건너뛰기'를 무시합니다(`음성 지정`에서 현재 텍스트 대상이 '건너뛰기'로 매칭된 경우에도, 버튼을 사용하여 재생하면 건너뛰기를 무시하고 강제로 재생합니다).
1. #### <i class="fa fa-copy"></i> <i class="fa fa-icon fa-rotate-right"></i> 클립보드에 복사 {#anchor-copy}
    현재 추출된 텍스트를 클립보드에 한 번 복사합니다. 자동으로 클립보드에 추출하려면 `텍스트 입력`->`클립보드`->`자동 출력`->`텍스트 자동 출력`을 활성화해야 합니다.
1. #### <i class="fa fa-history"></i> <i class="fa fa-icon fa-rotate-right"></i> 기록 텍스트 표시/숨기기 {#anchor-history}
    기록 텍스트 창을 열거나 닫습니다.
1. #### <i class="fa fa-gamepad"></i> <i class="fa fa-icon fa-rotate-right"></i> 게임 관리 {#anchor-gamepad_new}
    게임 관리자 인터페이스를 엽니다.
1. #### <i class="fa fa-edit"></i> <i class="fa fa-icon fa-rotate-right"></i> 편집 {#anchor-edit}
    편집 창을 열어 현재 추출된 텍스트를 편집합니다.

    이 창에서 텍스트를 수정한 후 번역할 수 있으며, 직접 입력한 텍스트도 번역할 수 있습니다.
1. #### <i class="fa fa-edit"></i> <i class="fa fa-icon fa-rotate-right"></i> 편집 번역 기록 {#anchor-edittrans}
    현재 게임의 번역 기록 편집 창을 엽니다.
1. #### <i class="fa fa-download"></i> <i class="fa fa-icon fa-rotate-right"></i> Ctrl 키 시뮬레이션 {#anchor-simulate_key_ctrl}
1. #### <i class="fa fa-download"></i> <i class="fa fa-icon fa-rotate-right"></i> Enter 키 시뮬레이션 {#anchor-simulate_key_enter}
    위와 동일하며, 게임 창에 시뮬레이션 키를 한 번 전송합니다. 스트리밍/태블릿 사용 시 유용합니다.
1. #### <i class="fa fa-list-ul"></i> <i class="fa fa-icon fa-rotate-right"></i> 메모 {#anchor-memory}
    현재 플레이 중인 게임에 대해 메모 창을 엽니다.

    왼쪽 클릭 시 현재 게임의 메모를 엽니다. 오른쪽 클릭 시 전역 메모를 엽니다.
1. #### <i class="fab fa-windows"></i> <i class="btnstatus2 fab fa-windows"></i> 창 바인딩 (클릭하여 취소) {#anchor-bindwindow}
    **이 버튼은 매우 중요하며, 많은 기능들이 이 버튼을 먼저 설정해야 사용 가능합니다**

    게임 창을 바인딩한 후에야 `창 크기 조절` `창 스크린샷` `게임 음소거`, `게임 창 따라가기`->`게임이 포커스를 잃을 때 항상 위 취소`와 `게임 창 이동 시 동기화 이동`, 그리고 게임 시간 기록 등이 사용 가능해집니다.
    HOOK/OCR/클립보드 모드 모두 이 버튼을 사용할 수 있습니다.

    HOOK 모드에서는 연결된 게임에 따라 자동으로 게임 창을 바인딩합니다. 하지만 이 버튼으로 다른 창을 다시 선택할 수도 있습니다.

    OCR 모드에서는 창 바인딩 후, 게임 창이 이동할 때 OCR 영역과 범위 박스도 자동으로 동기화 이동이 추가로 허용됩니다.
    OCR/클립보드 모드에서도 창 바인딩 후 HOOK 모드와 마찬가지로 현재 게임을 게임 설정에 연동하여 해당 게임 전용 번역 최적화 사전 등을 사용할 수 있습니다.

1. #### <i class="fa fa-neuter"></i> <i class="btnstatus2 fa fa-neuter"></i> 창 항상 위에 표시 {#anchor-keepontop}
    번역 창 항상 위 설정/해제

1. #### <i class="fa fa-i-cursor"></i> <i class="btnstatus2 fa fa-i-cursor"></i> 선택 가능한 {#anchor-selectable}
    번역 창의 텍스트 영역에 있는 텍스트를 선택할 수 있도록 합니다.

    활성화 시 마우스 오른쪽 버튼으로 클릭하면, 비텍스트 영역을 드래그하여 창을 이동하는 것이 금지됩니다.

1. #### <i class="fa fa-search"></i> <i class="fa fa-icon fa-rotate-right"></i> 단어 검색 {#anchor-searchwordW}
    현재 선택된 텍스트가 있으면 해당 텍스트를 검색하여 단어 검색 창을 엽니다. 그렇지 않으면 단어 검색 창을 열거나 닫기만 합니다.

1. #### <i class="fa fa-refresh"></i> 번역 상태 재설정 {#anchor-reset_TS_status}
    번역 상태를 재설정하며, 주로 증가하는 대규모 모델 번역需求에 대응하여 저장된 컨텍스트 및 기타 정보를 삭제할 수 있습니다.