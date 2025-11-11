# 軟體下載 & 常見問題

## 下載

| 作業系統 | 64 位元 |
| - | - |
| Windows 10 & 11 | <downloadbtn href="https://lunatranslator.org/Resource/DownloadLuna/x64_win10?doc=1"/> |

::: details 舊版作業系統相容版

>[!WARNING]
這些版本性能更差，運行更不穩定，而且缺少一些特性和功能，更容易被防毒軟體誤報。如果沒有特殊需求不建議使用。

| 作業系統 | 32 位元 | 64 位元 |
| - | - | - |
| Windows 7 及以上 | <downloadbtn href="https://lunatranslator.org/Resource/DownloadLuna/x86_win7?doc=1"/> | <downloadbtn href="https://lunatranslator.org/Resource/DownloadLuna/x64_win7?doc=1"/> |
| Windows XP & Vista | <downloadbtn href="https://lunatranslator.org/Resource/DownloadLuna/x86_winxp?doc=1"/> | |

:::

## 啟動

下載後解壓縮到任意目錄

::: warning
但請不要把軟體放到 **C:\Program Files** 等特殊路徑下，否則即使使用管理員身分，也可能無法儲存配置和快取檔案，甚至無法執行。
:::

**LunaTranslator.exe**：會以普通模式啟動。

**LunaTranslator_admin.exe**：會以管理員身分啟動，部份遊戲需要管理員權限才能 HOOK，僅這時需要使用這個，其他時候普通模式啟動即可。

**LunaTranslator_debug.bat**：會顯示命令提示字元的視窗。

## 更新

預設會自動進行更新。如果自動更新失敗，可以手動更新。

如果想要手動更新，只需下載新版本後解壓縮覆蓋到之前的目錄即可。

如果想要刪除重下，注意不要刪除`userconfig`資料夾，否則會失去之前的設定！！！

## 常見錯誤 {#anchor-commonerros}

### 找不到重要元件 / Missing embedded Python3

::: danger
有時會被防毒軟體刪掉，請新增例外並重新下載解壓縮。
:::

![img](https://image.lunatranslator.org/zh/cantstart/2.jpg)

![img](https://image.lunatranslator.org/zh/missingpython.png) 

解決方法：關閉防毒軟體，若無法關閉（如 Windows Defender）則新增例外，然後重新下載。

註：為了實現 HOOK 擷取遊戲文字，需要將 DLL 注入到遊戲，`shareddllproxy32.exe`、`LunaHost32.dll`等幾個檔案中實現了這些內容，因此特別容易被認為是病毒。軟體目前由 [Github Actions](https://github.com/HIllya51/LunaTranslator/actions) 自動建構，除非 Github 伺服器中毒了，否則不可能包含病毒，因此可以放心的新增例外。

::: details 對於 Windows Defender，方法為：`病毒與威脅防護`->`病毒與威脅防護設定`的`管理設定`->`排除項目`的`新增或移除排除項目`->`新增排除範圍`->`資料夾`，把 Luna 的資料夾新增進去。
![img](https://image.lunatranslator.org/zh/cantstart/4.png)
![img](https://image.lunatranslator.org/zh/cantstart/3.png)
:::

### Error/FileNotFoundError

如果沒有預先新增好例外，有可能在軟體執行一段時間後，部份必要元件才被防毒軟體刪除。然後等到 HOOK 模式選取處理程序之後，才會報出這個錯誤。解決方法同上。

<img src="https://image.lunatranslator.org/zh/notfound.png" width=400>

### Error/PermissionError

如果軟體被放到`C:\Program Files`等特殊資料夾，可能會無法正常執行。

<img src="https://image.lunatranslator.org/zh/cantstart/6.png" width=400>

