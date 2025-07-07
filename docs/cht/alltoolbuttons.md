# 工具按鈕

::: info
所有按鈕可以在`顯示設置`->`工具按鈕`中，進行隱藏或顯示。

所有按鈕均可以隨意調整位置。按鈕可以設置對齊組`居左` `居中` `居右`，對相對位置的調整都會被限定在對齊組中。

按鈕顏色可以在`顯示設置`->`界面設置`->`工具欄`->`按鈕顏色`中進行自定義。

部分按鈕有兩個圖標，用來指示兩種不同的狀態。部分按鈕僅有一個圖標，不過會用不同的顏色來表示不同的狀態
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

1. #### <i class="fa fa-rotate-right"></i> <i class="fa fa-icon fa-rotate-right"></i> 手動翻譯 {#anchor-retrans}
    實際意義是，從當前的文本輸入源，讀取一次輸入，並執行翻譯。
    
    例如如果當前是OCR模式，會再執行一次OCR。

1. #### <i class="fa fa-forward"></i> <i class="btnstatus2 fa fa-forward"></i> 自動翻譯 {#anchor-automodebutton}
    實際意義是，暫停/繼續自動從當前的文本輸入源讀取文本。

    例如如果當前是HOOK模式，會暫停讀取遊戲文本；當前是OCR模式，暫停自動識別圖像；如果當前是剪貼板模式，會暫停自動讀取剪貼板。

1. #### <i class="fa fa-gear"></i> <i class="fa fa-icon fa-rotate-right"></i> 打開設定 {#anchor-setting}
    略
1. #### <i class="fa fa-file"></i> <i class="fa fa-icon fa-rotate-right"></i> 讀取剪貼簿 {#anchor-copy_once}
    這個的實際意義是，不管當前的默認文本輸入源是什麼，都從剪貼板讀取一次文本，並傳給之後的翻譯/tts/...流程

    右擊按鈕會追加讀取到的文本到當前文本之後。
1. #### <i class="fa fa-futbol"></i> <i class="fa fa-icon fa-rotate-right"></i> 遊戲設定 {#anchor-open_game_setting}
    當使用HOOK模式連接到遊戲，或使用OCR模式綁定遊戲窗口後，則可以通過這個按鈕直接打開當前遊戲的設置窗口
1. #### <i class="fa fa-mouse-pointer"></i> <i class="btnstatus2 fa fa-mouse-pointer"></i> 滑鼠游標穿透視窗 {#anchor-mousetransbutton}
    激活這個按鈕後，鼠標點擊翻譯窗口時，翻譯窗口不會對鼠標點擊做出反應，而是把點擊事件傳遞給下層窗口。
    
    當把翻譯窗口置於遊戲窗口的文本框之上時，激活這個按鈕可以直接點擊遊戲的文本框而不是點擊到翻譯窗口上。
    
    當把鼠標移動到**鼠標穿透窗口按鈕及其左右一個按鈕的區域**時，會自動退出穿透以使用工具按鈕；移出區域時自動恢復穿透。

1. #### <i class="fa fa-lightbulb"></i> <i class="btnstatus2 fa fa-lightbulb"></i> 背景視窗透明 {#anchor-backtransbutton}
    該按鈕作用僅是一鍵使得翻譯窗口的不透明度切換到0。這個切換不會使得原版的不透明度設置被遺忘。
    
1. #### <i class="fa fa-lock"></i> <i class="btnstatus2 fa fa-unlock"></i> 鎖定工具列 {#anchor-locktoolsbutton}
    激活後工具欄將始終顯示。
    
    未鎖定工具欄時，當鼠標移出時，工具欄會自動隱藏，進入窗口後工具欄恢復顯示；如果是使用鼠標右鍵取消的鎖定工具欄，則僅當鼠標進入到**鎖定工具欄按鈕及其左右一個按鈕的區域**時，工具欄才恢復顯示。

    未鎖定工具欄時，如果激活了`鼠標穿透窗口`，則僅當鼠標移動到**鼠標穿透窗口按鈕及其左右一個按鈕的區域**時，工具欄才顯示；否則只要鼠標進入到翻譯窗口，工具就會顯示。

    如果當前使用了窗口特效(Aero/Arylic)，且不鎖定工具欄，則工具欄會處於文本區的z軸之上的區域，而非處於文本區的y軸上面。這是因爲由於Windows的原因，使用窗口特效時，如果將工具欄只是隱藏而非將縮去其窗口高度，則被隱藏的工具欄仍會被渲染亞力克/Aero背景，導致工具欄所在區域會有一塊空白。

1. #### <i class="fa fa-link"></i> <i class="fa fa-icon fa-rotate-right"></i> 選擇遊戲 {#anchor-selectgame}
    **該按鈕僅在HOOK模式下可用**
    
    點擊按鈕彈出選擇遊戲進程窗口，來選擇要HOOK的遊戲進程。
