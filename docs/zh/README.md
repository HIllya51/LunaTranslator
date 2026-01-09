# 软件下载 & 常见问题

## 下载

| 操作系统 | 64位 | 
| - | - | 
| Windows 10 & 11 | <downloadbtn href="https://lunatranslator.org/Resource/DownloadLuna/x64_win10?doc=1"/> | 

::: details 旧版操作系统兼容版

>[!WARNING]
这些版本性能更差，运行更不稳定，而且缺少一些特性和功能，更容易被杀毒软件误报。如果没有特殊需要不建议使用。

| 操作系统 | 32位 | 64位 |
| - | - | - |
| Windows 7 及以上 | <downloadbtn href="https://lunatranslator.org/Resource/DownloadLuna/x86_win7?doc=1"/> | <downloadbtn href="https://lunatranslator.org/Resource/DownloadLuna/x64_win7?doc=1"/> |
| Windows XP & Vista | <downloadbtn href="https://lunatranslator.org/Resource/DownloadLuna/x86_winxp?doc=1"/> | |

:::

## 启动

下载后解压到任意目录

::: warning
但请不要把软件放到**C:\Program Files**等特殊路径下，否则即使使用管理员权限，也可能无法保存配置和缓存文件，甚至无法运行。
:::

**LunaTranslator.exe** 会以普通模式启动 

**LunaTranslator_admin.exe** 会以管理员权限启动，部分游戏需要管理员权限才能HOOK，仅这时需要使用这个，其他时候普通模式启动即可。

**LunaTranslator_debug.bat** 会显示命令行窗口

## 更新

默认会自动进行更新。如果自动更新失败，可以手动更新。

如果想要手动更新，只需下载新版本后解压覆盖到之前的目录即可。

如果想要删除重下，注意不要删除userconfig文件夹，否则会失去之前的设置！！！

## 常见错误 {#anchor-commonerros}

### 找不到重要组件 / Missing embedded Python3

::: danger
有时会被杀毒软件杀掉，请添加信任并重新下载解压
:::

![img](https://image.lunatranslator.org/zh/cantstart/2.jpg) 

![img](https://image.lunatranslator.org/zh/missingpython.png) 

解决方法：关闭杀毒软件，无法关闭(如windows defender)则添加信任，然后重下。

注：为了实现HOOK提取游戏文本，需要将Dll注入到游戏，shareddllproxy32.exe/LunaHost32.dll等几个文件中实现了这些内容，因此特别容易被认为是病毒。软件目前由[Github Actions](https://github.com/HIllya51/LunaTranslator/actions)自动构建，除非Github服务器中毒了，否则不可能包含病毒，因此可以放心的添加信任。

::: details 对于windows defender，方法为：“病毒和威胁防护”->“排除项”->“添加或删除排除项”->“添加排除项”->“文件夹”，把Luna的文件夹添加进去
![img](https://image.lunatranslator.org/zh/cantstart/4.png) 
![img](https://image.lunatranslator.org/zh/cantstart/3.png) 
::: 

### 正在等待DLL注入到游戏中…… {#anchor-waitdll}

解决方法同上。

### Error/FileNotFoundError

如果没有预先添加好信任，有可能在软件运行一段时间后，部分必要组件才被杀毒软件删除。然后等到HOOK模式选取进程之后，报出这个错误。解决方法同上。

<img src="https://image.lunatranslator.org/zh/notfound.png" width=400>

### Error/PermissionError

如果软件被放到`C:\Program Files`等特殊文件夹，可能会无法正常运行。

<img src="https://image.lunatranslator.org/zh/cantstart/6.png" width=400>
