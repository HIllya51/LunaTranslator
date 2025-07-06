# Download and Launch

## Download

| OS | 32-bit | 64-bit | Description |
| - | - | - | - |
| Windows 10 & 11 |  | <downloadbtn href="https://lunatranslator.org/Resource/DownloadLuna/x64_win10?doc=1"/> | This version only supports newer Windows 10 versions to achieve higher performance, updated system features, and a lower virus false positive rate.
| Windows 7 or later | <downloadbtn href="https://lunatranslator.org/Resource/DownloadLuna/x86_win7?doc=1"/> | <downloadbtn href="https://lunatranslator.org/Resource/DownloadLuna/x64_win7?doc=1"/> | |
| Windows XP & Vista | <downloadbtn href="https://lunatranslator.org/Resource/DownloadLuna/x86_winxp?doc=1"/> | | This version only supports text extraction from very old games that can only run in XP VMs. It has limited functionality, is unstable, and runs slowly. Not recommended for regular use.


## Launch

After downloading, extract the files to any directory.

::: warning
But please do not put the software in special paths such as **C:\Program Files**, otherwise, even with administrator privileges, you may not be able to save configuration and cache files, or even run the program.
:::

- **LunaTranslator.exe** will start in normal mode.

- **LunaTranslator_admin.exe** will start with administrator privileges, which is required for hooking some games; use this only when necessary, otherwise start in normal mode.

- **LunaTranslator_debug.bat** will display a command-line window.


## Common Errors

::: danger
Sometimes it may be flagged by antivirus software. Please add it to the trust list and re-download and extract.
:::

### Missing Important Components

![img](https://image.lunatranslator.org/zh/cantstart/2.jpg) 

Solution: Close antivirus software. If it cannot be closed (such as Windows Defender), add it to the trust list and then re-download.

Note: To achieve HOOK extraction of game text, it is necessary to inject Dll into the game. Files such as shareddllproxy32.exe/LunaHost32.dll implement this, and therefore are particularly likely to be considered as viruses. The software is currently automatically built by [Github Actions](https://github.com/HIllya51/LunaTranslator/actions). Unless the Github server is infected, it is impossible to contain viruses, so it can be safely added to the trust list.

::: details For Windows Defender, the method is: “Virus & threat protection” -> “Exclusions” -> “Add or remove exclusions” -> “Add an exclusion” -> “Folder”, add Luna's folder to it
![img](https://image.lunatranslator.org/zh/cantstart/4.png) 
![img](https://image.lunatranslator.org/zh/cantstart/3.png) 
::: 

### Error/FileNotFoundError

If trust isn't pre-established, some essential components might get deleted by antivirus software after the program has been running for a while. Then when selecting a process in HOOK mode, this error occurs. The solution is the same as above.

<img src="https://image.lunatranslator.org/zh/notfound.png" width=400>

### Error/PermissionError

If the software is placed in special folders such as `C:\Program Files`, it may not work properly.

<img src="https://image.lunatranslator.org/zh/cantstart/6.png"  width=400>
