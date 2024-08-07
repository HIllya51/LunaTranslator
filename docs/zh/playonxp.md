## 在XP虚拟机上玩古老游戏并提取文本翻译

**1、 在虚拟机中使用ntleas转区运行**

如果游戏乱码，可以使用[ntleas](https://github.com/zxyacb/ntlea)的x86\ntleas.exe来转区运行游戏。打开cmd切换到ntleas\x86文件夹，运行`ntleas.exe "游戏绝对路径.exe"`。

![img](https://image.lunatranslator.org/zh/playonxp/ntleas.png)

**2、在虚拟机中使用LunaHook windows xp专用版提取文本**

下载[LunaHook](https://github.com/HIllya51/LunaHook/releases)中的`Release_Chinese_winxp.zip`，复制到虚拟机中运行。选择游戏的进程，选择游戏文本。然后，在设置中，激活`复制到剪贴板`。

![img](https://image.lunatranslator.org/zh/playonxp/image.png)


**3、在宿主机中进行翻译**

对虚拟机设置共享剪贴板，将虚拟机内的剪贴板内容传到宿主机内。
![img](https://image.lunatranslator.org/zh/playonxp/copy.png)

在宿主机中运行LunaTranslator，将文本输入从`HOOK`切换到`剪贴板`
![img](https://image.lunatranslator.org/zh/playonxp/host.png)

<hr>

最终效果如下：
![img](https://image.lunatranslator.org/zh/playonxp/effect.png)