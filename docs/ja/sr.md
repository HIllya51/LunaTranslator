# 音声認識

Windows 10とWindows 11では、Windows音声認識を使用できます。

Windows 11では、システムにインストールされている言語とその音声認識モデルを直接検出できます。`コア設定`->`その他`->`音声認識`で、認識したい言語を選択し、この機能を有効にすると使用を開始できます。必要な言語がオプションに表示されない場合は、システムに対応する言語をインストールするか、対応する言語の認識モデルを探してソフトウェアディレクトリに解凍してください。

Windows 10では、システムに必要なランタイムと認識モデルが不足しています。まず、私がパッケージ化した[ランタイムと中日英言語認識モデル](https://lunatranslator.org/Resource/DirectLiveCaptions.zip)をダウンロードし、ソフトウェアディレクトリに解凍してください。そうすれば、ソフトウェアは私がパッケージ化したランタイムと認識モデルを認識し、この機能を使用できるようになります。

:::warning
Windows 10システムの場合、ソフトウェアと`ランタイムと中日英言語認識モデル`を非英語のパスに配置しないでください。そうしないと認識されません。
:::

他の言語の認識モデルが必要な場合は、対応する言語の認識モデルを自分で探すことができます。方法は次のとおりです：
https://store.rg-adguard.net/ で、`PacakgeFamilyName`を使用して`MicrosoftWindows.Speech.{LANGUAGE}.1_cw5n1h2txyewy`を検索します。ここで、`{LANGUAGE}`は必要な言語名です（たとえばフランス語の場合は`MicrosoftWindows.Speech.fr-FR.1_cw5n1h2txyewy`）。次に、最新バージョンのmsixをダウンロードして、ソフトウェアディレクトリに解凍します。

![img](https://image.lunatranslator.org/zh/srpackage.png)