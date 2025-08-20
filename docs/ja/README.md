# ダウンロード ＆ 起動 ＆ 更新

## ダウンロード

| OS | 64ビット |
| - | - |
| Windows 10 & 11 | <downloadbtn href="https://lunatranslator.org/Resource/DownloadLuna/x64_win10?doc=1"/> |

::: details 旧版OS互換版  

>[!WARNING]  
これらのバージョンは性能が劣り、動作が不安定で、一部の機能や特徴が欠けており、ウイルス対策ソフトに誤検知されやすくなっています。特別な必要がない場合は使用しないことをお勧めします。

| OS | 32ビット | 64ビット |
| - | - | - |
| Windows 7 以降 | <downloadbtn href="https://lunatranslator.org/Resource/DownloadLuna/x86_win7?doc=1"/> | <downloadbtn href="https://lunatranslator.org/Resource/DownloadLuna/x64_win7?doc=1"/> |
| Windows XP & Vista | <downloadbtn href="https://lunatranslator.org/Resource/DownloadLuna/x86_winxp?doc=1"/> | |

:::

## 起動

ダウンロード後、任意のディレクトリにファイルを解凍します。

::: warning
ただし、**C:\Program Files** などの特別なパスにソフトウェアを配置しないでください。そうしないと、管理者権限があっても、構成やキャッシュファイルを保存したり、プログラムを実行したりできない可能性があります。
:::

- **LunaTranslator.exe** は通常モードで起動します。

- **LunaTranslator_admin.exe** は管理者権限で起動します。一部のゲームのフックには管理者権限が必要です。必要な場合のみ使用し、通常は通常モードで起動してください。

- **LunaTranslator_debug.bat** はコマンドラインウィンドウを表示します。

## 更新

デフォルトでは自動的に更新されます。自動更新に失敗した場合、手動で更新できます。

手動で更新したい場合は、新しいバージョンをダウンロードし、前のディレクトリに解凍して上書きするだけです。

削除して再ダウンロードしたい場合は、userconfigフォルダを削除しないように注意してください。削除すると以前の設定が失われます！！！

## よくあるエラー

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

### Error/FileNotFoundError

事前に信頼リストに追加していない場合、ソフトウェアがしばらく動作した後で必要なコンポーネントがウイルス対策ソフトに削除される可能性があります。その後、HOOKモードでプロセスを選択した際にこのエラーが発生します。解決方法は上記と同じです。

<img src="https://image.lunatranslator.org/zh/notfound.png" width=400>

### Error/PermissionError

ソフトウェアが`C:\Program Files`などの特殊なフォルダーに配置されている場合、正常に動作しない可能性があります。

<img src="https://image.lunatranslator.org/zh/cantstart/6.png" width=400>
