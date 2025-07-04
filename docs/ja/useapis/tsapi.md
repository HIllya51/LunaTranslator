# 従来のオンライン翻訳インターフェース

## 従来のAPI

::: tabs

== 百度

#### 百度翻訳オープンプラットフォーム

https://fanyi-api.baidu.com/product/11

#### 百度智能云

https://ai.baidu.com/ai-doc/MT/ykqq95r2y

== 腾讯

### コントロールパネルにログイン

登録して実名認証を通過した後、腾讯云コントロールパネルにログインします。アカウントがない場合は、[アカウント登録チュートリアル](https://cloud.tencent.com/document/product/378/17985)を参照してください。

### サービスの開通

1. 腾讯云公式サイトのトップナビゲーションの製品の下にある人工知能と機械学習を見つけ、**機械翻訳**をクリックします。
2. 機械翻訳[製品紹介ページ](https://cloud.tencent.com/product/tmt)に入り、**今すぐ使用**ボタンをクリックして、[機械翻訳コントロールパネル](https://console.cloud.tencent.com/tmt)に入ります。
3. コントロールパネルの画面で、《サービスレベル契約》を読んで「《サービスレベル契約》を読み、同意しました」にチェックを入れ、**有料版を開通**ボタンをクリックすると、テキスト翻訳、ファイル翻訳リクエスト、バッチテキスト翻訳、音声翻訳、画像翻訳、言語識別インターフェースを一括で開通できます。

![](https://qcloudimg.tencent-cloud.cn/image/document/a136e50d4ac8d22c2708f2626f392b05.png)

### 無料クォータと購入

機械翻訳の特定のサービスを開通すると、そのサービスに対応する無料クォータが提供され、リソースパッケージの形式で腾讯云アカウントに発行され、課金結算時に優先的に差し引かれます。無料クォータがなくなった後、機械翻訳は前払いと後払いの2つの課金モードを提供し、機械翻訳の[課金概要](https://cloud.tencent.com/document/product/551/35017)を確認できます。

### キーの確認

公式サイトのコントロールパネル[腾讯云コントロールパネルAPIキー管理](https://console.cloud.tencent.com/cam/capi)にアクセスしてキーを取得します。
![](https://qcloudimg.tencent-cloud.cn/image/document/aa99d195c3f475d6673506c6ad4c059f.png)
**新しいキーを作成**ボタンをクリックすると、ポップアップウィンドウで自分のSecretidとSecretkeyを確認できます。**CSVファイルをダウンロード**ボタンをクリックしてローカルに保存することもできます。
![](https://qcloudimg.tencent-cloud.cn/image/document/2eb8d6d645a13411dcee2427ffc37c03.png)

https://cloud.tencent.com/document/product/551/104415

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

== 阿里

**サービスの開通** https://www.aliyun.com/product/ai/alimt

**キーの作成** https://help.aliyun.com/zh/ram/user-guide/create-an-accesskey-pair

== 彩云

テストする場合は、`3975l6lr5pcbvidl6jl2`をテストトークンとして使用できます。このトークンの可用性は保証されないため、継続的に使用する場合は正式なトークンを申請してください。

まず[彩云科技オープンプラットフォーム](https://platform.caiyunapp.com/regist)に登録し、小译トークンを申請します。

新規ユーザー登録で100万文字の無料翻訳クォータが1ヶ月間提供されます。100万文字を超える場合は、39元/100万文字の料金がかかります。（文字数は翻訳元の文字数で計算され、空白や句読点も含まれます）

https://docs.caiyunapp.com/lingocloud-api/#%E7%94%B3%E8%AF%B7%E8%AE%BF%E9%97%AE%E4%BB%A4%E7%89%8C

== 火山

### サービスの開通

#### ステップ1：機械翻訳コントロールパネルにアクセスする

* エントリーポイント1

    ここをクリックして機械翻訳コントロールパネルにアクセスします。

* エントリーポイント2

    機械翻訳関連製品のランディングページの[管理コンソール]ボタンをクリックして、機械翻訳コントロールパネルにアクセスします。

![](https://lf6-volc-editor.volccdn.com/obj/volcfe/sop-public/upload_970c9da11bbfb79246efe0f8fdf95d6c.png)

![](https://lf3-volc-editor.volccdn.com/obj/volcfe/sop-public/upload_7993788aaeabd0f72c850d886abd2337.png)

* エントリーポイント3

    コントロールパネルのナビゲーションリストでAI中台の[機械翻訳]を選択して、機械翻訳コントロールパネルにアクセスします。

![](https://lf6-volc-editor.volccdn.com/obj/volcfe/sop-public/upload_b86d6c66ecdcd23fad8a826f5081518a.png)

#### ステップ2：機械翻訳サービスの開通

*注：開通ボタンをクリックすると開通キューに入ります。開通のピーク時には再度開通ページに戻ることがあります。この場合は数分待ってから再度コントロールパネルにアクセスしてください。コントロールパネルのページに正常にアクセスできれば開通完了です。この間、開通ボタンを繰り返しクリックする必要はありません。

![](https://lf3-volc-editor.volccdn.com/obj/volcfe/sop-public/upload_4a46f87a3f0f7cc1ad18482d3e16af42)

### キーの取得

右上のアカウントをクリックし、ドロップダウンリストから[キー管理]を選択し、[新しいキーを作成]ボタンをクリックしてアクセスキー（Access Key ID、Secret Access Key）を取得します。後でこのキーを使用してインターフェースを呼び出すことができますので、適切に保管してください。

![](https://lf6-volc-editor.volccdn.com/obj/volcfe/sop-public/upload_14c2ac0aa56155152181b48df1772d55)

https://www.volcengine.com/docs/4640/127684

== Google

https://cloud.google.com/translate/docs/basic/translating-text

== DeepL

https://www.deepl.com/en/products/api

== Azure

https://learn.microsoft.com/en-us/azure/ai-services/translator/reference/v3-0-reference#authentication

**key1** Ocp-Apim-Subscription-Key	

**Location** Ocp-Apim-Subscription-Region

== 小牛

https://niutrans.com/cloud/api/list

== yandex

https://yandex.cloud/en/docs/translate/api-ref/authentication#service-account_1

== 华为云

https://www.huaweicloud.com/product/nlpmt.html

== IBM

https://github.com/IBM/watson-translator-101/blob/master/translation-document.md

:::


## 従来

::: tabs

== DeepL

`DeepLX`は[DeepLX](https://github.com/OwO-Network/DeepLX)からダウンロードして自己ホストし、`DeepLX api`を入力して使用します。

== lingva

デフォルトのホストは`translate.plausibility.cloud`ですが、[lingva-translate](https://github.com/thedaviddelta/lingva-translate)からダウンロードして自己ホストし、自分のドメインを入力して使用することもできます。

:::
