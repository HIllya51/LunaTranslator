# 下载和启动

## 下载

| 版本 | 操作系统 | 32位 | 64位 | 说明 |
| - | - | - | - | - |
| 尝鲜版 | Windows 10 & 11 新版本 |  | <downloadbtn href="https://lunatranslator.org/Resource/DownloadLuna/x64_win10?doc=1"/> | 该版本只支持较新的Windows 10版本，以获取更高性能，更新的系统特性，及更低的病毒误报率。<br>如果系统是Windows 10的早期版本，可能也是无法运行的，请改用稳定版。
| 稳定版 | Windows 7 及以上 | <downloadbtn href="https://lunatranslator.org/Resource/DownloadLuna/x86_win7?doc=1"/> | <downloadbtn href="https://lunatranslator.org/Resource/DownloadLuna/x64_win7?doc=1"/> |
| 怀旧版 | Windows XP & Vista | <downloadbtn href="https://lunatranslator.org/Resource/DownloadLuna/x86_winxp?doc=1"/> | | 该版本仅用于支持提取仅能在XP虚拟机内运行的很老游戏的文本，功能残缺、不稳定、运行缓慢，一般不要使用。


## 启动

下载后解压到任意目录

::: warning
但请不要把软件放到**C:\Program Files**等特殊路径下，否则即使使用管理员权限，也可能无法保存配置和缓存文件，甚至无法运行。
:::

**LunaTranslator.exe** 会以普通模式启动 

**LunaTranslator_admin.exe** 会以管理员权限启动，部分游戏需要管理员权限才能HOOK，仅这时需要使用这个，其他时候普通模式启动即可。

**LunaTranslator_debug.bat** 会显示命令行窗口

## 常见错误

### 找不到重要组件

::: danger
有时会被杀毒软件杀掉，请添加信任并重新下载解压
:::

![img](https://image.lunatranslator.org/zh/cantstart/2.jpg) 

解决方法：关闭杀毒软件，无法关闭(如windows defender)则添加信任，然后重下。

注：为了实现HOOK提取游戏文本，需要将Dll注入到游戏，shareddllproxy32.exe/LunaHost32.dll等几个文件中实现了这些内容，因此特别容易被认为是病毒。软件目前由[Github Actions](https://github.com/HIllya51/LunaTranslator/actions)自动构建，除非Github服务器中毒了，否则不可能包含病毒，因此可以放心的添加信任。

::: details 对于windows defender，方法为：“病毒和威胁防护”->“排除项”->“添加或删除排除项”->“添加排除项”->“文件夹”，把Luna的文件夹添加进去
![img](https://image.lunatranslator.org/zh/cantstart/4.png) 
![img](https://image.lunatranslator.org/zh/cantstart/3.png) 
::: 

### Error/FileNotFoundError

如果没有预先添加好信任，有可能在软件运行一段时间后，部分必要组件才被杀毒软件删除。然后等到HOOK模式选取进程之后，报出这个错误。解决方法同上。

<img src="https://image.lunatranslator.org/zh/notfound.png" width=400>

### Error/PermissionError

如果软件被放到`C:\Program Files`等特殊文件夹，可能会无法正常运行。

<img src="https://image.lunatranslator.org/zh/cantstart/6.png" width=400>