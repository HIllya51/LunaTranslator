## 重要なコンポーネントが見つからない

![img](https://image.lunatranslator.org/zh/cantstart/2.jpg) 

解決方法：ウイルス対策ソフトを無効にする。無効にできない場合（例：Windows Defender）、信頼リストに追加してから再ダウンロードする。

注：ゲームテキストのHOOK抽出を実現するために、Dllをゲームに注入する必要があります。shareddllproxy32.exe/LunaHost32.dllなどのファイルはこれを実装しているため、特にウイルスと見なされやすいです。ソフトウェアは現在[Github Actions](https://github.com/HIllya51/LunaTranslator/actions)によって自動的にビルドされています。Githubサーバーが感染していない限り、ウイルスが含まれることはないため、信頼リストに安全に追加できます。

::: details Windows Defenderの場合、方法は：「ウイルスと脅威の防止」->「除外」->「除外の追加または削除」->「除外の追加」->「フォルダー」、Lunaのフォルダーを追加します
![img](https://image.lunatranslator.org/zh/cantstart/4.png) 
![img](https://image.lunatranslator.org/zh/cantstart/3.png) 
::: 

## エラー/PermissionError

ソフトウェアが`Program Files`などの特殊なフォルダーに配置されている場合、読み取りおよび書き込み権限がない可能性があります。管理者権限で実行してください。

<img src="https://image.lunatranslator.org/zh/cantstart/6.png" width=400>
