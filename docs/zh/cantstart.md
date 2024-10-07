## 无法启动软件？

#### **1. Error/ModuleNotFoundError**

如果你从旧版本直接覆盖更新到新版本，或者自动更新到新版本，旧的无效文件不会被删除，而且由于python的文件加载顺序，旧的文件被优先加载，导致无法加载新的文件，从而引发这个问题。

解决方法是：保留userconfig文件夹，删除其他文件后，重新下载解压。

<details>
  <summary>部分已内置解决的情况，不再会报错</summary>
  <img src="https://image.lunatranslator.org/zh/cantstart/1.png">
  <img src="https://image.lunatranslator.org/zh/cantstart/3.jpg">
</details>

#### **2. Error/PermissionError**

如果软件被放到`Program Files`等特殊文件夹，可能会没有读写权限。请使用管理员权限运行。

<img src="https://image.lunatranslator.org/zh/cantstart/6.png" width=400>

#### **3. 找不到重要组件**

<img src="https://image.lunatranslator.org/zh/cantstart/2.jpg">

解决方法：关闭杀毒软件，无法关闭(如windows defender)则添加信任，然后重下。

注：为了实现HOOK提取游戏文本，需要将Dll注入到游戏，shareddllproxy32.exe/LunaHost32.dll等几个文件中实现了这些内容，因此特别容易被认为是病毒。软件目前由[Github Actions](https://github.com/HIllya51/LunaTranslator/actions)自动构建，除非Github服务器中毒了，否则不可能包含病毒，因此可以放心的添加信任。



<details>
  <summary>对于windows defender，方法为：“病毒和威胁防护”->“排除项”->“添加或删除排除项”->“添加排除项”->“文件夹”，把Luna的文件夹添加进去</summary>
  <img src="https://image.lunatranslator.org/zh/cantstart/4.png">
  <img src="https://image.lunatranslator.org/zh/cantstart/3.png">
</details>