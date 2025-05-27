# OCR接口设置

## 在线OCR

::: tabs

== 百度

#### 百度智能云 OCR

https://ai.baidu.com/ai-doc/OCR/1k3h7y3db

#### 百度智能云 图片翻译

https://ai.baidu.com/ai-doc/MT/dkifdqg54

#### 百度翻译开放平台 图片翻译

https://fanyi-api.baidu.com/product/22

== 腾讯

#### OCR 通用印刷体识别

https://cloud.tencent.com/document/product/866/33526

#### 图片翻译

https://cloud.tencent.com/document/product/551/17232

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

== 火山

#### 步骤1：成为开发者

请您使用火山引擎账号登陆[火山引擎控制台](https://console.volcengine.com/auth/login/)；如还未持有火山引擎账户，点击[立即注册](https://console.volcengine.com/auth/signup?redirectURI=//www.volcengine.com/)，注册成为火山用户。

![](https://lf6-volc-editor.volccdn.com/obj/volcfe/sop-public/upload_d26f7523c21ef8f28cd0008d7357708e.png)

![](https://lf3-volc-editor.volccdn.com/obj/volcfe/sop-public/upload_9984617d3c4af144c282dfa6f1ad4de0.png)

#### 步骤2：进入视觉智能控制台

入口一示例

* 点击[视觉智能](https://console.volcengine.com/ai/console/info)，进入视觉智能控制台

![](https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_a889d07925d5038ac33be49dfb7beab7.png)

入口二示例

* 点击视觉相关产品落地页入口【管理控制台】按钮

![](https://lf6-volc-editor.volccdn.com/obj/volcfe/sop-public/upload_32871d39e485111ce66039264856a4c2.png)

入口三示例

* 点击控制台导航列表AI中台视觉相关产品，进入视觉智能控制台页面

![](https://lf3-volc-editor.volccdn.com/obj/volcfe/sop-public/upload_2ab1ccb501a1345a3cf90055a4329adc.png)

#### 步骤3：实名认证与服务开通

STEP1：顶部欢迎卡片点击【去认证】，进行实名认证后再开通服务，若未完成实名认证会弹出认证弹窗

![](https://lf6-volc-editor.volccdn.com/obj/volcfe/sop-public/upload_f01f78cd9672eb0db63bcb172ace7094.png)

![](https://lf3-volc-editor.volccdn.com/obj/volcfe/sop-public/upload_915b51d1f04bb495d28e64f9fb65b78a.png)


STEP2：完成认证后，进入视觉智能控制台，选择接入能力

![](https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_297a72f14b481766baae8079694448ef.png)

![](https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_23670c5d7aea4386eee69564b0dc58e6.png)

![](https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_30ae3a108f712d90274aaa1247a4001b.png)

您也可以直接在页面上找到某项需要的服务，直接点击开通服务

![](https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_cc39d6874e0b5e68d541d81c8d028851.png)

#### 步骤4：获取AK/SK


在调用火山引擎视觉智能控制台的各个能力之前，确保您已生成访问密钥（AccessKey）。AccessKey包括AccessKeyID（AK）和AccessKeySecret（SK），其中AccessKeyID用于标识用户，AccessKeySecret是用来验证用户的密钥，请妥善保管。

获取方式：点击右上角账号，下拉列表选择【密钥管理】，点击【新建密钥】按钮，可获取AK/SK，可以此为凭证调用上述已接入应用的接口。

![](https://lf6-volc-editor.volccdn.com/obj/volcfe/sop-public/upload_88753005e8633cb897faa097223a05fd.png)

![](https://lf3-volc-editor.volccdn.com/obj/volcfe/sop-public/upload_9d0ce0314c4f43f00b8298497e27742f.png)

![](https://lf6-volc-editor.volccdn.com/obj/volcfe/sop-public/upload_ab865eca01c5cef188c4841d22d747fa.png)


https://www.volcengine.com/docs/6790/116978

== 讯飞

### 第一步：注册成为开发者

进入[讯飞开放平台快捷登录页](https://passport.xfyun.cn/login) ，通过微信扫码、手机快捷登录，即可快速成为讯飞开放平台注册开发者。或进入[讯飞开放平台注册页](https://passport.xfyun.cn/register)注册完整的开放平台账号，成为讯飞开放平台注册开发者

### 第二步：创建您的第一个应用，开始使用服务

登录平台后，通过右上角「控制台」，或右上角下拉菜单的「我的应用」进入控制台。若您的账户未曾创建过应用，我们会引导您创建您的第一个应用。

![](https://www.xfyun.cn/doc/assets/img/creatapp.7d53afaa.png)

请为您的应用起一个名字，并填写相关的信息。点击提交按钮后，应用就创建完毕。

> [!WARNING]
>在旧版本的控制台中，需要指定一个应用的操作系统平台类型，用于后续的SDK或API接入。而新版本更新后，这项操作已经不需要，可以通过一个应用管理全部的接口了。
应用创建完成之后，您就可以通过左侧的服务列表，选择您要使用的服务。在服务管理面板中，您将看到这个服务对应的可用量、历史用量、服务接口的验证信息，还有可以调用的API和SDK了。

![](https://www.xfyun.cn/doc/assets/img/manage1.469e7fa3.png)

![](https://www.xfyun.cn/doc/assets/img/manage2.cc025e41.png)

> [!WARNING]
>并不是每个服务的管理面板都相同，不同的服务，有不同的管理面板的构成。另外也不是同时都具有SDK和API接口，有些服务只有API接口，而有些服务只有SDK。具体的可在对应的服务管理页中查看。

讯飞开放平台支持一个账户创建多个应用。当您需要返回应用列表页切换应用，可以点击页面左上角应用名称上方的返回按钮，或顶部右侧个人菜单中的「我的应用」。进入应用列表后，选择一个应用点击应用名称，即可进入这个应用对应的服务管理页。

同一个应用APPID可以用在多个业务上，这个没有限制，但考虑到多个业务共用一个APPID无法分业务统计用量，建议一个业务对应一个应用APPID。

![](https://www.xfyun.cn/doc/assets/img/BACK.75999ee8.png)

> [!WARNING]
>若您的账号下有多个应用，您最后一次操作的应用将会被记录下来，作为下次回到讯飞开放平台时，各个服务操作的“默认选择”的应用。

https://www.xfyun.cn/doc/platform/quickguide.html


== Google Cloud Vision

https://cloud.google.com/vision/docs

== ocrspace

https://ocr.space/

== 大模型通用接口

和[翻译](/zh/guochandamoxing.html)相同

:::


## 离线OCR


::: tabs

== 本地OCR

内置已包含中日英语的轻量级识别模型。如果需要识别其他语言，需要在`资源下载`中添加对应语言的识别模型。

`资源下载`中还提供了中日英语的高精度模型。如果使用的软件版本为Win10版，或系统为Windows11，还可以设置使用GPU运行模型，来提高高精度模型的识别效率。

== SnippingTool

>[!WARNING]
仅支持win10-win11操作系统

如果是最新版windows 11系统则可以直接使用，否则需要在`资源下载`中安装该模块以使用。

== manga-ocr

>[!WARNING]
>此OCR引擎对于横向文本识别不效果不佳。

CPU整合包 https://lunatranslator.org/Resource/IntegrationPack/manga_ocr/cpu

GPU整合包 https://lunatranslator.org/Resource/IntegrationPack/manga_ocr/gpu

#### 国内mangaocr整合包无法启动怎么办？

首次启动start.bat时，会尝试从huggingface上下载模型，但是国内你懂的。

![img](https://image.lunatranslator.org/zh/mangaocr/err1.png)

![img](https://image.lunatranslator.org/zh/mangaocr/err2.png)

解决方法有两种

1. 魔法上网，可能要开TUN代理

1. 使用vscode，“打开文件夹”打开整合包的文件夹。


![img](https://image.lunatranslator.org/zh/mangaocr/fix2.png)

然后使用搜索功能，将“huggingface.co”全部替换成“hf-mirror.com”。由于替换项较多，需要稍微等待一会儿。

![img](https://image.lunatranslator.org/zh/mangaocr/fix.png)

然后重新运行start.bat，之后会用国内镜像站下载模型，无须魔法上网。


![img](https://image.lunatranslator.org/zh/mangaocr/succ.png)


等待一会儿首次运行的下载模型和每次运行都需要的加载模型。显示“`* Running on http://127.0.0.1:5665`”表示服务已正常启动。

== WeChat/QQ OCR

需要安装微信或新版QQ

== WindowsOCR

>[!WARNING]
仅支持win10-win11操作系统

### WindowsOCR如何安装额外的语言支持？

#### 如何查询 OCR 语言包

若要返回所有支持的语言包的列表，请以管理员身份打开 PowerShell（右键单击，然后选择“以管理员身份运行”），并输入以下命令：

```powershell
Get-WindowsCapability -Online | Where-Object { $_.Name -Like 'Language.OCR*' }
```

示例输出：

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

语言和位置为缩写形式，因此“en-US”表示“英语-美国”，“en-GB”则表示“英语-英国”。 如果某个语言在输出中不可用，则 OCR 不支持该语言。 必须先安装 `State: NotPresent` 语言。

#### 如何安装 OCR 语言包

以下为安装“en-US”OCR 包的命令：

```powershell
$Capability = Get-WindowsCapability -Online | Where-Object { $_.Name -Like 'Language.OCR*en-US*' }
$Capability | Add-WindowsCapability -Online
```

#### 如何移除 OCR 语言包

以下为移除“en-US”OCR 包的命令：

```powershell
$Capability = Get-WindowsCapability -Online | Where-Object { $_.Name -Like 'Language.OCR*en-US*' }
$Capability | Remove-WindowsCapability -Online
```

https://learn.microsoft.com/zh-cn/windows/powertoys/text-extractor#supported-languages

== Tesseract5

>[!WARNING]
>效果太差，不推荐使用。

https://github.com/tesseract-ocr/tesseract/releases

:::
