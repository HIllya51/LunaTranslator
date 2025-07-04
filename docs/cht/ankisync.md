# Anki本地同步服務器

使用LunaTranslator內置的制卡模板在添加過多卡片時，有超出anki.web同步體積的可能。這時可以選擇使用anki內置的本地同步服務器功能。

1. ## 開啓本地同步服務器

    在cmd中，運行以下代碼：

    ```bat
    set SYNC_PORT=8080
    set SYNC_USER1=user:pass
    set MAX_SYNC_PAYLOAD_MEGS=10000000
    %LOCALAPPDATA%\Programs\Anki\anki.exe --syncserver
    pause
    ```

    ::: tip
    其中，`8080`是同步服務器佔用的默認端口號。如果運行失敗，可能是端口號被佔用，修改成其他端口號，**修改後後續也應做出對應的修改**。

    `user:pass`分別是自定義的用戶名和密碼，並隨時可以更改，**後續登錄時都需要填寫這個內容**。

    `%LOCALAPPDATA%\Programs\Anki\anki.exe`是anki的路徑，這裏是默認的安裝路徑，如果你的電腦上的anki路徑不是這個，那麼自行修改即可。
    :::

    爲了更方便的運行，可以將這段代碼保存爲`XXX.bat`，即可雙擊運行。

    ::: details 啓動成功&失敗
    啓動成功
    ![img](https://image.lunatranslator.org/zh/anki/startsuccess.png)

    啓動失敗，可能是端口號被佔用
    ![img](https://image.lunatranslator.org/zh/anki/startfailed.png)
    :::
    
    ::: details 隱藏控制檯窗口在後臺運行

    如果想要隱藏控制檯窗口在後臺運行同步服務器，可以再創建一個`YYY.vbs`，其中寫入以下內容：

    ```vbs
    Set objShell = WScript.CreateObject("WScript.Shell")
    objShell.Run "XXX.bat", 0, False
    ```
    其中，`YYY.vbs`中的`XXX.bat`必須和保存的bat文件名相同。
    
    雙擊`YYY.vbs`即可後臺運行，但會看不到錯誤信息，建議先用bat版本調式好後再用vbs運行。
    :::

1. ## 將電腦上的數據上傳到本地同步服務器

    首次啓動本地同步服務器後，其中內容是空白的，需要首先將電腦上的數據上傳到本地同步服務器之後，手機上才能從本地服務器下載數據。

    1. 首先，在`設置`->`同步`中修改`自託管同步服務器`，修改爲`http://127.0.0.1:8080`。如果前面修改了端口號(SYNC_PORT)，則這裏8080也要修改爲同樣的值。

        ![img](https://image.lunatranslator.org/zh/anki/ankiset1.png)

    1. 關閉anki，然後重新打開，使上述修改生效

    1. 使用前面設置的用戶名和密碼(`user:pass`)進行登錄，然後按照anki的提示同步數據到本地同步服務器即可。
        ::: details 圖例
        ![img](https://image.lunatranslator.org/zh/anki/login.png)
        :::

1. ## 在手機上從本地同步服務器下載數據

    1. 確保手機和電腦處於同一個局域網內，例如鏈接到同一個路由器等。

        如果同時連接到校園網等，可能仍無法通信，可以在電腦上開啓移動熱點，然後讓手機連接電腦的熱點。

    1. 獲取電腦的ip地址。在cmd中輸入以下內容，可以獲取可能的ip地址。若有多個候選的ip地址，在後續中對其一一進行測試即可。
        ```bat
        for /f "tokens=2 delims=:" %A in ('ipconfig ^| findstr /i "IPv4"') do @for /f "tokens=*" %B in ("%A") do @echo %B
        ```

    1. 在`設置`->`同步`中修改`自定義同步服務器`。同步地址爲`http://電腦的ip地址:8080`，其中電腦的ip地址爲上一步獲取的ip地址，8080爲前面設置端口號(SYNC_PORT)。
        ::: details 圖例
        ![img](https://image.lunatranslator.org/zh/anki/ankiandr1.jpg)
    
        ![img](https://image.lunatranslator.org/zh/anki/ankiandr2.jpg)
        :::

    1. 設置好後，使用前面設置的用戶名和密碼(`user:pass`)進行登錄，然後按照anki的提示同步數據即可。

        如果同步失敗，可能是前面設置的ip地址錯誤，修改ip地址後，再次測試登錄即可。
        ::: details 圖例
        ![img](https://image.lunatranslator.org/zh/anki/ankiandr3.jpg)
        :::