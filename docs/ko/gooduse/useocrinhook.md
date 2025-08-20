
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

# HOOK 모드에서 일시적으로 OCR 사용하기  

때로는 HOOK 모드에서 게임 메뉴, 선택지 등의 텍스트를 캡처하지 못하는 경우가 있습니다. 이럴 때 OCR 모드로 전환하여 인식한 후 다시 HOOK 모드로 돌아가는 것은 번거롭습니다.  

사실 이런 상황을 위한 내장 솔루션이 이미 존재합니다. "OCR 한 번 수행" 버튼 <i class="fa fa-crop"></i> 또는 단축키를 사용하는 방법입니다.  

이 버튼은 OCR 모드에서 인식 범위를 선택하는 버튼과 기본 아이콘이 동일하며, 현재는 이 버튼 사용이 기본적으로 활성화되어 있습니다.  

이 버튼으로 범위를 선택하면 OCR을 한 번만 수행한 후 OCR을 종료하고 HOOK 모드로 원활하게 돌아가 자동으로 텍스트를 추출합니다. 이를 통해 HOOK 모드의 일부 단점을 완벽하게 보완합니다.  

**이 버튼의 아이콘 때문에 원래 OCR을 사용하려던 많은 사용자들이 이 버튼을 OCR 버튼으로 오해하고 HOOK 모드 상태에서 이 버튼을 사용한 후 범위를 선택해도 자동 번역이 이루어지지 않는다는 것을 알게 됩니다. 실제로 OCR 모드로 전환하면 OCR 모드 버튼이 나타납니다.**  

고정 위치의 선택지에서 매번 범위를 선택하고 싶지 않은 경우 "OCR 다시 수행" 버튼 <i class="fa fa-spinner"></i> 또는 단축키를 사용하면 이전에 선택한 범위로 OCR을 수행할 수 있습니다.  
