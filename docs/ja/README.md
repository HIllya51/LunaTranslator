# ダウンロードと起動

## ダウンロード

### Windows 7 以降のシステム

<a href="https://lunatranslator.org/Resource/DownloadLuna/64"> 64ビット <img style="display:inline-block" src="https://img.shields.io/badge/download_64bit-blue"/> </a>

<a href="https://lunatranslator.org/Resource/DownloadLuna/32"> 32ビット <img style="display:inline-block" src="https://img.shields.io/badge/download_32bit-blue"/> </a>

### Windows XP & Vista システム

<a href="https://lunatranslator.org/Resource/DownloadLuna/xp"> 32ビット <img style="display:inline-block" src="https://img.shields.io/badge/download_32bit_XP-blue"/></a>

## 起動

ダウンロード後、任意のディレクトリにファイルを解凍します。

::: warning
ただし、**C:\Program Files** などの特別なパスにソフトウェアを配置しないでください。そうしないと、管理者権限があっても、構成やキャッシュファイルを保存したり、プログラムを実行したりできない可能性があります。
:::

- **LunaTranslator.exe** は通常モードで起動します。

- **LunaTranslator_admin.exe** は管理者権限で起動します。一部のゲームのフックには管理者権限が必要です。必要な場合のみ使用し、通常は通常モードで起動してください。

- **LunaTranslator_debug.bat** はコマンドラインウィンドウを表示します。

## ソフトウェアが起動しない

### 重要なコンポーネントが見つからない

::: danger
時々、ウイルス対策ソフトによってフラグが立てられることがあります。信頼リストに追加し、再度ダウンロードして解凍してください。
:::

![img](https://image.lunatranslator.org/zh/cantstart/2.jpg) 

解決方法：ウイルス対策ソフトを無効にする。無効にできない場合（例：Windows Defender）、信頼リストに追加してから再ダウンロードする。

注：ゲームテキストのHOOK抽出を実現するために、Dllをゲームに注入する必要があります。shareddllproxy32.exe/LunaHost32.dllなどのファイルはこれを実装しているため、特にウイルスと見なされやすいです。ソフトウェアは現在[Github Actions](https://github.com/HIllya51/LunaTranslator/actions)によって自動的にビルドされています。Githubサーバーが感染していない限り、ウイルスが含まれることはないため、信頼リストに安全に追加できます。

::: details Windows Defenderの場合、方法は：「ウイルスと脅威の防止」->「除外」->「除外の追加または削除」->「除外の追加」->「フォルダー」、Lunaのフォルダーを追加します
![img](https://image.lunatranslator.org/zh/cantstart/4.png) 
![img](https://image.lunatranslator.org/zh/cantstart/3.png) 
::: 

### エラー/PermissionError

ソフトウェアが`C:\Program Files`などの特殊なフォルダーに配置されている場合、正常に動作しない可能性があります。

<img src="https://image.lunatranslator.org/zh/cantstart/6.png" width=400>
