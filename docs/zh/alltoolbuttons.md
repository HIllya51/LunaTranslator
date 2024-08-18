## 详解工具按钮

?>所有按钮可以在`显示设置`->`工具按钮`中，进行隐藏或显示。<br>
所有按钮均可以随意调整位置。按钮可以设置对齐组`居左` `居中` `居右`，对相对位置的调整都会被限定在对齐组中。<br>
按钮颜色可以在`显示设置`->`界面设置`->`工具栏`->`按钮颜色`中进行自定义。<br>
部分按钮有两个图标，用来指示两种不同的状态。部分按钮仅有一个图标，不过会用不同的颜色来表示不同的状态

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

1. #### <i class="fa fa-rotate-right"></i> <i class="fa fa-icon fa-rotate-right"></i> 手动翻译
    实际意义是，从当前的文本输入源，读取一次输入，并执行翻译。
    例如如果当前是OCR模式，会再执行一次OCR。

1. #### <i class="fa fa-forward"></i> <i class="btnstatus2 fa fa-forward"></i> 自动翻译
    实际意义是，暂停/继续自动从当前的文本输入源读取文本。
    例如如果当前是HOOK模式，会暂停读取游戏文本；当前是OCR模式，暂停自动识别图像；如果当前是剪贴板模式，会暂停自动读取剪贴板。

1. #### <i class="fa fa-gear"></i> <i class="fa fa-icon fa-rotate-right"></i> 打开设置
    略
1. #### <i class="fa fa-file"></i> <i class="fa fa-icon fa-rotate-right"></i> 读取剪贴板
    这个的实际意义是，不管当前的默认文本输入源是什么，都从剪贴板读取一次文本，并传给之后的翻译/tts/...流程

1. #### <i class="fa fa-sitemap"></i> <i class="fa fa-icon fa-rotate-right"></i> 打开关联页面
    相当于一个小浏览器，主要是可以为每个游戏，单独创建一个小的收藏夹。会自动查询元数据收藏游戏的vndb/bangumi/dlsite/等页面，也可以手动再添加一些和这个游戏关联的网页进去（例如游戏攻略的网页，除了用备忘录外，也可以用这个功能进行收藏），方便查看。免去了在浏览器里创建收藏夹进行管理的麻烦。
    详见[实用功能](/zh/usefulsmalltools.md?id=关联页面，便捷管理游戏相关网页)
1. #### <i class="fa fa-futbol"></i> <i class="fa fa-icon fa-rotate-right"></i> 游戏设置
    当使用HOOK模式连接到游戏，或使用OCR模式绑定游戏窗口后，则可以通过这个按钮直接打开当前游戏的设置窗口
1. #### <i class="fa fa-mouse-pointer"></i> <i class="btnstatus2 fa fa-mouse-pointer"></i> 鼠标穿透窗口
    激活这个按钮后，鼠标点击翻译窗口时，翻译窗口不会对鼠标点击做出反应，而是把点击事件传递给下层窗口。<br>
    当把翻译窗口置于游戏窗口的文本框之上时，激活这个按钮可以直接点击游戏的文本框而不是点击到翻译窗口上。<br>
    当把鼠标移动到**鼠标穿透窗口按钮及其左右一个按钮的区域**时，会自动退出穿透以使用工具按钮；移出区域时自动恢复穿透。

1. #### <i class="fa fa-lightbulb"></i> <i class="btnstatus2 fa fa-lightbulb"></i> 背景窗口透明
    该按钮作用仅是一键使得翻译窗口的不透明度切换到0。这个切换不会使得原版的不透明度设置被遗忘。
1. #### <i class="fa fa-lock"></i> <i class="btnstatus2 fa fa-unlock"></i> 锁定工具栏
    未锁定工具栏时，当鼠标移出时，工具栏会自动隐藏；激活后工具栏将始终显示。<br>
    未锁定工具栏时，如果激活了`鼠标穿透窗口`，则仅当鼠标移动到**鼠标穿透窗口按钮及其左右一个按钮的区域**时，工具栏才显示；否则只要鼠标进入到翻译窗口，工具就会显示。<br>
    如果当前使用了窗口特效(Aero/Arylic)，且不锁定工具栏，则工具栏会处于文本区的z轴之上的区域，而非处于文本区的y轴上面。这是因为由于Windows的原因，使用窗口特效时，如果将工具栏只是隐藏而非将缩去其窗口高度，则被隐藏的工具栏仍会被渲染亚力克/Aero背景，导致工具栏所在区域会有一块空白。
