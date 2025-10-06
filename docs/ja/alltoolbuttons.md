# ツールボタン

::: info
すべてのボタンは「表示設定」->「ツールボタン」で非表示または表示にできます。

すべてのボタンは自由に位置を調整できます。ボタンは「左」「中央」「右」の整列グループに設定でき、相対位置の調整は整列グループ内で制限されます。

ボタンの色は「表示設定」->「インターフェース設定」->「ツールバー」->「ボタンの色」でカスタマイズできます。

一部のボタンには2つのアイコンがあり、2つの異なる状態を示します。一部のボタンには1つのアイコンしかありませんが、異なる色を使用して異なる状態を表します。
:::

<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.6.0/css/all.min.css"> 

<style>
    i{
        color:blue;
        width:20px;
    }
    .fa-icon {
  visibility: hidden;
}
.btnstatus2{
    color:deeppink;
}
</style>

1. #### <i class="fa fa-rotate-right"></i> <i class="fa fa-icon fa-rotate-right"></i> 手動実行 {#anchor-retrans}
    実際の意味は、現在のテキスト入力ソースから1回入力を読み取り、翻訳を実行することです。

    たとえば、現在のモードがOCRの場合、再度OCRを実行します。

1. #### <i class="fa fa-forward"></i> <i class="btnstatus2 fa fa-forward"></i> オートモード {#anchor-automodebutton}
    実際の意味は、現在のテキスト入力ソースからの自動読み取りを一時停止/再開することです。

    たとえば、現在のモードがHOOKの場合、ゲームテキストの読み取りを一時停止します。現在のモードがOCRの場合、自動画像認識を一時停止します。現在のモードがクリップボードモードの場合、クリップボードの自動読み取りを一時停止します。

1. #### <i class="fa fa-gear"></i> <i class="fa fa-icon fa-rotate-right"></i> 設定を開く {#anchor-setting}
    該当なし
1. #### <i class="fa fa-file"></i> <i class="fa fa-icon fa-rotate-right"></i> クリップボードから読み込み {#anchor-copy_once}
    実際の意味は、現在のデフォルトのテキスト入力ソースに関係なく、クリップボードから1回テキストを読み取り、後続の翻訳/tts/...プロセスに渡すことです。

    右クリックすると、読み込んだテキストが現在のテキストの後に追加されます。
1. #### <i class="fa fa-futbol"></i> <i class="fa fa-icon fa-rotate-right"></i> ゲーム設定 {#anchor-open_game_setting}
    HOOKモードでゲームに接続している場合、またはOCRモードでゲームウィンドウにバインドしている場合、このボタンを使用して現在のゲームの設定ウィンドウを直接開くことができます。
1. #### <i class="fa fa-mouse-pointer"></i> <i class="btnstatus2 fa fa-mouse-pointer"></i> マウス透過 {#anchor-mousetransbutton}
    このボタンを有効にすると、翻訳ウィンドウはマウスクリックに反応せず、クリックイベントを下層のウィンドウに渡します。

    翻訳ウィンドウをゲームウィンドウのテキストボックスの上に配置し、このボタンを有効にすると、翻訳ウィンドウではなくゲームのテキストボックスを直接クリックできます。

    マウスが**マウススルーウィンドウボタンとその左右の1つのボタンの領域**に移動すると、自動的にスルーを終了してツールボタンを使用できます。領域外に移動すると、自動的にスルーが復元されます。

1. #### <i class="fa fa-lightbulb"></i> <i class="btnstatus2 fa fa-lightbulb"></i> 背景ウィンドウを透明化 {#anchor-backtransbutton}
    このボタンの機能は、翻訳ウィンドウの不透明度をワンクリックで0に切り替えることです。このスイッチは、元の不透明度設定を忘れることはありません。
    
