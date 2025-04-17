# 下载和启动

## 下载

### Windows 7 及以上系统

<a href="https://lunatranslator.org/Resource/DownloadLuna/64"> 64位 <img style="display:inline-block" src="https://img.shields.io/badge/download_64bit-blue"/> </a>

<a href="https://lunatranslator.org/Resource/DownloadLuna/32"> 32位 <img style="display:inline-block" src="https://img.shields.io/badge/download_32bit-blue"/> </a>

### Windows XP & Vista系统

<a href="https://lunatranslator.org/Resource/DownloadLuna/xp"> 32位 <img style="display:inline-block" src="https://img.shields.io/badge/download_32bit_XP-blue"/></a>

## 启动

下载后解压到任意目录

**LunaTranslator.exe** 会以普通模式启动 

**LunaTranslator_admin.exe** 会以管理员权限启动，部分游戏需要管理员权限才能HOOK，仅这时需要使用这个，其他时候普通模式启动即可。

**LunaTranslator_debug.exe** 会显示命令行窗口

## 无法启动软件

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

### Error/PermissionError

如果软件被放到`Program Files`等特殊文件夹，可能会没有读写权限。请使用管理员权限运行。

<img src="https://image.lunatranslator.org/zh/cantstart/6.png"  width=400>