1. #### <i class="fa fa-link"></i> <i class="fa fa-icon fa-rotate-right"></i> 选择游戏
    **该按钮仅在HOOK模式下可用**<br>
    点击按钮弹出选择游戏进程窗口，来选择要HOOK的游戏进程。
1. #### <i class="fa fa-tasks"></i> <i class="fa fa-icon fa-rotate-right"></i> 选择文本
    **该按钮仅在HOOK模式下可用**<br>
    点击按钮弹出选择游戏文本窗口，来选择要翻译哪条HOOK到的文本。<br>
    不过，选择文本窗口在选择进程后会自动弹出，这个按钮实际上是用来更换选择的文本，或修改一些设置用的。
1. #### <i class="fa fa-crop"></i> <i class="fa fa-icon fa-rotate-right"></i> 选取OCR范围
    **OCR模式下**，选取OCR区域，或者更换OCR区域，或者当激活`OCR设置`->`其他`->`多重区域模式`时增加新的OCR区域
    **非OCR模式下**，合并了原`进行一次OCR`按钮的功能，先进行OCR范围选择，然后进行一次OCR，然后进行翻译流程。一般用于，在HOOK模式下，遇到选择支时，临时使用一次OCR进行翻译选择支。或者在OCR模式下，临时去识别一次其他偶尔出现的新的位置。
1. #### <i class="fa fa-square"></i> <i class="fa fa-icon fa-rotate-right"></i> 显示/隐藏范围框 
    **该按钮仅在OCR模式下可用**<br>
    当未选择任何OCR范围时，使用该按钮显示OCR范围，会自动设置OCR范围为上一次选择的OCR。
1. #### <i class="fa fa-spinner"></i> <i class="fa fa-icon fa-rotate-right"></i> 再次进行OCR
    **非OCR模式下**，当使用过一次`选取OCR范围`后，使用这个按钮，可以在原来的位置上再次进行一次OCR而无需重新选择识别区域。
    
1. #### <i class="fa fa-book"></i> <i class="fa fa-icon fa-rotate-right"></i> 专有名词翻译_直接替换
1. #### <i class="fa fa-book"></i> <i class="fa fa-icon fa-rotate-right"></i> 专有名词翻译_sakura_gpt_词典
1. #### <i class="fa fa-book"></i> <i class="fa fa-icon fa-rotate-right"></i> 专有名词翻译_占位符_全局
1. #### <i class="fa fa-book"></i> <i class="fa fa-icon fa-rotate-right"></i> 专有名词翻译_占位符
1. #### <i class="fa fa-won"></i> <i class="fa fa-icon fa-rotate-right"></i> 翻译结果修正_全局
1. #### <i class="fa fa-won"></i> <i class="fa fa-icon fa-rotate-right"></i> 翻译结果修正
    以上六个按钮，效果类似，是用来快捷打开翻译优化的设置窗口，增加新的指定词条的。<br>
    对于`全局`，则一定打开全局的词典设置。对于非`全局`，则当有绑定的游戏(HOOK链接游戏/剪贴板、OCR绑定窗口)时，打开游戏的专用词典设置，否则则是打开全局的词典设置
1. #### <i class="fa fa-minus"></i> <i class="fa fa-icon fa-rotate-right"></i> 最小化到托盘
    略
1. #### <i class="fa fa-times"></i> <i class="fa fa-icon fa-rotate-right"></i> 退出
    略
1. #### <i class="fa fa-hand-paper"></i> <i class="fa fa-icon fa-rotate-right"></i> 移动
    拖动翻译窗口。<br>
    实际上当按钮栏有没有按钮存在的额外空白区域时，都可以随意拖动。该按钮仅用来预留一个拖动位置。
1. #### <i class="fa fa-compress"></i> <i class="fa fa-expand"></i> 窗口缩放
    可以一键对游戏窗口(HOOK链接游戏/剪贴板、OCR绑定窗口)进行缩放（默认使用内置的Magpie，也可以设置使用自己下载的Magpie等）。<br>
1. #### <i class="fa fa-camera"></i> <i class="fa fa-icon fa-rotate-right"></i> 窗口截图
    可以对绑定的窗口进行截图，（默认会截两张图，GDI和Winrt，两者均有一定概率会失败）。最好的地方是，如果当前正在使用Magpie进行缩放，还会对放大的窗口进行截图。<br>
    详见[实用功能](/zh/usefulsmalltools.md?id=窗口截图amp画廊amp录音，捕捉每个精彩瞬间)
