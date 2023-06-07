# YY-Thunks - 让兼容 Windows 更轻松
![license](https://img.shields.io/github/license/Chuyu-Team/YY-Thunks)
![downloads](https://img.shields.io/github/downloads/Chuyu-Team/YY-Thunks/total)
![contributors](https://img.shields.io/github/contributors-anon/Chuyu-Team/YY-Thunks)
![release](https://img.shields.io/github/v/release/Chuyu-Team/YY-Thunks?include_prereleases)
![nuget](https://img.shields.io/nuget/vpre/YY-Thunks)
[![Build&Test](https://github.com/Chuyu-Team/YY-Thunks/actions/workflows/Build&Test.yml/badge.svg)](https://github.com/Chuyu-Team/YY-Thunks/actions/workflows/Build&Test.yml)

## 关于 YY-Thunks

众所周知，从 Windows 的每次更新又会新增大量 API，这使得兼容不同版本的 Windows 
需要花费很大精力。导致现在大量开源项目已经不再兼容一些早期的 Windows 版本，比如
Windows XP RTM。

难道就没有一种快速高效的方案解决无法定位程序输入点的问题吗？

YY-Thunks（鸭船），存在的目的就是抹平不同系统的差异，编译时单纯添加一个 obj 
即可自动解决这些兼容性问题。让你兼容旧版本 Windows 更轻松！

[ [鸭船交流群 633710173](https://shang.qq.com/wpa/qunwpa?idkey=21d51d8ad1d77b99ea9544b399e080ec347ca6a1bc04267fb59cebf22644a42a) ]

### 原理

使用 `LoadLibrary` 以及 `GetProcAddress` 动态加载 API，不存在时做出补偿措施，
最大限度模拟原始 API 行为，让你的程序正常运行。

### 亮点

* 更快！更安全！`鸭船`内建2级缓存以及按需加载机制，同时自动加密所有函数指针，
  防止内存爆破攻击。最大程度减少不需要和不必要的 `LoadLibrary` 以及 
  `GetProcAddress` 调用以及潜在安全风险。
* 轻松兼容 Windows XP，让你安心专注于业务逻辑。
* 完全开源且广泛接受用户意见，希望大家能踊跃的创建 PR，为`鸭船`添砖加瓦。

## 使用方法

大家可以在以下方案中任选一种，但是我们优先推荐 NuGet 方案。

### NuGet（推荐）

1. 项目右键 “管理 NuGet 程序包”。
2. NuGet搜索框中输入：`YY-Thunks`，搜索后点击安装。
3. 项目右键 - 属性 - YY-Thunks 中，自行调整YY-Thunks等级，允许 Windows 2000, 
   Windows XP 以及 Windows Vista（默认）。
4. 重新编译代码

### 手工配置

1. 下载 [YY-Thunks-Binary](https://github.com/Chuyu-Team/YY-Thunks/releases)，
   然后解压到你的工程目录。
2. 【链接器】-【输入】-【附加依赖项】，添加 
   `objs\$(PlatformShortName)\YY_Thunks_for_WinXP.obj`。
3. 重新编译代码。

> 温馨提示：如果需要兼容 Vista，请选择 
  `objs\$(PlatformShortName)\YY_Thunks_for_Vista.obj`。

## 兼容性

### 支持的编译器

全平台ABI兼容。

* 所有Visual Studio版本均支持
  （比如：VC6.0、VS2008、VS2010、VS2015、VS2017、VS2019等等）。
* 所有运行库模式均支持（比如：`/MD`、`/MT`、`/MDd`、`/MTd`）。

### SDK版本要求
至少需要SDK 6.0（VS2008默认附带）

> 温馨提示：VC6.0、VS2005用户请注意，由于这些编译器默认附带的SDK版本太低。请先将SDK升级到6.0或者更高版本，然后再使用YY-Thunks，否则将发生链接失败！
高版本的SDK不影响对老系统的兼容性，请坐和放宽，安心升级。

### Thunks 清单

请参阅 [ThunksList.md](ThunksList.md)

## 更新日志

请参阅 [Changelog.md](https://github.com/Chuyu-Team/YY-Thunks/wiki)
