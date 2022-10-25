# Textractor

[English](README.md) ● [Español](README_ES.md) ● [简体中文](README_SC.md) ● [Русский](README_RU.md) ● [한국어](README_KR.md) ● [ภาษาไทย](README_TH.md) ● [Français](README_FR.md) ● [Italiano](README_IT.md) ● [日本語](README_JP.md) ● [Bahasa Indonesia](README_ID.md) ● [Português](README_PT.md)

## 概述

**Textractor** (曾用名: NextHooker) 是一个基于 [ITHVNR](https://web.archive.org/web/20160202084144/http://www.hongfire.com/forum/showthread.php/438331-ITHVNR-ITH-with-the-VNR-engine), 为 Windows/Wine 开发的开源 x86/x64 文本提取器.<br>

![它工作起来的样子](screenshot.png)

## 下载

Textractor 的发行版可以在[这里](https://github.com/Artikash/Textractor/releases)找到.

老版 ITHVNR 可以在[这里](https://github.com/mireado/ITHVNR/releases)找到.

## 特点

- 高度可扩展
- 自动从很多游戏中提取 (包括一些没有被 VNR 支持的!)
- 通过 /H "hook" 码提取文本 (支持大多数 AGTH 码)
- 使用 /R "read" 码直接抽取文本

## 扩展

通过我的[扩展示例项目](https://github.com/Artikash/ExampleExtension)查看如何构建扩展.<br>
通过 extensions 文件夹查看扩展能够做什么.

## 贡献

欢迎一切贡献！如有任何关于代码的疑问，请向 akashmozumdar@gmail.com 发邮件.<br>
你应当使用创建 PR 的标准过程 (分岔 (fork), 分支 (branch), 提交变化, 创建从你的分支到我的 master 分支的 PR).<br>
提供翻译贡献很简单: 只需翻译 text.cpp 中的字符串和这份 README 即可.

## 编译

编译 *Textractor* 前, 你应当获取支持 CMake 的 Visual Studio, 以及 Qt 5.13 版.<br>
之后就可以使用 Visual Studio 打开文件夹, 然后构建. 运行 Textractor.exe.

## 项目架构

宿主 (位于 host 文件夹) 向目标进程注入 texthook.dll (由 texthook 文件夹创建) 并通过两个管道文件互联.<br>
宿主向 hostPipe 写入, texthook 向 hookPipe 写入.<br>
texthook 等待管道连接, 之后向一些文本输出函数 (如 TextOut, GetGlyphOutline) 注入一系列指令, 使得它们的输入被沿着管道发送.<br>
其它关于钩子的信息通过一个被 TextHook 类保有引用的文件视图 (曾用名: 段对象) 共享.<br>
之后, 宿主通过管道接收到的文本在传回 GUI 前被简单处理.<br>
最后, GUI 在显示文本前将其分发给扩展.

## [开发者](docs/CREDITS.md)