1. #### <i class="fa fa-lock"></i> <i class="btnstatus2 fa fa-unlock"></i> ツールバーを固定 {#anchor-locktoolsbutton}
    アクティブ化後、ツールバーは常に表示されます。

    ツールバーがロックされていない場合、マウスが外れるとツールバーは自動的に非表示になり、ウィンドウ内にマウスが入るとツールバーが再表示されます。マウスの右クリックでツールバーのロックを解除した場合、**ロックツールバーボタンとその左右のボタンの領域**にマウスが入った時のみ、ツールバーが再表示されます。

    ツールバーがロックされていない場合、`マウススルーウィンドウ`が有効になっている場合、マウスが**マウススルーウィンドウボタンとその左右の1つのボタンの領域**に移動すると、ツールバーが表示されます。それ以外の場合、マウスが翻訳ウィンドウに入ると、ツールバーが表示されます。

    現在、ウィンドウ効果（Aero/Arylic）を使用しており、ツールバーがロックされていない場合、ツールバーはテキストエリアのz軸上の領域にあり、y軸上のテキストエリアの上にはありません。これは、Windowsのため、ウィンドウ効果を使用している場合、ツールバーを非表示にするだけでなく、ウィンドウの高さを縮小しないと、非表示のツールバーがアクリル/Aero背景でレンダリングされ続け、ツールバーの位置に空白領域が表示されるためです。
1. #### <i class="fa fa-link"></i> <i class="fa fa-icon fa-rotate-right"></i> ゲームを選択 {#anchor-selectgame}
    **このボタンはHOOKモードでのみ使用可能です**

    ボタンをクリックすると、ゲームプロセス選択ウィンドウが表示され、HOOKするゲームプロセスを選択できます。
1. #### <i class="fa fa-tasks"></i> <i class="fa fa-icon fa-rotate-right"></i> テキストを選択 {#anchor-selecttext}
    **このボタンはHOOKモードでのみ使用可能です**

    ボタンをクリックすると、ゲームテキスト選択ウィンドウが表示され、HOOKされたテキストのどれを翻訳するかを選択できます。

    ただし、プロセスを選択した後、テキスト選択ウィンドウは自動的に表示されます。このボタンは、選択したテキストを置き換えたり、設定を変更したりするために使用されます。
1. #### <i class="fa fa-crop"></i> <i class="fa fa-icon fa-rotate-right"></i> OCR範囲を選択 {#anchor-selectocrrange}
    **このボタンはOCRモードでのみ使用可能です**

    OCRモードでは、OCRエリアを選択するか、OCRエリアを変更するか、`OCR設定` -> `その他` -> `複数エリアモード`を有効にして新しいOCRエリアを追加します。

    右ボタンを押すと、選択されたすべての範囲がクリアされ、新しいエリアが追加されます。
1. #### <i class="fa fa-square"></i> <i class="fa fa-icon fa-rotate-right"></i> 範囲枠の表示/非表示 {#anchor-hideocrrange}
    **このボタンはOCRモードでのみ使用可能です**

    OCR範囲が選択されていない場合、このボタンを使用してOCR範囲を表示し、最後に選択されたOCRに自動的に設定されます。

    右ボタンを押すと、選択されたすべての範囲がクリアされます。
1. #### <i class="fa fa-crop"></i> <i class="fa fa-icon fa-rotate-right"></i> OCRを実行 {#anchor-ocr_once}
    このボタンは`クリップボードを読み取る`と似ており、現在のデフォルトのテキスト入力ソースに関係なく、最初にOCR範囲を選択し、次に1回OCRを実行し、その後翻訳プロセスを進めます。

    このボタンは通常、HOOKモードで選択肢に遭遇したときに、一時的にOCRを使用して選択肢を翻訳するために使用されます。または、OCRモー���で一時的に新しい位置を認識するために使用されます。

1. #### <i class="fa fa-spinner"></i> <i class="fa fa-icon fa-rotate-right"></i> OCRを再実行 {#anchor-ocr_once_follow}
    `1回OCRを実行`を使用した後、このボタンを使用して、元の位置で再度OCRを実行し、認識エリアを再選択する必要はありません。
    
1. #### <i class="fa fa-book"></i> <i class="fa fa-icon fa-rotate-right"></i> 翻訳前の置換 {#anchor-noundict_direct}
1. #### <i class="fa fa-book"></i> <i class="fa fa-icon fa-rotate-right"></i> 固有名詞翻訳 {#anchor-noundict}
1. #### <i class="fa fa-won"></i> <i class="fa fa-icon fa-rotate-right"></i> 翻訳結果の修正 {#anchor-fix}
    上記の3つのボタンは、翻訳最適化設定ウィンドウを迅速に開いて新しい指定用語を追加するために使用されます。

    マウスの左クリック時、バインドされたゲーム（HOOKリンクゲーム/クリップボード、OCRバインドウィンドウ）がある場合、ゲーム専用の辞書設定を開きます。それ以外の場合は、グローバルな辞書設定を開きます。

    マウスの右クリック時、必ずグローバルな辞書設定を開きます。