1. #### <i class="fa fa-tasks"></i> <i class="fa fa-icon fa-rotate-right"></i> 選擇文字 {#anchor-selecttext}
    **該按鈕僅在HOOK模式下可用**

    點擊按鈕彈出選擇遊戲文本窗口，來選擇要翻譯哪條HOOK到的文本。

    不過，選擇文本窗口在選擇進程後會自動彈出，這個按鈕實際上是用來更換選擇的文本，或修改一些設置用的。
1. #### <i class="fa fa-crop"></i> <i class="fa fa-icon fa-rotate-right"></i> 選取 OCR 範圍 {#anchor-selectocrrange}
    **該按鈕僅在OCR模式下可用**

    OCR模式下，選取OCR區域，或者更換OCR區域，或者當激活`OCR設置`->`其他`->`多重區域模式`時增加新的OCR區域

    當按下右鍵時，會先清除所有已選取範圍，再添加新的區域。
1. #### <i class="fa fa-square"></i> <i class="fa fa-icon fa-rotate-right"></i> 顯示／隱藏範圍框 {#anchor-hideocrrange}
    **該按鈕僅在OCR模式下可用**

    當未選擇任何OCR範圍時，使用該按鈕顯示OCR範圍，會自動設置OCR範圍爲上一次選擇的OCR。

    當按下右鍵時，會清除所有已選取範圍
1. #### <i class="fa fa-crop"></i> <i class="fa fa-icon fa-rotate-right"></i> 進行一次 OCR {#anchor-ocr_once}
    該按鈕和`讀取剪貼板`類似，不管當前的默認文本輸入源是什麼，都會先進行OCR範圍選擇，然後進行一次OCR，然後進行翻譯流程。

    該按鈕一般用於，在HOOK模式下，遇到選擇支時，臨時使用一次OCR進行翻譯選擇支。或者在OCR模式下，臨時去識別一次其他偶爾出現的新的位置。

1. #### <i class="fa fa-spinner"></i> <i class="fa fa-icon fa-rotate-right"></i> 再次進行 OCR {#anchor-ocr_once_follow}
    當使用過一次`進行一次OCR`後，使用這個按鈕，可以在原來的位置上再次進行一次OCR而無需重新選擇識別區域。
    
1. #### <i class="fa fa-book"></i> <i class="fa fa-icon fa-rotate-right"></i> 專有名詞翻譯 翻譯前替換 {#anchor-noundict_direct}
1. #### <i class="fa fa-book"></i> <i class="fa fa-icon fa-rotate-right"></i> 專有名詞翻譯 {#anchor-noundict}
1. #### <i class="fa fa-won"></i> <i class="fa fa-icon fa-rotate-right"></i> 翻譯結果修正 {#anchor-fix}
    以上三個按鈕，效果類似，是用來快捷打開翻譯優化的設置窗口，增加新的指定詞條的。

    鼠標左鍵點擊時，當有綁定的遊戲(HOOK鏈接遊戲/剪貼板、OCR綁定窗口)時，打開遊戲的專用詞典設置，否則則是打開全局的詞典設置。

    鼠標右鍵點擊時，必然打開全局的詞典設置。
1. #### <i class="fa fa-minus"></i> <i class="fa fa-icon fa-rotate-right"></i> 最小化到系統匣 {#anchor-minmize}
    略
1. #### <i class="fa fa-times"></i> <i class="fa fa-icon fa-rotate-right"></i> 退出 {#anchor-quit}
    略
1. #### <i class="fa fa-hand-paper"></i> <i class="fa fa-icon fa-rotate-right"></i> 移動 {#anchor-move}
    拖動翻譯窗口。

    實際上當按鈕欄有沒有按鈕存在的額外空白區域時，都可以隨意拖動。該按鈕僅用來預留一個拖動位置。
1. #### <i class="fa fa-compress"></i> <i class="fa fa-expand"></i> 視窗縮放 {#anchor-fullscreen}
    可以一鍵對遊戲窗口使用內置的Magpie進行縮放。

    左鍵爲窗口化縮放，右鍵爲全屏縮放。

1. #### <i class="fa fa-camera"></i> <i class="fa fa-icon fa-rotate-right"></i> 視窗截圖 {#anchor-grabwindow}
    可以對綁定的窗口進行截圖，（默認會截兩張圖，GDI和Winrt，兩者均有一定概率會失敗）。最好的地方是，如果當前正在使用Magpie進行縮放，還會對放大的窗口進行截圖。

    左鍵點擊時會把截圖保存到文件，右鍵點擊時截圖會保存到剪貼板。
1. #### <i class="fa fa-volume-off"></i> <i class="btnstatus2 fa fa-volume-up"></i> 遊戲靜音 {#anchor-muteprocess}
    當綁定遊戲窗口後（不只是hook模式，ocr或剪貼板模式都可以，只要綁定了遊戲窗口），可以一鍵對遊戲進行靜音，省去了在系統音量合成器進行遊戲靜音的麻煩。
1. #### <i class="fa fa-eye"></i> <i class="btnstatus2 fa fa-eye-slash"></i> 顯示／隱藏原文 {#anchor-showraw}
    切換是否顯示原文，會立即生效。