1. #### <i class="fa fa-volume-off"></i> <i class="btnstatus2 fa fa-volume-up"></i> 游戏静音
    当绑定游戏窗口后（不只是hook模式，ocr或剪贴板模式都可以，只要绑定了游戏窗口），可以一键对游戏进行静音，省去了在系统音量合成器进行游戏静音的麻烦。
1. #### <i class="fa fa-eye"></i> <i class="btnstatus2 fa fa-eye-slash"></i> 显示/隐藏原文
    切换是否显示原文的状态，当下一次读取文本时，才真正生效。
1. #### <i class="fa fa-eye"></i> <i class="btnstatus2 fa fa-eye-slash"></i> 显示/隐藏翻译
    切换是否显示翻译的状态，当下一次读取文本时，才真正生效。
1. #### <i class="fa fa-music"></i> <i class="fa fa-icon fa-rotate-right"></i> 朗读
    对当前文本进行语音合成。<br>
    该朗读会无视`跳过`（如果在`语音指定`中，匹配当前文本目标为`跳过`，则使用按钮进行朗读时，会无视跳过，强制进行朗读）
1. #### <i class="fa fa-copy"></i> <i class="fa fa-icon fa-rotate-right"></i> 复制到剪贴板
    复制当前提取到的文本到剪贴板一次。如果想要自动提取到剪贴板，应当激活`文本输入`->`文本输出`->`剪贴板`->`自动输出`。
1. #### <i class="fa fa-rotate-left"></i> <i class="fa fa-icon fa-rotate-right"></i> 显示/隐藏历史翻译
    打开或关闭历史翻译的窗口。
1. #### <i class="fa fa-gamepad"></i> <i class="fa fa-icon fa-rotate-right"></i> 游戏管理
    打开游戏管理器界面。
1. #### <i class="fa fa-edit"></i> <i class="fa fa-icon fa-rotate-right"></i> 编辑
    打开编辑窗口，运行编辑当前提取到的文本。<br>
    该窗口中，可以运行修改文本后，再去进行翻译；或者可以翻译任何自行输入的文本。
1. #### <i class="fa fa-edit"></i> <i class="fa fa-icon fa-rotate-right"></i> 编辑_翻译记录
    打开当前游戏的翻译记录编辑窗口
1. #### <i class="fa fa-download"></i> <i class="fa fa-icon fa-rotate-right"></i> 模拟按键Ctrl
1. #### <i class="fa fa-download"></i> <i class="fa fa-icon fa-rotate-right"></i> 模拟按键Enter
    同上，用于向游戏窗口发送一次模拟按键。对于使用串流/平板时，有些作用。
1. #### <i class="fa fa-list-ul"></i> <i class="fa fa-icon fa-rotate-right"></i> 备忘录
    对于当前正在玩的游戏，打开备忘录窗口。对于每个游戏都有单独的一个备忘录文件。<br>
    可以用来临时写点笔录，或者把攻略复制进来看并且随玩随删，很方便，免去打开网页/单独开一个txt文件的麻烦，非常实用。
1. #### <i class="fab fa-windows"></i> <i class="btnstatus2 fab fa-windows"></i> 绑定窗口（部分软件不支持）（点击自己取消）
    **该按钮非常重要，需要功能都依赖于该按钮先进行设置后才可用**<br>
    在绑定了游戏窗口后，`窗口缩放` `窗口截图` `游戏静音`，`跟随游戏窗口`->`游戏失去焦点时取消置顶`和`游戏窗口移动时同步移动`，以及记录游戏时间等，才可用。
    不论HOOK/OCR/剪贴板模式，该按钮都可用。<br>
    在HOOK模式下，会自动根据连接的游戏，自动绑定游戏窗口。但也可以在用该按钮重新选择其他窗口。<br>
    在OCR模式下，绑定窗口后，还额外允许游戏窗口移动时，同步自动移动OCR区域和范围框。
    在OCR/剪贴板模型下，绑定窗口后，也可以和HOOK模式下一样，关联到当前游戏到游戏设置，从而使用当前游戏的专有翻译优化词典等。

1. #### <i class="fa fa-neuter"></i> <i class="btnstatus2 fa fa-neuter"></i> 窗口置顶
    取消/置顶翻译窗口
1. #### <i class="fa fa-i-cursor"></i> <i class="btnstatus2 fa fa-i-cursor"></i> 可选取的
    使得翻译窗的文本区中的文本，是可用进行选择的。当激活了可选取后，无法在文本去进行拖动而只能拖动工具栏（因为拖动时是在选取文本）
1. #### <i class="fa fa-search"></i> <i class="fa fa-icon fa-rotate-right"></i> 查词
    打开查词窗口。
  