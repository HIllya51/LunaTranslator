# HOOK設定

## 共通設定

1. #### コードページ

    ::: info
    この設定は、ゲームから抽出されたテキストが**HOOKエンジン内でエンコードが指定されていないマルチバイト文字列**の場合にのみ意味があります。HOOKエンジン内で既にコードページが指定されている場合、またはテキストが**ワイド文字列**または**UTF32**文字列の場合、この設定には意味がありません。
    :::
    この設定は通常変更する必要はありません。古いエンジン（例：Yuris）の公式中国語版でGBK/BIG5/UTF8が使用されている場合にのみ必要です。正しいテキストが見つからない場合は、直接[issue](https://lunatranslator.org/Resource/game_support)を送信してください。この設定を変更することは通常無駄です。

1. #### リフレッシュ遅延

    以下のいずれかの状況に直面した場合：

        1. テキストが1文字または2文字ずつ抽出される。
        2. テキストが行ごとに抽出され、前の行を押し出し、最後の行のみが表示される。
        3. テキストは正しいが、非常に遅く抽出される。

    このオプションを調整する必要があります。

    **1と2**の場合、ゲームテキストの表示が遅すぎて、リフレッシュ遅延が低すぎるため、1文字または2文字、または1行のテキストが抽出されるたびにすぐにリフレッシュされます。この場合、**リフレッシュ遅延を増やす**か、ゲームのテキスト表示速度を上げる必要があります。

    **3**の場合、**リフレッシュ遅延を適度に減らす**ことができますが、**1と2**の状況を引き起こさないように注意してください。

1. #### 最大バッファ長

    時々、テキストが止まらずに繰り返しリフレッシュされることがあります。リフレッシュ遅延が高く、減らすことができない場合、バッファがいっぱいになるか、テキストがリフレッシュを停止するまでテキストを受信し続けます（通常、ゲームがフォーカスを失うときに停止するため、通常はバッファがいっぱいになるまで待ちます）。

    この問題を解決するために、バッファ長を適度に減らすことができますが、バッファ長が実際のテキスト長よりも短くならないように注意してください。

1. #### 最大キャッシュテキスト長

    受信した履歴テキストはキャッシュされます。テキスト選択ウィンドウでテキスト項目の内容を表示する場合、履歴キャッシュテキストがクエリされます。テキスト項目が多すぎるか、テキストが繰り返しリフレッシュされると、キャッシュされたテキストが多すぎて、テキストの表示が遅くなります（時には表示していないときでも）。実際、ここでキャッシュされているテキストのほとんどは無駄です。有用な履歴テキストは履歴テキストウィンドウで表示できます。この値を任意に下げることができます（デフォルトは1000000ですが、1000に下げることができます）。

## 専用ゲーム設定

1. #### 追加のフック
    1. #### Win32ユニバーサルフック
        有効にすると、Win32のユニバーサル関数フックがゲームに注入され、GDI関数、D3DX関数、および文字列関数が含まれます。
        フックを注入しすぎるとゲームが遅くなる可能性があるため、これらのフックはデフォルトでは注入されません。
        正しいテキストを抽出できない場合は、これらのオプションを有効にしてみてください。
    1. #### 特殊コード
        **特殊コードを挿入**し、**特殊コードのテキストを選択**した場合にのみ、この特殊コードが記録されます。次回ゲームを開始すると、この特殊コードが自動的に挿入されます。この設定には、以前に記録されたすべての特殊コードが記録されており、特殊コードを追加または削除できます。

1. #### 遅延注入
    ゲームでフックする必要がある位置がdll上にあり、ゲームが少し実行された後にのみロードされる場合があります。dllがロードされるまで待ってから注入を行う必要があります。

1. #### 専用HOOK設定
    設定インターフェース -> HOOK設定で行われた設定はデフォルト設定です。ゲームに専用のHOOK設定が指定されていない場合、デフォルト設定が使用されます。
    
    ゲームに専用のHOOK設定を行うには、**ゲーム管理**に移動し、**ゲーム設定**インターフェースを開き、ゲーム設定選択カードのHOOKサブタブに切り替えます。**デフォルトに従う**のチェックを外してから、ゲームに専用のHOOK設定を行うことができます。

    ::: details
    ![img](https://image.lunatranslator.org/zh/gamesettings/1.jpg)

    ![img](https://image.lunatranslator.org/zh/gamesettings/2.png)
    :::