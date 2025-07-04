# 網絡服務

## Web頁面

1. #### /page/mainui

    與主窗口顯示的文本內容同步

1. #### /page/transhist

    與歷史文本顯示的文本內容同步

1. #### /page/dictionary

    查詢單詞頁面。在/page/mainui中進行點擊單詞查詞時會喚出該頁面。

1. #### /

    整合上述三個頁面的一個頁面。在該窗口中的/page/mainui子區域中進行點擊單詞查詞時，不會打開新的查詞窗口，而是會在當前窗口的/page/dictionary子區域中進行查詞

1. #### /page/translate

    翻譯界面

1. #### /page/ocr

    OCR界面

1. #### /page/tts

    TTS界面

## API服務

### HTTP服務

1. #### /api/translate
    
    必須指定查詢參數`text`

    如果指定參數`id`（翻譯器的ID），則會使用該翻譯器進行翻譯，否則會返回最快的翻譯接口

    返回`application/json`，包含翻譯器ID`id`、名稱`name`和翻譯結果`result`

1. #### /api/dictionary

    必須指定查詢參數`word`

    如果指定參數`id`（詞典的ID），則會返回該詞典的查詢結果的`application/json`對象，包含詞典ID`id`、詞典名稱`name`和HTML內容`result`。如果查詢失敗則會返回一個空的對象。

    否則會查詢所有詞典，返回`event/text-stream`，每個event爲一個JSON對象，包含詞典ID`id`、詞典名稱`name`和HTML內容`result`

1. #### /api/mecab
    
    必須指定查詢參數`text`

    返回Mecab對`text`的解析結果

1. #### /api/tts
    
    必須指定查詢參數`text`

    返回音頻二進制

1. #### /api/ocr
    
    使用POST方法，發送json請求，包含`image`字段，內容爲base64編碼的圖像。

1. #### /api/list/dictionary

    列出當前可用的辭書

1. #### /api/list/translator

    列出當前可用的翻譯器


### WebSocket服務

1.  #### /api/ws/text/origin

    會持續輸出所有提取到的原文文本

1.  #### /api/ws/text/trans

    會持續輸出所有翻譯結果