1. #### <i class="fa fa-minus"></i> <i class="fa fa-icon fa-rotate-right"></i> トレイに最小化 {#anchor-minmize}
    該当なし
1. #### <i class="fa fa-times"></i> <i class="fa fa-icon fa-rotate-right"></i> 終了 {#anchor-quit}
    該当なし
1. #### <i class="fa fa-hand-paper"></i> <i class="fa fa-icon fa-rotate-right"></i> 移動 {#anchor-move}
    翻訳ウィンドウをドラッグします。

    実際には、ボタンバーにボタンがない場合、追加の空白領域があり、自由にドラッグできます。このボタンはドラッグ位置を予約するためのものです。
1. #### <i class="fa fa-compress"></i> <i class="fa fa-expand"></i> ウィンドウ拡大縮小 {#anchor-fullscreen}
    ゲームウィンドウをバインド後、ゲームウィンドウに内蔵のMagpieを使用してワンクリックでスケーリングが可能です。

    左クリックでウィンドウスケーリング、右クリックでフルスクリーンスケーリングを行います。

1. #### <i class="fa fa-camera"></i> <i class="fa fa-icon fa-rotate-right"></i> ウィンドウスクリーンショット {#anchor-grabwindow}
    ゲームウィンドウをバインド後、バインドされたウィンドウのスクリーンショットを撮ることができます（デフォルトではGDIとWinrtの2枚が撮られ、どちらも失敗する可能性があります）。Magpieでスケーリング中使用中の場合は、拡大されたウィンドウも撮影されます。

    左クリックすると、スクリーンショットがファイルに保存され、右クリックすると、スクリーンショットがクリップボードに保存されます。中ボタンはゲーム内のオーバーレイレイヤを開くためです。

1. #### <i class="fa fa-volume-off"></i> <i class="btnstatus2 fa fa-volume-up"></i> ゲームをミュート {#anchor-muteprocess}
    ゲームウィンドウをバインドした後、ワンクリックでゲームをミュートにできます。システムの音量ミキサーでゲームをミュートにする手間が省けます。
1. #### <i class="fa fa-eye"></i> <i class="btnstatus2 fa fa-eye-slash"></i> 原文の表示/非表示 {#anchor-showraw}
    原文を表示するかどうかを切り替えます。すぐに反映されます。

1. #### <i class="fa fa-toggle-on"></i> <i class="btnstatus2 fa fa-toggle-off"></i> 翻訳の表示/非表示 {#anchor-showtrans}
    翻訳を使用するかどうかを切り替えます。これは翻訳のマスタースイッチです。オフにすると、翻訳は実行されません。

    すでに翻訳が実行されている場合、オフにすると翻訳結果が非表示になり、再度オンにすると現在の翻訳結果が再表示されます。

    翻訳が実行されていない場合、非表示から表示に切り替えると、現在の文の翻訳がトリガーされます。

1. #### <i class="fa fa-music"></i> <i class="fa fa-icon fa-rotate-right"></i> 音声読み上げ {#anchor-langdu}
    ボタンを左クリックすると、現在のテキストの音声合成が実行されます。
    
    ボタンを右クリックすると、音読が中断されます。
  
    この音読は`スキップ`を無視します（`音声設定`で現在のテキストターゲットが`スキップ`として一致している場合、ボタンを使用して音読すると、スキップを無視して強制的に音読します）。
1. #### <i class="fa fa-copy"></i> <i class="fa fa-icon fa-rotate-right"></i> クリップボードにコピー {#anchor-copy}
    現在抽出されたテキストを1回クリップボードにコピーします。自動的にクリップボードに抽出したい場合は、`テキスト入力` → `クリップボード` → `自動出力` → `自動でテキストを出力`を有効にする必要があります。