1. #### <i class="fa fa-toggle-on"></i> <i class="btnstatus2 fa fa-toggle-off"></i> 顯示／隱藏翻譯 {#anchor-showtrans}
    切換是否使用翻譯，系翻譯的總開關，關閉後將不會進行任何翻譯。

    如果已經進行過了翻譯，則關閉後將會隱藏翻譯結果，並再重新打開時重新顯示本次的翻譯結果。

    如果未進行過翻譯，並從隱藏切換到顯示，則會觸發對當前句子的翻譯。

1. #### <i class="fa fa-music"></i> <i class="fa fa-icon fa-rotate-right"></i> 朗讀 {#anchor-langdu}
    左擊按鈕會對當前文本進行語音合成。

    右擊該按鈕會中斷朗讀。

    該朗讀會無視`跳過`（如果在`語音指定`中，匹配當前文本目標爲`跳過`，則使用按鈕進行朗讀時，會無視跳過，強制進行朗讀）
1. #### <i class="fa fa-copy"></i> <i class="fa fa-icon fa-rotate-right"></i> 複製到剪貼簿 {#anchor-copy}
    複製當前提取到的文本到剪貼板一次。如果想要自動提取到剪貼板，應當激活`文本輸入`->`剪貼板`->`自動輸出`->`自動輸出文本`。
1. #### <i class="fa fa-rotate-left"></i> <i class="fa fa-icon fa-rotate-right"></i> 顯示／隱藏歷史文字 {#anchor-history}
    打開或關閉歷史文本的窗口。
1. #### <i class="fa fa-gamepad"></i> <i class="fa fa-icon fa-rotate-right"></i> 遊戲管理 {#anchor-gamepad_new}
    打開遊戲管理器界面。
1. #### <i class="fa fa-edit"></i> <i class="fa fa-icon fa-rotate-right"></i> 編輯 {#anchor-edit}
    打開編輯窗口，運行編輯當前提取到的文本。

    該窗口中，可以運行修改文本後，再去進行翻譯；或者可以翻譯任何自行輸入的文本。
1. #### <i class="fa fa-edit"></i> <i class="fa fa-icon fa-rotate-right"></i> 編輯 翻譯紀錄 {#anchor-edittrans}
    打開當前遊戲的翻譯記錄編輯窗口
1. #### <i class="fa fa-download"></i> <i class="fa fa-icon fa-rotate-right"></i> 模擬按鍵 Ctrl {#anchor-simulate_key_ctrl}
1. #### <i class="fa fa-download"></i> <i class="fa fa-icon fa-rotate-right"></i> 模擬按鍵 Enter {#anchor-simulate_key_enter}
    同上，用於向遊戲窗口發送一次模擬按鍵。對於使用串流/平板時，有些作用。
1. #### <i class="fa fa-list-ul"></i> <i class="fa fa-icon fa-rotate-right"></i> 備忘錄 {#anchor-memory}
    對於當前正在玩的遊戲，打開備忘錄窗口。
    
    點擊左鍵時，打開當前遊戲的備忘錄。點擊右鍵時，打開全局的備忘錄。
1. #### <i class="fab fa-windows"></i> <i class="btnstatus2 fab fa-windows"></i> 綁定視窗 （點擊自己取消） {#anchor-bindwindow}
    **該按鈕非常重要，許多功能都依賴於該按鈕先進行設置後纔可用**

    在綁定了遊戲窗口後，`窗口縮放` `窗口截圖` `遊戲靜音`，`跟隨遊戲窗口`->`遊戲失去焦點時取消置頂`和`遊戲窗口移動時同步移動`，以及記錄遊戲時間等，纔可用。
    不論HOOK/OCR/剪貼板模式，該按鈕都可用。

    在HOOK模式下，會自動根據連接的遊戲，自動綁定遊戲窗口。但也可以在用該按鈕重新選擇其他窗口。

    在OCR模式下，綁定窗口後，還額外允許遊戲窗口移動時，同步自動移動OCR區域和範圍框。
    在OCR/剪貼板模型下，綁定窗口後，也可以和HOOK模式下一樣，關聯到當前遊戲到遊戲設置，從而使用當前遊戲的專有翻譯優化詞典等。

1. #### <i class="fa fa-neuter"></i> <i class="btnstatus2 fa fa-neuter"></i> 視窗置頂 {#anchor-keepontop}
    取消/置頂翻譯窗口

1. #### <i class="fa fa-i-cursor"></i> <i class="btnstatus2 fa fa-i-cursor"></i> 可選取的 {#anchor-selectable}
    使得翻譯窗的文本區中的文本，是可以進行選擇的。

    如果激活時點擊的是鼠標右鍵，則會禁止拖拽非文本區域以移動窗口。

1. #### <i class="fa fa-search"></i> <i class="fa fa-icon fa-rotate-right"></i> 查詞 {#anchor-searchwordW}
    如果當前有文本被選取，則會查詢選取的文本並打開查詞窗口。否則只是打開或關閉查詞窗口。
  