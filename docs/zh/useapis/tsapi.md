# 传统在线翻译接口

## 传统API

::: tabs

== 百度

#### 百度翻译开放平台

https://fanyi-api.baidu.com/product/11

#### 百度智能云

https://ai.baidu.com/ai-doc/MT/ykqq95r2y

== 腾讯

### 登录控制台

注册并通过实名认证后，登录腾讯云控制台。如果没有账号，请参考 [账号注册教程](https://cloud.tencent.com/document/product/378/17985)。

### 开通服务

1. 在腾讯云官网顶部导航产品下面，找到人工智能与机器学习，单击**机器翻译**。
2. 进入机器翻译[产品介绍页](https://cloud.tencent.com/product/tmt)，单击**立即使用**按钮，进入 [机器翻译控制台](https://console.cloud.tencent.com/tmt)。
3. 在控制台界面，阅读《服务等级协议》后勾选“我已阅读并同意《服务等级协议》”，然后单击**开通付费版**，即可一键开通文本翻译、文件翻译请求、批量文本翻译、语音翻译、图片翻译、语种识别接口。

![](https://qcloudimg.tencent-cloud.cn/image/document/a136e50d4ac8d22c2708f2626f392b05.png)

### 免费额度与购买

开通了机器翻译某项服务，该项服务即可享受对应额度的免费调用额度，以资源包的形式发放到您的腾讯云账号中，并在计费结算时优先扣减。免费额度耗尽后，机器翻译提供预付费和后付费两种计费模式，您可以查看机器翻译的 [计费概述](https://cloud.tencent.com/document/product/551/35017)。

### 查看密钥

前往官网控制台 [腾讯云控制台 API 密钥管理](https://console.cloud.tencent.com/cam/capi) 获取密钥。
![](https://qcloudimg.tencent-cloud.cn/image/document/aa99d195c3f475d6673506c6ad4c059f.png)
单击**新建密钥**按钮，弹窗查看自己的 Secretid 和 Secretkey，可单击**下载 CSV 文件**保存至本地。
![](https://qcloudimg.tencent-cloud.cn/image/document/2eb8d6d645a13411dcee2427ffc37c03.png)

https://cloud.tencent.com/document/product/551/104415

== 有道

### 第一步：成为开发者 

点击智云平台页面右上角“注册/登录”按钮，注册并完善信息，即可成为开发者。

![](https://ai.youdao.com/images/guide-register.png)

### 第二步：访问控制台并创建应用 

在官网登录后您会自动跳转至智云[控制台](https://ai.youdao.com/console/)。

![](https://ai.youdao.com/images/app_overview.png)

在业务总览页 / 应用总览页 / 服务详情页，点击创建应用按钮，进入[创建应用页](https://ai.youdao.com/console/#/app-overview/create-application)。

![](https://ai.youdao.com/images/create_app.png)

填写应用名称，选择服务及接入方式，并填写其他关键信息，即可完成创建。

![](https://ai.youdao.com/images/edit_app.png)

### 第三步：进入服务详情页，查看接入文档 

点击控制台左侧的服务名称，可以进入服务详情页。点击“接入方式”中的“文档”按钮，可以访问对应的技术文档，点击“SDK下载”按钮可以下载SDK；在“示例”部分可以查看Demo。在接入过程中您可能会用到“应用ID（即APP key）”、“应用密钥”等信息，这些信息可以在应用总览中查看。

![](https://ai.youdao.com/images/serve_singleton.png)

https://ai.youdao.com/doc.s#guide

== 阿里

**开通服务** https://www.aliyun.com/product/ai/alimt

**创建密钥** https://help.aliyun.com/zh/ram/user-guide/create-an-accesskey-pair

== 彩云

如果你要测试，可以使用 `3975l6lr5pcbvidl6jl2` 作为测试 Token，我们不保证该 Token 的可用性，所以如果要持续使用，还请申请正式 Token。

请先至[彩云科技开放平台](https://platform.caiyunapp.com/regist)注册账号，申请开通小译 Token。

新用户注册会获得 100 万字的免费翻译额度,有效期一个月；如果您使用超过 100 万字，我们会按照 39 元 / 100 万字的费率收费。(字数按照翻译原文字符计算，包含空格和标点)

https://docs.caiyunapp.com/lingocloud-api/#%E7%94%B3%E8%AF%B7%E8%AE%BF%E9%97%AE%E4%BB%A4%E7%89%8C

== 火山

### 开通服务

#### Step1：进入机器翻译控制台

* 入口一

    点击此处，进入机器翻译控制台。

* 入口二

    点击机器翻译相关产品，进入【机器翻译落地页】-点击【管理控制台】，进入机器翻译控制台。

![](https://lf6-volc-editor.volccdn.com/obj/volcfe/sop-public/upload_970c9da11bbfb79246efe0f8fdf95d6c.png)

![](https://lf3-volc-editor.volccdn.com/obj/volcfe/sop-public/upload_7993788aaeabd0f72c850d886abd2337.png)

* 入口三

    点击控制台导航列表，选择AI中台的【机器翻译】，进入机器翻译控制台。

![](https://lf6-volc-editor.volccdn.com/obj/volcfe/sop-public/upload_b86d6c66ecdcd23fad8a826f5081518a.png)

#### Step2：开通机器翻译服务

*注：点击开通后会进入开通队列，如遇开通高峰，会重新跳回开通页面，此时请耐心等待几分钟后再进入控制台，成功进入控制台页面即为开通完成，在此期间无需反复点击开通。

![](https://lf3-volc-editor.volccdn.com/obj/volcfe/sop-public/upload_4a46f87a3f0f7cc1ad18482d3e16af42)

### 获取密钥

点击右上角账号，下拉列表选择【密钥管理】-点击【新建密钥】，可获取访问密钥（Access Key ID、Secret Access Key）。后续可使用此密钥调用接口，请您妥善保管。

![](https://lf6-volc-editor.volccdn.com/obj/volcfe/sop-public/upload_14c2ac0aa56155152181b48df1772d55)

https://www.volcengine.com/docs/4640/127684

== 谷歌

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


## 传统

::: tabs

== DeepL

`DeepLX`需要在[DeepLX](https://github.com/OwO-Network/DeepLX)下载后自行部署，并填入`DeepLX api`以使用。

== lingva

默认host为`translate.plausibility.cloud`，也可以在[lingva-translate](https://github.com/thedaviddelta/lingva-translate)自行部署后填入自己的域名。

:::