1. #### <i class="fa fa-rotate-left"></i> <i class="fa fa-icon fa-rotate-right"></i> 履歴テキストの表示/非表示 {#anchor-history}
    履歴テキストのウィンドウを開くまたは閉じます。
1. #### <i class="fa fa-gamepad"></i> <i class="fa fa-icon fa-rotate-right"></i> ゲーム管理 {#anchor-gamepad_new}
    ゲーム管理インターフェースを開く。
1. #### <i class="fa fa-edit"></i> <i class="fa fa-icon fa-rotate-right"></i> 編集 {#anchor-edit}
    現在抽出されたテキストを編集するための編集ウィンドウを開く。

    このウィンドウでは、テキストを変更してから翻訳を実行することができます。または、自分で入力した任意のテキストを翻訳することができます。
1. #### <i class="fa fa-edit"></i> <i class="fa fa-icon fa-rotate-right"></i> 編集 翻訳履歴 {#anchor-edittrans}
    現在のゲームの翻訳履歴編集ウィンドウを開く。
1. #### <i class="fa fa-download"></i> <i class="fa fa-icon fa-rotate-right"></i> Ctrlキーをシミュレート {#anchor-simulate_key_ctrl}
1. #### <i class="fa fa-download"></i> <i class="fa fa-icon fa-rotate-right"></i> Enterキーをシミュレート {#anchor-simulate_key_enter}
    上記と同様に、ゲームウィンドウにキー押下をシミュレートして送信します。ストリーミング/タブレットを使用する場合に効果があります。
1. #### <i class="fa fa-list-ul"></i> <i class="fa fa-icon fa-rotate-right"></i> メモ {#anchor-memory}
    現在プレイしているゲームのメモウィンドウを開く。

    左クリックすると、現在のゲームのメモが開きます。右クリックするとグローバルメモが開きます。
1. #### <i class="fab fa-windows"></i> <i class="btnstatus2 fab fa-windows"></i> ウィンドウをバインド （クリックでキャンセル） {#anchor-bindwindow}
    **このボタンは非常に重要で、多くの機能はこのボタンを設定してから使用できます**

    ゲームウィンドウをバインドした後、`ウィンドウのスケーリング` `ウィンドウのスクリーンショット` `ゲームミュート`、`ゲームウィンドウに従う` -> `ゲームがフォーカスを失ったときにピンを解除`および`ゲームウィンドウの移動と同期`、およびゲーム時間の記録などが利用可能になります。
    HOOK/OCR/クリップボードモードに関係なく、このボタンは使用できます。

    HOOKモードでは、接続されたゲームに基づいて自動的にゲームウィンドウをバインドしますが、このボタンを使用して他のウィンドウを再選択することもできます。

    OCRモードでは、ウィンドウをバインドした後、ゲームウィンドウの移動に同期してOCRエリアと範囲ボックスを自動的に移動させることもできます。
    OCR/クリップボードモードでは、ウィンドウをバインドした後、HOOKモードと同様に現在のゲームのゲーム設定にリンクし、現在のゲーム専用の翻訳最適化辞書などを使用できます。

1. #### <i class="fa fa-neuter"></i> <i class="btnstatus2 fa fa-neuter"></i> ウィンドウを最前面に {#anchor-keepontop}
    翻訳ウィンドウの常に最前面をキャンセル/有効にする。
    
1. #### <i class="fa fa-i-cursor"></i> <i class="btnstatus2 fa fa-i-cursor"></i> 選択可能 {#anchor-selectable}
    翻訳ウィンドウのテキストエリア内のテキストを選択可能にします。

    アクティブ時にマウスの右ボタンをクリックすると、テキスト以外の領域をドラッグしてウィンドウを移動できなくなります。

1. #### <i class="fa fa-search"></i> <i class="fa fa-icon fa-rotate-right"></i> 辞書を引く {#anchor-searchwordW}
    現在選択されているテキストがある場合は、選択されているテキストを問い合せ、単語検索ウィンドウを開きます。それ以外の場合は単に単語検索ウィンドウを開いたり閉じたりします。

1. #### <i class="fa fa-refresh"></i> 翻訳状態をリセットします {#anchor-reset_TS_status}
    翻訳状態をリセットします。主に増加し続ける大規模モデル翻訳のニーズに対応し、保存されたコンテキストやその他の情報をクリアできます。