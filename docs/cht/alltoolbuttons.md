# 工具按鈕

::: info
所有按鈕可以在`顯示設定`->`工具按鈕`中，進行隱藏或顯示。

所有按鈕均可以隨意調整位置。按鈕可以設定對齊分組`置左` `置中` `置右`，對相對位置的調整都會被限定在對齊分組中。

按鈕顏色可以點擊「顏色」進行自定義。

按鈕圖標可以點擊「圖標」進行自定義。

部份按鈕有兩個圖示，用來表示兩種不同的狀態。部份按鈕僅有一個圖示，不過會用不同的顏色來表示不同的狀態
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

1. #### <i class="fa fa-rotate-right"></i> <i class="fa fa-icon fa-rotate-right"></i> 手動執行 {#anchor-retrans}
    實際意義是，從目前的文字輸入來源，讀取一次輸入，並執行翻譯。

    例如如果目前是 OCR 模式，會再執行一次 OCR。

1. #### <i class="fa fa-forward"></i> <i class="btnstatus2 fa fa-forward"></i> 自動模式 {#anchor-automodebutton}
    實際意義是，暫停／繼續自動從目前的文字輸入來源讀取文字。

    例如如果目前是 HOOK 模式，會暫停讀取遊戲文字；目前是 OCR 模式，暫停自動辨識圖像；如果目前是剪貼簿模式，會暫停自動讀取剪貼簿。

1. #### <i class="fa fa-gear"></i> <i class="fa fa-icon fa-rotate-right"></i> 開啟設定 {#anchor-setting}
    開啟或關閉程式的設定視窗。

1. #### <i class="fa fa-file"></i> <i class="fa fa-icon fa-rotate-right"></i> 讀取剪貼簿 {#anchor-copy_once}
    這個的實際意義是，不管目前的預設文字輸入來源是什麼，都從剪貼簿讀取一次文字，並傳給之後的翻譯／TTS／…流程。

    右鍵點擊按鈕會追加讀取到的文字到目前文字之後。

1. #### <i class="fa fa-futbol"></i> <i class="fa fa-icon fa-rotate-right"></i> 遊戲設定 {#anchor-open_game_setting}
    當使用 HOOK 模式連接到遊戲，或使用 OCR 模式綁定遊戲視窗後，則可以透過這個按鈕直接開啟目前遊戲的設定視窗。

1. #### <i class="fa fa-mouse-pointer"></i> <i class="btnstatus2 fa fa-mouse-pointer"></i> 滑鼠游標穿透視窗 {#anchor-mousetransbutton}
    啟用這個按鈕後，滑鼠點擊翻譯視窗時，翻譯視窗不會對滑鼠點擊做出反應，而是把點擊事件傳遞給下層視窗。

    當把翻譯視窗置於遊戲視窗的文字框之上時，啟用這個按鈕可以直接點擊遊戲的文字框而不是點擊到翻譯視窗上。

    當把滑鼠游標移動到**滑鼠游標穿透視窗按鈕及其左右一個按鈕的區域**時，會自動退出穿透狀態以使用工具按鈕；移出區域時自動恢復穿透狀態。

1. #### <i class="fa fa-lightbulb"></i> <i class="btnstatus2 fa fa-lightbulb"></i> 窗口背景透明 {#anchor-backtransbutton}
    該按鈕作用僅是一鍵使得翻譯視窗的不透明度切換到 0。這個切換不會使得原本的不透明度設定被遺忘。

