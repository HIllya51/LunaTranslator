# 各種翻譯優化的作用

1. ## 專有名詞翻譯 翻譯前取代 {#anchor-vndbnamemap}

    這種方法會在翻譯之前，直接用譯文將原文進行替換。支持使用`正則` `轉義`進行更復雜的替換。

    當遊戲從VNDB加載元數據時，會查詢遊戲中的人名信息作爲預設的詞典。不過譯文由於VNDB的原因是英文，可以自行進行修改譯文成中文。

    ::: details 示例
    ![img](https://image.lunatranslator.org/zh/transoptimi/1.png)
    :::


1. ## 專有名詞翻譯 {#anchor-noundict}

    如果使用`sakura大模型`並設置prompt格式爲支持gpt詞典的prompt，則會轉換成gpt詞典格式，否則會參考的VNR的做法，將原文替換爲佔位符`ZX?Z` （ps：我也不知道這是什麼意思），翻譯源翻譯後一般不會將佔位符破壞，然後在翻譯後將佔位符替換成翻譯。

    對於遊戲的專用詞條，建議不要在文本處理->翻譯優化中添加。過去使用遊戲的md5值來區分多個遊戲的詞條，但這樣的實現其實不是很好，已經廢棄這樣的實現。現在建議在`遊戲設置`中的`翻譯優化`中的該方法的設置中，添加遊戲專用的詞條。

    最後一列`註釋`僅用於給`sakura大模型`使用，其他翻譯會無視這一列。
      
    ::: details 設置遊戲的專用詞條
    建議使用：
    ![img](https://image.lunatranslator.org/zh/transoptimi/2.png)
    而不是：
    ![img](https://image.lunatranslator.org/zh/transoptimi/3.png)
    :::
    ::: details sakura大模型設置prompt格式爲v0.10pre1（支持gpt詞典）
    ![img](https://image.lunatranslator.org/zh/transoptimi/4.png)
    :::

1. ## 翻譯結果修正 {#anchor-transerrorfix}

    這個方法是，在翻譯完畢後，可以對翻譯的結果進行一定的修正，並可以使用整個表達式進行復雜的修正。

1. ## 自訂優化 {#anchor-myprocess}

    撰寫一個Python腳本來進行更複雜的處理

## 遊戲專用翻譯優化

在`遊戲設置`->`翻譯優化`中，若取消激活跟隨默認，則會使用遊戲專用的翻譯優化設置。

若激活`繼承默認`，則在遊戲專用翻譯優化的詞典之外，也會同時使用默認的全局詞典。