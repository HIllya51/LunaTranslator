# 各種翻譯優化的作用

1. ## 專有名詞翻譯 {#anchor-noundict}

    這種方法會在翻譯之前，直接用譯文將原文進行取代。支援使用`正則` `跳脫`進行更複雜的取代。

    當從 VNDB 載入中繼資料時，遊戲會查詢角色名稱資訊並設定為預設詞典。對於英文使用者，提取的英文名稱會被填入作為原文對應的翻譯。否則，為了在使用者未進行修改時不影響翻譯，翻譯內容將填入與原文相同的內容。

    ::: details 範例
    ![img](https://image.lunatranslator.org/zh/transoptimi/1.png)
    :::


1. ## 專有名詞翻譯 {#anchor-noundict}

    針對`大模型通用介面`，如果其提示詞中包含`DictWithPrompt`，則會將詞條放入模型的提示詞中。使用方法請參考[此文件](/zh/guochandamoxing.html#anchor-prompt)。
        
    對於其他傳統翻譯，或`大模型通用介面`的提示詞中不包含`DictWithPrompt`，則會參考 VNR 的做法，將原文替換為佔位符號`ZX?Z`（附註：我也不知道這是什麼意思），翻譯來源翻譯後一般不會破壞佔位符號，然後在翻譯後將佔位符號替換成翻譯。

    對於遊戲的專用詞條，建議不要在文字處理->翻譯優化中新增。建議在`遊戲設定`中的`翻譯最佳化`的該方法的設定中，新增遊戲專用的詞條。

    遊戲從 VNDB 載入中繼資料時，會查詢遊戲中的人物名稱資訊作為預設詞典。對於英文使用者，會將提取到的英文填入作為原文對應的翻譯，否則會將翻譯留空，以避免在使用者未進行修改時影響翻譯。

    ::: details 設定遊戲的專用詞條
    建議使用：
    ![img](https://image.lunatranslator.org/zh/transoptimi/2.png)
    而不是：
    ![img](https://image.lunatranslator.org/zh/transoptimi/3.png)
    :::
    ::: details Sakura 大模型設定 Prompt 格式為非 v0.9 以外的版本，以支援 GPT 詞典
    ![img](https://image.lunatranslator.org/zh/transoptimi/4.png)
    :::

1. ## 翻譯結果修正 {#anchor-transerrorfix}

    這個方法是，在翻譯完畢後，可以對翻譯的結果進行一定的修正，並可以使用整個表達式進行複雜的修正。

1. ## 自訂優化 {#anchor-myprocess}

    撰寫一個 Python 腳本來進行更複雜的處理。

1. ## 跳過僅包含標點符號的句子 {#anchor-skiponlypunctuations}

    略

## 遊戲專用翻譯優化

在`遊戲設定`->`翻譯優化`中，若取消啟用`跟隨預設`，則會使用遊戲專用的翻譯優化設定。

若啟用`繼承預設`，則在遊戲專用翻譯優化的詞典之外，也會同時使用預設的全域詞典。