1. #### <i class="fa fa-lock"></i> <i class="btnstatus2 fa fa-unlock"></i> 鎖定工具列 {#anchor-locktoolsbutton}
    啟用後工具列將始終顯示。

    未鎖定工具列時，當滑鼠游標移出後，工具列會自動隱藏，進入視窗後工具列才會恢復顯示；如果是使用滑鼠右鍵取消的鎖定工具列，則僅當滑鼠游標進入到**鎖定工具列按鈕及其左右一個按鈕的區域**時，工具列才會恢復顯示。

    未鎖定工具列時，如果啟用了`滑鼠游標穿透視窗`，則僅當滑鼠游標移動到**滑鼠游標穿透視窗按鈕及其左右一個按鈕的區域**時，工具列才顯示；否則只要滑鼠游標進入到翻譯視窗，工具就會顯示。

    如果目前使用了視窗特效（Aero/Arylic），且不鎖定工具列，則工具列會處於文字區的 z 軸之上的區域，而非處於文字區的 y 軸上面。這是因為由於 Windows 的原因，使用視窗特效時，如果將工具列只是隱藏而非將縮去其視窗高度，則被隱藏的工具列仍會被渲染 Aero/Arylic 背景，導致工具列所在區域會有一塊空白。

1. #### <i class="fa fa-link"></i> <i class="fa fa-icon fa-rotate-right"></i> 選擇遊戲 {#anchor-selectgame}
    **該按鈕僅在 HOOK 模式下可用**

    點擊按鈕會彈出選擇遊戲處理程序視窗，來選擇要 HOOK 的遊戲處理程序。

1. #### <i class="fa fa-tasks"></i> <i class="fa fa-icon fa-rotate-right"></i> 選擇文字 {#anchor-selecttext}
    **該按鈕僅在 HOOK 模式下可用**

    點擊按鈕會彈出選擇遊戲文字視窗，來選擇要翻譯哪項 HOOK 到的文字。

    不過，選擇文字視窗在選擇處理程序後會自動彈出，這個按鈕實際上是用來更換選擇的文字，或修改一些設定用的。

1. #### <i class="fa fa-crop"></i> <i class="fa fa-icon fa-rotate-right"></i> 選取 OCR 範圍 {#anchor-selectocrrange}
    **該按鈕僅在 OCR 模式下可用**

    OCR 模式下，選取 OCR 區域，或者更換 OCR 區域，或者當啟用`OCR 設定`->`其他`->`多重區域模式`時增加新的 OCR 區域。

    當按下右鍵時，會先清除所有已選取範圍，再新增新的區域。

1. #### <i class="fa fa-square"></i> <i class="fa fa-icon fa-rotate-right"></i> 顯示／隱藏範圍框 {#anchor-hideocrrange}
    **該按鈕僅在 OCR 模式下可用**

    當未選擇任何 OCR 範圍時，使用該按鈕顯示 OCR 範圍，會自動設定 OCR 範圍為上一次選擇的 OCR。

    當按下右鍵時，會清除所有已選取範圍。

1. #### <i class="fa fa-crop"></i> <i class="fa fa-icon fa-rotate-right"></i> 進行一次 OCR {#anchor-ocr_once}
    該按鈕和`讀取剪貼簿`類似，不管目前的預設文字輸入來源是什麼，都會先進行 OCR 範圍選擇，然後進行一次 OCR，然後進行翻譯流程。

    該按鈕一般用於：在 HOOK 模式下，遊戲中遇到選項（選擇肢）時，臨時使用一次 OCR 來翻譯該選項的文字；或者在 OCR 模式下，臨時去辨識一次其他偶爾出現的新的位置。

1. #### <i class="fa fa-spinner"></i> <i class="fa fa-icon fa-rotate-right"></i> 再次進行 OCR {#anchor-ocr_once_follow}
    當使用過一次`進行一次 OCR`後，使用這個按鈕，可以在原來的位置上再次進行一次 OCR 而無需重新選擇辨識區域。

1. #### <i class="fa fa-book"></i> <i class="fa fa-icon fa-rotate-right"></i> 翻譯前取代 {#anchor-noundict_direct}
1. #### <i class="fa fa-book"></i> <i class="fa fa-icon fa-rotate-right"></i> 專有名詞翻譯 {#anchor-noundict}
1. #### <i class="fa fa-won"></i> <i class="fa fa-icon fa-rotate-right"></i> 翻譯結果修正 {#anchor-fix}
    以上三個按鈕效果類似，是用來快速開啟翻譯優化的設定視窗，增加新的指定詞條的。

    滑鼠左鍵點擊時，當有綁定的遊戲（HOOK 連結遊戲／剪貼簿、OCR 綁定視窗）時，開啟遊戲的專用詞典設定，否則則是開啟全域的詞典設定。

    滑鼠右鍵點擊時，必然開啟全域的詞典設定。

