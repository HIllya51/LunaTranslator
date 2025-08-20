
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

# 在 HOOK 模式下臨時使用 OCR  

有時，HOOK 模式不會擷取遊戲中的選單、選項等文字，而為此切換到 OCR 模式進行辨識再切換回 HOOK 模式又很麻煩。  

其實，對於這種情況，早已有了內建的解決方案，即使用「進行一次OCR」按鈕<i class="fa fa-crop"></i>或快速鍵。  

這個按鈕和 OCR 模式下選取辨識範圍的按鈕的預設圖示是相同的，並且現在已經預設顯示該按鈕。  

這個按鈕在選取完範圍後，只會進行一次 OCR，然後退出 OCR，然後無縫繼續使用 HOOK 自動擷取文字，完美解決了 HOOK 模式的一些缺漏。  

**由於這個按鈕的圖示，很多原本就想要使用 OCR 的人，誤以為這就是 OCR 的按鈕，結果仍在 HOOK 模式下就使用這個按鈕，選取完範圍後卻不會進行自動翻譯。實際上當切換到 OCR 模式後，OCR 模式的按鈕才會顯示出來。**  

如果對於固定位置的選項，不想每次重複選取，可以使用「再次進行 OCR」按鈕<i class="fa fa-spinner"></i>或快速鍵，即可延續上一次選取的範圍來進行一次 OCR。