# 大規模モデル翻訳インターフェース

## 大規模モデルの汎用インターフェース

::: details 複数の大規模モデルインターフェースを同時に使用するには？
異なる複数のキーをローテーションしたいだけなら、`|`で区切るだけでOKです。

しかし、複数の異なるAPIインターフェースアドレス、プロンプト、モデル、パラメータなどを同時に使用して翻訳効果を比較したい場合もあります。その方法は以下の通りです：

1. 上の「+」ボタンをクリックします。
   ![img](https://image.lunatranslator.org/zh/damoxing/extraapi1.png)
1. ウィンドウがポップアップします。大規模モデルの汎用インターフェースを選択し、名前を付けます。これにより、現在の大規模モデル汎用インターフェースの設定とAPIが複製されます。
   ![img](https://image.lunatranslator.org/zh/damoxing/extraapi2.png)
1. 複製されたインターフェースをアクティブにし、個別に設定できます。複製されたインターフェースは元のインターフェースと一緒に実行でき、複数の異なる設定を使用して実行できます。
   ![img](https://image.lunatranslator.org/zh/damoxing/extraapi3.png)
:::

### パラメータ説明  

1. #### APIインターフェースアドレス  

    主要な大規模モデルプラットフォームの`APIインターフェースアドレス`は、ドロップダウンリストから選択可能ですが、一部抜けている場合があります。リストにないインターフェースについては、各プラットフォームのドキュメントを参照して手動で入力してください。  

1. #### API Key  

    `API Key`は各プラットフォームで取得できます。複数のキーを追加した場合、自動的にローテーションされ、エラーフィードバックに基づいてキーの重みが調整されます。  

1. #### モデル  

    ほとんどのプラットフォームでは、`APIインターフェースアドレス`と`API Key`を入力後、`モデル`横の更新ボタンをクリックすると、利用可能なモデルリストを取得できます。  

    プラットフォームがモデル取得インターフェースをサポートしておらず、デフォルトリストに使用したいモデルがない場合は、API公式ドキュメントを参照して手動でモデル名を入力してください。  

1. #### ストリーミング出力  

    有効にすると、モデルの出力内容をストリーミング形式で逐次表示します。無効の場合は、モデルの出力が完了してから一括で表示されます。  

1. #### 思考プロセスを非表示  

    有効にすると、`<think>`タグで囲まれた内容を表示しません。ただし、思考の進捗状況は表示されます。  

1. #### 付帯コンテキスト数  

    翻訳を最適化するため、指定した数の過去の原文と翻訳を大規模モデルに提供します。0に設定するとこの機能は無効になります。  

    - **キャッシュヒットを最適化** - DeepSeekなどのプラットフォームでは、キャッシュヒットした入力に対して低価格で課金されます。有効にすると、付帯コンテキストの形式を最適化し、キャッシュヒット率を向上させます。  

1. #### カスタムsystem prompt / カスタムuser message / プリフィル  

    出力内容を制御するためのいくつかの方法です。好みに応じて設定するか、デフォルトのまま使用できます。  

    カスタムシステムプロンプトとユーザーメッセージ内では、いくつかの情報をフィールドを使って参照できます：
    - `{sentence}`：現在翻訳するテキスト
    - `{srclang}`と`{tgtlang}`：ソース言語とターゲット言語。プロンプトで英語のみが使用されている場合、これらは言語名の英語訳に置き換えられます。それ以外の場合は、現在のUI言語の言語名訳に置き換えられます。
    - `{contextOriginal[N]}` と `{contextTranslation[N]}` と `{contextTranslation[N]}`：N件の履歴原文、翻訳文、両方。Nは「付随するコンテキストの数」とは関係なく、入力時に整数に置き換えてください。
    - `{DictWithPrompt[XXXXX]}`: このフィールドは「固有名詞翻訳」のエントリを参照できます。**一致するエントリがない場合、翻訳内容を破壊しないようにこのフィールドはクリアされます**。`XXXXX`は、LLMに与えられたエントリを使用して翻訳を最適化するように導くプロンプトであり、ユーザーが定義することも、カスタムユーザーメッセージを無効にしてデフォルトのプロンプトを使用することもできます。


1. #### Temperature / max tokens / top p / frequency penalty  

    一部のプラットフォームの一部のモデルでは、`top p` や `frequency penalty` などのパラメータがインターフェースで受け入れられない場合があります。また、`max tokens` パラメータが廃止され、代わりに `max completion tokens` に変更されている場合もあります。これらの問題は、スイッチをオンまたはオフにすることで解決できます。

1. #### reasoning effort  

    Geminiプラットフォームでは、このオプションをGeminiの`thinkingBudget`に自動的にマッピングします。マッピングルールは次の通りです：
    
    minimal->0（思考無効、ただしGemini-2.5-Proモデルでは適用不可）、low->512、medium->-1（動的思考を有効）、high->24576。  

1. #### その他のパラメータ  

    上記は一般的なパラメータのみを提供しています。使用するプラットフォームで有用な未記載のパラメータがある場合は、手動でキーと値を追加してください。  

## 一般的な大規模モデルプラットフォーム

### 欧米の大規模モデルプラットフォーム  

::: tabs

== OpenAI

**API Key** https://platform.openai.com/api-keys

== Gemini

**API Key** https://aistudio.google.com/app/apikey

== Claude

**API Key** https://console.anthropic.com/

**model** https://docs.anthropic.com/en/docs/about-claude/models

== Cohere

**API Key** https://dashboard.cohere.com/api-keys

== x.ai

**API Key** https://console.x.ai/

== Groq

**API Key** https://console.groq.com/keys

== OpenRouter

**API Key** https://openrouter.ai/settings/keys

== Mistral AI

**API Key** https://console.mistral.ai/api-keys/

== Azure

**APIインターフェースアドレス** `https://{endpoint}.openai.azure.com/openai/deployments/{deployName}/chat/completions?api-version=2023-12-01-preview`

`{endpoint}`と`{deployName}`をあなたのendpointとdeployNameに置き換えてください。

== Deepinfra


**API Key** https://deepinfra.com/dash/api_keys

== Cerebras

**API Key** https://cloud.cerebras.ai/  ->  API Keys

== Chutes

**API Key** https://chutes.ai/app/api


:::

### 中国の大規模モデルプラットフォーム  

::: tabs

== DeepSeek

**API Key** https://platform.deepseek.com/api_keys

== 阿里雲百煉大模型

**API Key** https://bailian.console.aliyun.com/?apiKey=1#/api-key

**model** https://help.aliyun.com/zh/model-studio/getting-started/models

== バイトダンス ボルケーノエンジン

**API Key** [API Keyを作成](https://console.volcengine.com/ark/region:ark+cn-beijing/apiKey?apikey=%7B%7D)して取得

**model** [推論エンドポイントを作成](https://console.volcengine.com/ark/region:ark+cn-beijing/endpoint?current=1&pageSize=10)した後、**エンドポイント**を記入（**モデル**ではない）

![img](https://image.lunatranslator.org/zh/damoxing/doubao.png)

== 月の暗面

**API Key** https://platform.moonshot.cn/console/api-keys

== 智譜AI

**API Key** https://bigmodel.cn/usercenter/apikeys

**model** https://bigmodel.cn/dev/howuse/model

== 零一万物

**API Key** https://platform.lingyiwanwu.com/apikeys

== 硅基流動

**API Key** https://cloud-hk.siliconflow.cn/account/ak

== 訊飛星火大模型

**API Key** [公式ドキュメント](https://www.xfyun.cn/doc/spark/HTTP%E8%B0%83%E7%94%A8%E6%96%87%E6%A1%A3.html#_3-%E8%AF%B7%E6%B1%82%E8%AF%B4%E6%98%8E)を参照して**APIKey**と**APISecret**を取得し、`APIKey:APISecret`の形式で記入

**model** https://www.xfyun.cn/doc/spark/HTTP%E8%B0%83%E7%94%A8%E6%96%87%E6%A1%A3.html#_3-2-%E8%AF%B7%E6%B1%82%E5%8F%82%E6%95%B0

== テンセント混元大模型

**API Key** [公式ドキュメント](https://cloud.tencent.com/document/product/1729/111008)を参照

**model** https://cloud.tencent.com/document/product/1729/97731

== 百度千帆大模型

**API Key** https://cloud.baidu.com/doc/WENXINWORKSHOP/s/Um2wxbaps

**model** https://cloud.baidu.com/doc/WENXINWORKSHOP/s/Fm2vrveyu

>[!WARNING]
>**API Key**は、百度智能雲IAMのAccess KeyとSecret Keyを使用してインターフェースのBearerTokenを生成し、それを**API Key**として記入するか、`Access Key`:`Secret Key`の形式で直接記入してください。千帆ModelBuilderの旧版v1バージョンのAPI KeyとSecret Keyとは互換性がないので注意してください。

== MiniMax

**API Key** https://platform.minimaxi.com/document/Fast%20access?key=66701cf51d57f38758d581b2

:::

### API集約管理システム

[new-api](https://github.com/QuantumNous/new-api)などのAPIリレーツールを使用して、複数の大規模モデルプラットフォームモデルと複数のキーをより便利に集約管理することもできます。

使用方法については、[この記事](https://www.newapi.ai/apps/luna-translator/)を参照してください。

### オフライン大規模モデル

[llama.cpp](https://github.com/ggerganov/llama.cpp)、[ollama](https://github.com/ollama/ollama)などのツールを使用してモデルをデプロイし、アドレスとモデルを入力することができます。

