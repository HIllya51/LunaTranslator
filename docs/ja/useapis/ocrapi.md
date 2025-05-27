# OCRインターフェース設定

## オンラインOCR

::: tabs

== 百度

#### 百度智能云 OCR

https://ai.baidu.com/ai-doc/OCR/1k3h7y3db

#### 百度智能云 画像翻訳

https://ai.baidu.com/ai-doc/MT/dkifdqg54

#### 百度翻訳オープンプラットフォーム 画像翻訳

https://fanyi-api.baidu.com/product/22

== 腾讯

#### OCR 一般印刷体認識

https://cloud.tencent.com/document/product/866/33526

#### 画像翻訳

https://cloud.tencent.com/document/product/551/17232

== 有道

### ステップ1：開発者になる

智云プラットフォームページの右上の「登録/ログイン」ボタンをクリックし、登録して情報を完了させると、開発者になることができます。

![](https://ai.youdao.com/images/guide-register.png)

### ステップ2：コンソールにアクセスしてアプリケーションを作成する

公式サイトにログインすると、自動的に智云[コンソール](https://ai.youdao.com/console/)にリダイレクトされます。

![](https://ai.youdao.com/images/app_overview.png)

ビジネス概要ページ / アプリケーション概要ページ / サービス詳細ページで、アプリケーション作成ボタンをクリックして[アプリケーション作成ページ](https://ai.youdao.com/console/#/app-overview/create-application)に入ります。

![](https://ai.youdao.com/images/create_app.png)

アプリケーション名を入力し、サービスと統合方法を選択し、他の重要な情報を入力して作成を完了します。

![](https://ai.youdao.com/images/edit_app.png)

### ステップ3：サービス詳細ページに入り、統合ドキュメントを表示する

コンソールの左側にあるサービス名をクリックしてサービス詳細ページに入ります。「統合方法」の下の「ドキュメント」ボタンをクリックして対応する技術ドキュメントにアクセスします。「SDKダウンロード」ボタンをクリックしてSDKをダウンロードします。「サンプル」セクションではデモを表示できます。統合プロセス中に「アプリケーションID（つまりAPPキー）」や「アプリケーションシークレットキー」などの情報が必要になる場合があります。これらの情報はアプリケーション概要で確認できます。

![](https://ai.youdao.com/images/serve_singleton.png)

https://ai.youdao.com/doc.s#guide

== 火山

#### ステップ1：開発者になる

火山引擎アカウントで[火山引擎コンソール](https://console.volcengine.com/auth/login/)にログインしてください。まだ火山引擎アカウントを持っていない場合は、[今すぐ登録](https://console.volcengine.com/auth/signup?redirectURI=//www.volcengine.com/)をクリックして火山ユーザーとして登録してください。

![](https://lf6-volc-editor.volccdn.com/obj/volcfe/sop-public/upload_d26f7523c21ef8f28cd0008d7357708e.png)

![](https://lf3-volc-editor.volccdn.com/obj/volcfe/sop-public/upload_9984617d3c4af144c282dfa6f1ad4de0.png)

#### ステップ2：ビジュアルインテリジェンスコンソールに入る

エントリーポイント1の例

* [ビジュアルインテリジェンス](https://console.volcengine.com/ai/console/info)をクリックしてビジュアルインテリジェンスコンソールに入ります

![](https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_a889d07925d5038ac33be49dfb7beab7.png)

エントリーポイント2の例

* ビジュアル関連製品のランディングページの[管理コンソール]ボタンをクリックします

![](https://lf6-volc-editor.volccdn.com/obj/volcfe/sop-public/upload_32871d39e485111ce66039264856a4c2.png)

エントリーポイント3の例

* AIプラットフォームのナビゲーションリストのビジュアル関連製品をクリックしてビジュアルインテリジェンスコンソールページに入ります

![](https://lf3-volc-editor.volccdn.com/obj/volcfe/sop-public/upload_2ab1ccb501a1345a3cf90055a4329adc.png)

#### ステップ3：実名認証とサービスの有効化

STEP1：トップのウェルカムカードで[認証に進む]をクリックして実名認証を完了し、サービスを有効化します。実名認証が完了していない場合、認証を促すポップアップウィンドウが表示されます。

![](https://lf6-volc-editor.volccdn.com/obj/volcfe/sop-public/upload_f01f78cd9672eb0db63bcb172ace7094.png)

![](https://lf3-volc-editor.volccdn.com/obj/volcfe/sop-public/upload_915b51d1f04bb495d28e64f9fb65b78a.png)

STEP2：認証が完了したら、ビジュアルインテリジェンスコンソールに入り、統合する機能を選択します。

![](https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_297a72f14b481766baae8079694448ef.png)

![](https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_23670c5d7aea4386eee69564b0dc58e6.png)

![](https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_30ae3a108f712d90274aaa1247a4001b.png)

必要な特定のサービスをページ上で直接見つけてクリックして有効化することもできます。

![](https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_cc39d6874e0b5e68d541d81c8d028851.png)

#### ステップ4：AK/SKの取得

火山引擎ビジュアルインテリジェンスコンソールのさまざまな機能を呼び出す前に、アクセスキー（AccessKey）を生成したことを確認してください。AccessKeyにはAccessKeyID（AK）とAccessKeySecret（SK）が含まれ、AccessKeyIDはユーザーを識別し、AccessKeySecretはユーザーの身元を確認するために使用されます。安全に保管してください。

取得方法：右上のアカウントをクリックし、ドロップダウンリストから[キー管理]を選択し、[新しいキーを作成]ボタンをクリックしてAK/SKを取得し、統合したアプリケーションのインターフェースを呼び出すための資格情報として使用します。

![](https://lf6-volc-editor.volccdn.com/obj/volcfe/sop-public/upload_88753005e8633cb897faa097223a05fd.png)

![](https://lf3-volc-editor.volccdn.com/obj/volcfe/sop-public/upload_9d0ce0314c4f43f00b8298497e27742f.png)

![](https://lf6-volc-editor.volccdn.com/obj/volcfe/sop-public/upload_ab865eca01c5cef188c4841d22d747fa.png)

https://www.volcengine.com/docs/6790/116978

== 讯飞

### ステップ1：開発者として登録する

[讯飞オープンプラットフォームクイックログインページ](https://passport.xfyun.cn/login)にアクセスし、WeChatスキャンコードまたはモバイルクイックログインでログインして讯飞オープンプラットフォームの登録開発者になります。または[讯飞オープンプラットフォーム登録ページ](https://passport.xfyun.cn/register)にアクセスして完全なオープンプラットフォームアカウントを登録し、讯飞オープンプラットフォームの登録開発者になります。

### ステップ2：最初のアプリケーションを作成し、サービスを使用開始する

プラットフォームにログインし、右上の「コンソール」または右上のドロップダウンメニューの「マイアプリケーション」からコンソールにアクセスします。アカウントがアプリケーションを作成したことがない場合、最初のアプリケーションを作成するように案内されます。

![](https://www.xfyun.cn/doc/assets/img/creatapp.7d53afaa.png)

アプリケーションに名前を付け、関連情報を入力します。送信ボタンをクリックすると、アプリケーションが作成されます。

> [!WARNING]
>旧バージョンのコンソールでは、後続のSDKまたはAPI統合のためにアプリケーションのオペレーティングシステムプラットフォームタイプを指定する必要がありましたが、新バージョンの更新後、この操作は不要になり、1つのアプリケーションで全てのインターフェースを管理できます。

アプリケーションが作成されると、左側のサービスリストから使用するサービスを選択できます。サービス管理パネルでは、利用可能なクォータ、履歴使用量、サービスインターフェースの検証情報、および呼び出せるAPIとSDKを確認できます。

![](https://www.xfyun.cn/doc/assets/img/manage1.469e7fa3.png)

![](https://www.xfyun.cn/doc/assets/img/manage2.cc025e41.png)

> [!WARNING]
>すべてのサービス管理パネルが同じではありません。異なるサービスには異なる管理パネルの構成があります。また、すべてのサービスにSDKとAPIインターフェースがあるわけではありません。一部のサービスにはAPIインターフェースのみがあり、他のサービスにはSDKのみがあります。詳細は対応するサービス管理ページで確認できます。

讯飞オープンプラットフォームは1つのアカウントで複数のアプリケーションを作成することをサポートしています。アプリケーションリストページに戻ってアプリケーションを切り替えるには、ページの左上のアプリケーション名の上にある戻るボタン、または右上の個人メニューの「マイアプリケーション」をクリックします。アプリケーションリストでアプリケーションを選択し、その名前をクリックしてそのアプリケーションに対応するサービス管理ページに入ります。

同じアプリケーションAPPIDは複数のビジネスで使用できますが、複数のビジネスが1つのAPPIDを共有すると使用量を個別に追跡できないため、各ビジネスに対して個別のアプリケーションAPPIDを使用することをお勧めします。

![](https://www.xfyun.cn/doc/assets/img/BACK.75999ee8.png)

> [!WARNING]
>アカウントに複数のアプリケーションがある場合、最後に操作したアプリケーションが記録され、讯飞オープンプラットフォームに戻ったときにさまざまなサービス操作のデフォルトアプリケーションとして設定されます。

https://www.xfyun.cn/doc/platform/quickguide.html

== Google Cloud Vision

https://cloud.google.com/vision/docs

== ocrspace

https://ocr.space/

== 大規模モデルの汎用インターフェース

[翻訳](/ja/guochandamoxing.html)と同じ

:::


## オフラインOCR


::: tabs

== ローカルOCR

組み込みでは、中国語・日本語・英語の軽量認識モデルが含まれています。他の言語を認識する必要がある場合は、`リソースダウンロード`で対応する言語モデルを追加してください。

さらに、`リソースダウンロード`では、中国語・日本語・英語の高精度モデルも提供されています。Windows 10版のソフトウェアを使用している場合、またはシステムがWindows 11の場合、GPUを使用してモデルを実行するように設定することで、高精度モデルの認識効率を向上させることができます。

== SnippingTool

>[!WARNING]
> Windows 10およびWindows 11オペレーティングシステムのみをサポートしています。

最新版のWindows 11システムであれば直接使用できます。

それ以外の場合は、`リソースダウンロードで`このモジュールをインストールする必要があります。

== manga-ocr

>[!WARNING]
>このOCRエンジンは横書きテキストの認識に不向きです。

CPU統合パッケージ https://lunatranslator.org/Resource/IntegrationPack/manga_ocr/cpu

GPU統合パッケージ https://lunatranslator.org/Resource/IntegrationPack/manga_ocr/gpu

== WeChat/QQ OCR

WeChatまたは最新バージョンのQQのインストールが必要です

== WindowsOCR

>[!WARNING]
> Windows 10およびWindows 11オペレーティングシステムのみをサポートしています。

### WindowsOCRの追加言語サポートをインストールする方法

#### OCR 言語パックのクエリを実行する方法

サポートされているすべての言語パックの一覧を返すには、管理者として PowerShell を開き (右クリックし、[管理者として実行] を選択します)、次のコマンドを入力します。

```powershell
Get-WindowsCapability -Online | Where-Object { $_.Name -Like 'Language.OCR*' }
```

出力例:

```
Name  : Language.OCR~~~el-GR~0.0.1.0
State : NotPresent

Name  : Language.OCR~~~en-GB~0.0.1.0
State : NotPresent

Name  : Language.OCR~~~en-US~0.0.1.0
State : Installed

Name  : Language.OCR~~~es-ES~0.0.1.0
State : NotPresent

Name  : Language.OCR~~~es-MX~0.0.1.0
State : NotPresent
```

言語と場所は省略されているため、"en-US" は "English-United States" になり、"en-GB" は "English-Great Britain" になります。 出力で使用できない言語は、OCR ではサポートされません。 `State: NotPresent` 言語を最初にインストールする必要があります。

#### OCR 言語パックをインストールする方法

次のコマンドは、"en-US" 用の OCR パックをインストールします:

```powershell
$Capability = Get-WindowsCapability -Online | Where-Object { $_.Name -Like 'Language.OCR*en-US*' }
$Capability | Add-WindowsCapability -Online
```

#### OCR 言語パックを削除する方法

次のコマンドは、"en-US" の OCR パックを削除します:

```powershell
$Capability = Get-WindowsCapability -Online | Where-Object { $_.Name -Like 'Language.OCR*en-US*' }
$Capability | Remove-WindowsCapability -Online
```

https://learn.microsoft.com/ja-jp/windows/powertoys/text-extractor#supported-languages

== Tesseract5

>[!WARNING]
>性能が低すぎるため、使用は推奨されません。

https://github.com/tesseract-ocr/tesseract/releases

:::
