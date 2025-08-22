# 網路服務

## Web 頁面

1. #### /page/mainui

    與主視窗顯示的文字內容同步

1. #### /page/transhist

    與歷史文字顯示的文字內容同步

1. #### /page/dictionary

    查詢單字頁面。在`/page/mainui`中進行點擊單字查詞時會喚出該頁面。

1. #### /

    整合上述三個頁面的一個頁面。在該視窗中的`/page/mainui`子區域中進行點擊單字查詞時，不會開啟新的查詞視窗，而是會在目前視窗的`/page/dictionary`子區域中進行查詞。

1. #### /page/translate

    翻譯介面

1. #### /page/ocr

    OCR 介面

1. #### /page/tts

    TTS 介面

## API 服務

### HTTP 服務

1. #### /api/translate

    - 必須指定查詢參數`text`
    - 如果指定參數`id`（翻譯器的 ID），則會使用該翻譯器進行翻譯，否則會回傳最快的翻譯介面
    - 回傳`application/json`，包含翻譯器 ID`id`、名稱`name`和翻譯結果`result`

1. #### /api/dictionary

    - 必須指定查詢參數`word`
    - 如果指定參數`id`（詞典的 ID），則會回傳該詞典的查詢結果的`application/json`物件，包含詞典 ID`id`、詞典名稱`name`和 HTML 內容`result`。如果查詢失敗則會回傳一個空的物件
    - 否則會查詢所有詞典，回傳`event/text-stream`，每個 Event 為一個 JSON 物件，包含詞典 ID`id`、詞典名稱`name`和 HTML 內容`result`

1. #### /api/mecab

    - 必須指定查詢參數`text`
    - 回傳 Mecab 對`text`的解析結果

1. #### /api/tts

    - 必須指定查詢參數`text`
    - 回傳音訊的二進制資料

1. #### /api/ocr

    使用 POST 方法，發送 JSON 請求，包含`image`欄位，內容為 Base64 編碼的圖像。

1. #### /api/list/dictionary

    列出目前可用的辭書

1. #### /api/list/translator

    列出目前可用的翻譯器


### WebSocket 服務

1.  #### /api/ws/text/origin

    會持續輸出所有擷取到的原文文字

1.  #### /api/ws/text/trans

    會持續輸出所有翻譯結果
