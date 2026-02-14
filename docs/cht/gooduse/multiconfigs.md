# 建立多份設定檔

在此之前，如果想讓軟體同時以不同的設定開啟多個，只能透過整個將軟體複製多份才能實現，這會浪費很多空間。

近期，對此進行了優化，可以讓軟體讀取指定目錄的設定檔，從而只需在執行時指定使用的設定檔目錄，即可使用不同的設定檔。

方法是：

1. 為主程式建立捷徑。

    ![img](https://image.lunatranslator.org/zh/multiconfigs.png)

1. 修改捷徑的屬性->目標，在最後新增` --userconfig=XXXX`，其中，將`XXXX`取代為您想使用作為新的設定檔之資料夾的名字。然後使用這個捷徑啟動軟體即可。

    如果`XXXX`是一個不存在的資料夾，那麼會使用預設設定啟動軟體，並建立這個資料夾。

    如果`XXXX`是一個已經存在的資料夾，那麼會使用這個資料夾中的設定檔來啟動軟體。您可以複製舊的`userconfig`資料夾，然後指定`XXXX`為複製的資料夾的名字，這樣就可以從之前的設定之上，分叉出新的設定。

    ![img](https://image.lunatranslator.org/zh/multiconfigs2.png)

    ![img](https://image.lunatranslator.org/zh/multiconfigs3.png)
