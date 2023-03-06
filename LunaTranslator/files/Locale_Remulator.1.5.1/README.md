# Locale Remulator

[![license](https://img.shields.io/github/license/InWILL/Locale_Remulator.svg)](https://www.gnu.org/licenses/lgpl-3.0.en.html)
[![GitHub all releases](https://img.shields.io/github/downloads/InWILL/Locale_Remulator/total)](https://github.com/InWILL/Locale_Remulator/releases/latest)

### English | [简体中文](#english--%E7%AE%80%E4%BD%93%E4%B8%AD%E6%96%87-1)

System Region and Language Simulator.

The project is similar with Locale-Emulator, but LE doesn't support 64-bit application, so I base on Detours to start a new project.

The most important reason is that Japan MapleStory will become 64-bit.

## Download

Download available at <https://github.com/InWILL/Locale_Remulator/releases/latest>.

## Getting Started

### Prerequisites

* [.NET Framework 4.8](https://dotnet.microsoft.com/en-us/download/dotnet-framework/net48)
* [Microsoft Visual C++ Redistributable](https://docs.microsoft.com/en-US/cpp/windows/latest-supported-vc-redist?view=msvc-170)

### Install

Run `LRInstaller.exe` to install Locale_Remulator.

If you installed old version in the past, please restart explorer or reboot system after installing new version.

### Uninstall

Run `LRInstaller.exe` to remove Locale_Remulator.

### Usage Method 1

Select a `*.exe` application and right click, there will show a section named "Locale Remulator x64", and choose what config you want.

### Usage Method 2

Run `LREditor.exe` and click `Shortcut` button, choose what config and application you want to run, there will generate a lnk file in the same path. You could use this lnk file to use LR conveniently without right click menu.

## Built With

* [Detours](https://github.com/microsoft/Detours) - Used to hook ANSI/Unicode functions
* [SharpShell](https://github.com/dwmkerr/sharpshell) - Used to generate right-click menu

## Deployment

Choose solution Platform x86 or x64.

Copy these files in the same directory.

```
    LREditor.exe
    LRHookx32.dll
    LRHookx64.dll
    LRInstaller.exe
    LRProc.exe
    LRSubMenus.dll
    ServerRegistrationManager.exe
    SharpShell.dll
    System.Drawing.Common.dll
```

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/InWILL/Locale_Remulator/tags). 

## Contributors

* **InWILL** - *Initial work* - [InWILL](https://github.com/InWILL)
* **lintx** - [lintx](https://github.com/lintx)

See also the list of [contributors](https://github.com/InWILL/Locale_Remulator/graphs/contributors) who participated in this project.

## License

This project is licensed under the LGPL-3.0 License - see the [LICENSE](LICENSE) file for details.

## Q&A

### LRHookx64.dll The specified module could not be found

Please install [Microsoft Visual C++ Redistributable](https://docs.microsoft.com/en-US/cpp/windows/latest-supported-vc-redist?view=msvc-170).

### VCRUNTIME140_1.dll was not found

Please install [Microsoft Visual C++ Redistributable](https://docs.microsoft.com/en-US/cpp/windows/latest-supported-vc-redist?view=msvc-170).

### The Application was Unable to Start Correctly (0xc000007b)

Please update Locale_Remulator to 1.4.3-beta.2+


### [English](#english--%E7%AE%80%E4%BD%93%E4%B8%AD%E6%96%87) | 简体中文

系统区域和语言模拟器。

该项目与Locale-Emulator类似，但LE不支持64位应用程序，所以我基于Detours开始一个新项目。

最重要的原因是日服冒险岛将变成64位。

## 下载

可在 <https://github.com/InWILL/Locale_Remulator/releases/latest> 下载。

## 入门

### 安装要求

* [.NET Framework 4.8](https://dotnet.microsoft.com/en-us/download/dotnet-framework/net48)
* [Microsoft Visual C++ Redistributable](https://docs.microsoft.com/en-US/cpp/windows/latest-supported-vc-redist?view=msvc-170)

### 安装

运行 `LRInstaller.exe` 来安装 Locale_Remulator。

如果您以前安装过旧版本，请在安装新版本后重新启动资源管理器或重新启动系统。

### 卸载

运行 `LRInstaller.exe` 以卸载 Locale_Remulator。

### 使用方法一

选择一个`*.exe`应用程序并右键单击，将显示一个名为“Locale Remulator x64”的部分，然后选择您想要的配置。

### 使用方法二

运行`LREditor.exe`并点击`Shortcut`按钮，选择你要运行的配置和应用程序，会在相同路径下生成一个lnk文件。您可以使用此 lnk 文件方便地使用 LR，无需右键菜单。

## 内置

* [Detours](https://github.com/microsoft/Detours) - 用于挂钩 ANSI/Unicode 函数
* [SharpShell](https://github.com/dwmkerr/sharpshell) - 用于生成右键菜单

## 部署

选择解决方案平台 x86 或 x64进行编译。

将这些文件复制到同一目录中。

```
    LREditor.exe
    LRHookx32.dll
    LRHookx64.dll
    LRInstaller.exe
    LRProc.exe
    LRSubMenus.dll
    ServerRegistrationManager.exe
    SharpShell.dll
    System.Drawing.Common.dll
```

## 版本控制

我们使用 [SemVer](http://semver.org/) 进行版本控制。有关可用版本，请参阅 [此存储库上的标签](https://github.com/InWILL/Locale_Remulator/tags)。

## 使用许可

该项目在 LGPL-3.0 许可下获得许可 - 请参阅 [LICENSE](LICENSE) 文件了解详细信息

## 常见问题

### LRHookx64.dll 找不到指定模块

请安装 [Microsoft Visual C++ Redistributable](https://docs.microsoft.com/en-US/cpp/windows/latest-supported-vc-redist?view=msvc-170)。

### 因为计算机中丢失VCRUNTIME140_1.dll

请安装 [Microsoft Visual C++ Redistributable](https://docs.microsoft.com/en-US/cpp/windows/latest-supported-vc-redist?view=msvc-170)。

### 应用程序无法正常启动(0xc000007b)

请升级到Locale_Remulator.1.4.3-beta.2以上。

## 捐赠

![收款码405x250](https://user-images.githubusercontent.com/13805009/185916994-6a17d723-27f6-4eec-8571-ad869ad99cf0.png)