1. #### <i class="fa fa-minus"></i> <i class="fa fa-icon fa-rotate-right"></i> 最小化到系統匣 {#anchor-minmize}
    將程式最小化到系統匣。

1. #### <i class="fa fa-times"></i> <i class="fa fa-icon fa-rotate-right"></i> 退出 {#anchor-quit}
    結束程式。

1. #### <i class="fa fa-hand-paper"></i> <i class="fa fa-icon fa-rotate-right"></i> 移動 {#anchor-move}
    拖動翻譯視窗。

    實際上當按鈕欄有或沒有按鈕存在的額外空白區域時，都可以隨意拖動。該按鈕僅用來預留一個拖動位置。

1. #### <i class="fa fa-compress"></i> <i class="fa fa-expand"></i> 視窗縮放 {#anchor-fullscreen}
    可以一鍵對遊戲視窗使用內建的 Magpie 進行縮放。

    左鍵為視窗化縮放，右鍵為全螢幕縮放。

1. #### <i class="fa fa-camera"></i> <i class="fa fa-icon fa-rotate-right"></i> 視窗截圖 {#anchor-grabwindow}
    當綁定遊戲視窗後，可以對綁定的視窗進行截圖（預設會截兩張圖，GDI 和 WinRT，兩者均有一定機率會失敗）。如果目前正在使用 Magpie 進行縮放，還會對放大的視窗進行截圖。

    左鍵點擊時會把截圖儲存到檔案，右鍵點擊時截圖會儲存到剪貼簿。

1. #### <i class="fa fa-volume-off"></i> <i class="btnstatus2 fa fa-volume-up"></i> 遊戲靜音 {#anchor-muteprocess}
    當綁定遊戲視窗後，可以一鍵對遊戲進行靜音，節省了還要在系統音量混音程式才能將遊戲靜音的麻煩。

1. #### <i class="fa fa-eye"></i> <i class="btnstatus2 fa fa-eye-slash"></i> 顯示／隱藏原文 {#anchor-showraw}
    切換是否顯示原文，會立即生效。

1. #### <i class="fa fa-toggle-on"></i> <i class="btnstatus2 fa fa-toggle-off"></i> 顯示／隱藏翻譯 {#anchor-showtrans}
    切換是否使用翻譯，為翻譯的總開關，關閉後將不會進行任何翻譯。

    如果已經進行過了翻譯，則關閉後將會隱藏翻譯結果，並在重新開啟時重新顯示本次的翻譯結果。

    如果未進行過翻譯，並從隱藏切換到顯示，則會觸發對目前句子的翻譯。

1. #### <i class="fa fa-music"></i> <i class="fa fa-icon fa-rotate-right"></i> 朗讀 {#anchor-langdu}
    左擊按鈕會對目前文字進行語音合成。

    右鍵點擊該按鈕會中斷朗讀。

    該朗讀會無視`跳過`（如果在`語音指定`中，有將目前比對到的文字目標設為`跳過`，則使用按鈕進行朗讀時，會無視跳過，強制進行朗讀）。

1. #### <i class="fa fa-copy"></i> <i class="fa fa-icon fa-rotate-right"></i> 複製到剪貼簿 {#anchor-copy}
    複製目前擷取到的文字到剪貼簿一次。如果想要自動擷取到剪貼簿，應啟用`文字輸入`->`剪貼簿`->`自動輸出`->`自動輸出文字`。

1. #### <i class="fa fa-rotate-left"></i> <i class="fa fa-icon fa-rotate-right"></i> 顯示／隱藏歷史文字 {#anchor-history}
    開啟或關閉歷史文字的視窗。

