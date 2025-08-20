# 創建多份配置檔案

在此之前，如果想讓軟體同時以不同的配置打開多個，只能通過整個將軟體複製多份才能實現，這會浪費很多空間。

近期，對此進行了優化，可以讓軟體讀取指定目錄的配置檔案，從而只需在運行時指定使用的配置檔案目錄，即可使用不同的配置檔案。

方法是：

1. 為主程式創建捷徑

    ![img](https://image.lunatranslator.org/zh/multiconfigs.png)

1. 修改捷徑的屬性->目標，在最後添加` --userconfig=XXXX`，其中，將`XXXX`替換為你想使用作為新的配置項的資料夾的名字。然後使用這個捷徑啟動軟體即可。

    如果`XXXX`是一個不存在的資料夾，那麼會使用預設設定啟動軟體，並創建這個資料夾。

    如果`XXXX`是一個已經存在的資料夾，那麼會使用這個資料夾中的配置檔案啟動軟體。你可以複製舊的userconfig資料夾，然後指定`XXXX`為複製的資料夾的名字，這樣就可以從之前的配置之上，分叉出新的配置。

    ![img](https://image.lunatranslator.org/zh/multiconfigs2.png)

    ![img](https://image.lunatranslator.org/zh/multiconfigs3.png)
