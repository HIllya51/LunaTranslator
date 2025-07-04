# 內嵌翻譯

## 使用方法

::: danger
首先，不是所有遊戲都支持內嵌。其次，內嵌有一定可能會導致遊戲崩潰
:::

::: details 如果選擇文本中沒有內嵌這一行，就說明不支持內嵌 
![img](https://image.lunatranslator.org/zh/embed/noembed.png) 
![img](https://image.lunatranslator.org/zh/embed/someembed.png) 
:::

對於支持內嵌的遊戲，選擇支持內嵌的文本條目，激活內嵌即可

![img](https://image.lunatranslator.org/zh/embed/select.png)

對於支持內嵌的條目，**顯示**和**內嵌**可以隨意選擇是否同時激活。當同時激活時，既會在遊戲中嵌入翻譯，也會在軟件窗口中顯示更多翻譯；若只激活內嵌，則只會在遊戲中顯示嵌入的翻譯，軟件窗口則不會顯示任何內容。

當開始內嵌翻譯後，經常會出現亂碼的情況。遊戲亂碼一般會是**字符集**和**字體**兩種問題。對於英文遊戲，通常是因爲遊戲缺少中文**字體**導致的，例如：

![img](https://image.lunatranslator.org/zh/embed/luanma.png)

這時，你需要激活**修改遊戲字體**，並選擇一個適當的字體，以顯示中文字符

![img](https://image.lunatranslator.org/zh/embed/ziti.png)

修改完畢字體後，中文可以正確的顯示了：

![img](https://image.lunatranslator.org/zh/embed/okembed.png)

對於許多古早日本galgame，他們使用自己內置的shift-jis字符集處理，無法正確處理中文字符，可以嘗試**將漢字轉換成繁體/日式漢字**，減少亂碼的出現。

對於一些較新的遊戲引擎和大部分英文遊戲，一般使用utf-8或utf-16等Unicode字符集（如**KiriKiri**，**Renpy**，**TyranoScript**，**RPGMakerMV**等），即使出現亂碼一般也是字體的問題，而不是字符集的問題。

![img](https://image.lunatranslator.org/zh/embed/fanti.png)

取消這一設置後，可以正常顯示簡體中文了。但對於一些無法正常顯示簡體中文的遊戲，可以嘗試激活這一選擇來看看能不能正常顯示。

![img](https://image.lunatranslator.org/zh/embed/good.png)

## 內嵌翻譯設置

1. #### 顯示模式

    ![img](https://image.lunatranslator.org/zh/embed/keeporigin.png)

    由於遊戲能顯示的文本行數的限制，所以默認沒有在翻譯和原文中間添加換行。如果確定可以容納，可以通過在**翻譯優化**->**翻譯結果修正**中添加一條正則來在翻譯前面添加一個換行來實現。

    ![img](https://image.lunatranslator.org/zh/embed/addspace.png)

1. #### 翻譯等待時間

    內嵌翻譯的原理是在遊戲顯示文本前，在某個函數中停住遊戲，把其中要顯示的文本發送給翻譯器，等待到翻譯後把文本內存修改從翻譯的文本，然後讓遊戲繼續運行來顯示翻譯。因此**當使用的翻譯速度較慢時，是一定會導致遊戲卡頓的**。可以通過限制等待的時間，來避免翻譯過慢導致長時間卡頓。

1. #### 將漢字轉換成繁體/日式漢字

    略

1. #### 限制每行字數

    有時某些遊戲每行能顯示的字符數是有限的，超出長度的內容會顯示到文本框右邊的更外邊而無法顯示。可以通過這一設置來手動分行來避免這一情況。

    ![img](https://image.lunatranslator.org/zh/embed/limitlength.png)

1. #### 修改遊戲字體

    略

1. #### 內嵌安全性檢查

    對於Renpy等遊戲，提取的文本經常會包括`{` `}` `[` `]`等語法元素的字符，如果翻譯源沒有正確處理這些內容導致破壞了語法，會導致遊戲崩潰。因此軟件默認會通過正則匹配來**跳過翻譯**某些可能會導致遊戲的字符組合。如果不擔心遊戲崩潰，可以取消這一設置，或者手動更換一些更細粒度的正則匹配來減少不必要的跳過。

    ![img](https://image.lunatranslator.org/zh/embed/safeskip.png)
    
1. #### 清除遊戲內顯示的文字

    激活該選項後，遊戲內要顯示內嵌文本處的內容將被清空。

    該選項可能滿足以下需要：

    1. 有時，內嵌翻譯有無法解決的字符編碼和字體無法顯示的問題。開啓該選項，然後將軟件窗口覆蓋到原本遊戲中顯示文字的地方，可以僞裝成內嵌翻譯的樣子。

    1. 有時，我們並不是想要進行內嵌翻譯，而是使用外掛翻譯時，有可能覺得將窗口放在文字區會和原文本重疊，放在其他地方會遮擋畫面。
    
    1. 有時，我們僅想要用來學習日語，然後遊戲文本沒有對文字加註音或雙語對照的功能。