1. #### <i class="fa fa-gamepad"></i> <i class="fa fa-icon fa-rotate-right"></i> 遊戲管理 {#anchor-gamepad_new}
    開啟遊戲管理器介面。

1. #### <i class="fa fa-edit"></i> <i class="fa fa-icon fa-rotate-right"></i> 編輯 {#anchor-edit}
    開啟編輯視窗，以編輯目前擷取到的文字。

    該視窗中，可以在修改文字後，再去進行翻譯；或者可以翻譯任何自行輸入的文字。

1. #### <i class="fa fa-edit"></i> <i class="fa fa-icon fa-rotate-right"></i> 編輯 翻譯紀錄 {#anchor-edittrans}
    開啟目前遊戲的翻譯紀錄編輯視窗。

1. #### <i class="fa fa-download"></i> <i class="fa fa-icon fa-rotate-right"></i> 模擬按鍵 Ctrl {#anchor-simulate_key_ctrl}
    用於向遊戲視窗發送一次模擬按鍵 Ctrl。對於使用串流／平板時有些用處。

1. #### <i class="fa fa-download"></i> <i class="fa fa-icon fa-rotate-right"></i> 模擬按鍵 Enter {#anchor-simulate_key_enter}
    同上，用於向遊戲視窗發送一次模擬按鍵 Enter。對於使用串流／平板時有些用處。

1. #### <i class="fa fa-list-ul"></i> <i class="fa fa-icon fa-rotate-right"></i> 備忘錄 {#anchor-memory}
    對於目前正在玩的遊戲，開啟備忘錄視窗。

    點擊左鍵時，開啟目前遊戲的備忘錄。點擊右鍵時，開啟全域的備忘錄。

1. #### <i class="fab fa-windows"></i> <i class="btnstatus2 fab fa-windows"></i> 綁定視窗 （點擊自己取消） {#anchor-bindwindow}
    **該按鈕非常重要，許多功能都依賴於該按鈕先進行設定後才可用**

    在綁定了遊戲視窗後，`視窗縮放` `視窗截圖` `遊戲靜音`，`跟隨遊戲視窗`->`遊戲失去焦點時取消置頂`和`遊戲視窗移動時同步移動`，以及記錄遊戲時間等功能，才可用。
    不論 HOOK／OCR／剪貼簿模式，該按鈕都可用。

    在 HOOK 模式下，會自動根據連接的遊戲，自動綁定遊戲視窗。但也可以再用該按鈕重新選擇其他視窗。

    在 OCR 模式下，綁定視窗後，還額外允許在遊戲視窗移動時，自動同步移動 OCR 區域和範圍框。
    在 OCR／剪貼簿模式下，綁定視窗後，也可以和 HOOK 模式下一樣，關聯到目前遊戲到遊戲設定，從而使用目前遊戲的專用翻譯優化詞典等。

1. #### <i class="fa fa-neuter"></i> <i class="btnstatus2 fa fa-neuter"></i> 視窗置頂 {#anchor-keepontop}
    取消／置頂翻譯視窗。

1. #### <i class="fa fa-i-cursor"></i> <i class="btnstatus2 fa fa-i-cursor"></i> 可選取的 {#anchor-selectable}
    使得翻譯視窗的文字區中的文字，是可以進行選擇的。

    如果啟用時點擊的是滑鼠右鍵，則會禁止拖曳非文字區域以移動視窗。

1. #### <i class="fa fa-search"></i> <i class="fa fa-icon fa-rotate-right"></i> 查詞 {#anchor-searchwordW}
    如果目前有文字被選取，則會查詢選取的文字並開啟查詞視窗。否則只是開啟或關閉查詞視窗。

1. #### <i class="fa fa-refresh"></i> 重置翻譯狀態 {#anchor-reset_TS_status}
    重置翻譯狀態，主要針對用於現今日益增長的大模型翻譯需求，可清除保存的上下文和其他資訊。