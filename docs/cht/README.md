# 下載和啓動

## 下載

| 操作系統 | 32位 | 64位 | 說明 |
| - | - | - | - |
| Windows 10 & 11 |  | <downloadbtn href="https://lunatranslator.org/Resource/DownloadLuna/x64_win10?doc=1"/> | 該版本只支持較新的Windows 10版本，以獲取更高性能，更新的系統特性，及更低的病毒誤報率。
| Windows 7 及以上 | <downloadbtn href="https://lunatranslator.org/Resource/DownloadLuna/x86_win7?doc=1"/> | <downloadbtn href="https://lunatranslator.org/Resource/DownloadLuna/x64_win7?doc=1"/> |
| Windows XP & Vista | <downloadbtn href="https://lunatranslator.org/Resource/DownloadLuna/x86_winxp?doc=1"/> | | 該版本僅用於支持提取僅能在XP虛擬機內運行的很老遊戲的文本，功能殘缺、不穩定、運行緩慢，一般不要使用。


## 啓動

下載後解壓到任意目錄

::: warning
但請不要把軟件放到**C:\Program Files**等特殊路徑下，否則即使使用管理員權限，也可能無法保存配置和緩存文件，甚至無法運行。
:::

**LunaTranslator.exe** 會以普通模式啓動 

**LunaTranslator_admin.exe** 會以管理員權限啓動，部分遊戲需要管理員權限才能HOOK，僅這時需要使用這個，其他時候普通模式啓動即可。

**LunaTranslator_debug.bat** 會顯示命令行窗口

## 常見錯誤

### 找不到重要組件

::: danger
有時會被殺毒軟件殺掉，請添加信任並重新下載解壓
:::

![img](https://image.lunatranslator.org/zh/cantstart/2.jpg) 

解決方法：關閉殺毒軟件，無法關閉(如windows defender)則添加信任，然後重下。

注：爲了實現HOOK提取遊戲文本，需要將Dll注入到遊戲，shareddllproxy32.exe/LunaHost32.dll等幾個文件中實現了這些內容，因此特別容易被認爲是病毒。軟件目前由[Github Actions](https://github.com/HIllya51/LunaTranslator/actions)自動構建，除非Github服務器中毒了，否則不可能包含病毒，因此可以放心的添加信任。

::: details 對於windows defender，方法爲：“病毒和威脅防護”->“排除項”->“添加或刪除排除項”->“添加排除項”->“文件夾”，把Luna的文件夾添加進去
![img](https://image.lunatranslator.org/zh/cantstart/4.png) 
![img](https://image.lunatranslator.org/zh/cantstart/3.png) 
::: 

### Error/FileNotFoundError

如果沒有預先添加好信任，有可能在軟件運行一段時間後，部分必要組件才被殺毒軟件刪除。然後等到HOOK模式選取進程之後，報出這個錯誤。解決方法同上。

<img src="https://image.lunatranslator.org/zh/notfound.png" width=400>

### Error/PermissionError

如果軟件被放到`C:\Program Files`等特殊文件夾，可能會無法正常運行。

<img src="https://image.lunatranslator.org/zh/cantstart/6.png" width=400>