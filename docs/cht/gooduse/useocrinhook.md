
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

# 在HOOK模式下臨時使用OCR  

有時，HOOK模式不會捕獲遊戲中的菜單、選項等文字，而為此切換到OCR模式進行識別再切換回HOOK模式又很麻煩。  

其實，對於這種情況，早已有了內置的解決方案，即使用「進行一次OCR」按鈕<i class="fa fa-crop"></i>或快捷鍵。  

這個按鈕和OCR模式下選取識別範圍的按鈕的默認圖標是相同的，並且現在已經默認激活使用該按鈕。  

這個按鈕在選取完範圍後，只會進行一次OCR，然後退出OCR，然後無縫繼續使用HOOK自動提取文本，完美解決了HOOK模式的一些缺漏。  

**由於這個按鈕的圖標，很多原本就想要使用OCR的人，誤以為這就是OCR的按鈕，結果仍在HOOK模式下就使用這個按鈕，選取完範圍後卻不會進行自動翻譯。實際上當切換到OCR模式後，OCR模式的按鈕才會顯示出來。**  

如果對於固定位置的選項，不想每次重複選區，可以使用「再次進行OCR」按鈕<i class="fa fa-spinner"></i>或快捷鍵，即可延續上一次選取的範圍來進行一次OCR。