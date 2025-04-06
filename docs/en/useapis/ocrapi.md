# OCR interface settings

## Online OCR

::: tabs

== Baidu

#### Baidu Intelligent Cloud OCR

https://ai.baidu.com/ai-doc/OCR/1k3h7y3db

#### Baidu Intelligent Cloud Image Translation

https://ai.baidu.com/ai-doc/MT/dkifdqg54

#### Baidu Translation Open Platform Image Translation

https://fanyi-api.baidu.com/product/22

== Tencent

#### General Printed Text Recognition

https://cloud.tencent.com/document/product/866/33526

#### Image Translation

https://cloud.tencent.com/document/product/551/17232

== Youdao

### Step 1: Become a Developer

Click the "Register/Login" button in the upper right corner of the Zhiyun platform page, register and complete your information to become a developer.

[](https://ai.youdao.com/images/guide-register.png)

### Step 2: Access the Console and Create an Application

After logging in on the official website, you will be automatically redirected to the Zhiyun [Console](https://ai.youdao.com/console/).

[](https://ai.youdao.com/images/app_overview.png)

On the business overview page / application overview page / service details page, click the create application button to enter the [Create Application Page](https://ai.youdao.com/console/#/app-overview/create-application).

[](https://ai.youdao.com/images/create_app.png)

Fill in the application name, select the service and integration method, and fill in other key information to complete the creation.

[](https://ai.youdao.com/images/edit_app.png)

### Step 3: Enter the Service Details Page, View Integration Documentation

Click the service name on the left side of the console to enter the service details page. Click the "Documentation" button under "Integration Method" to access the corresponding technical documentation; click the "SDK Download" button to download the SDK; in the "Examples" section, you can view demos. During the integration process, you may need information such as "Application ID (i.e., APP key)" and "Application Secret Key", which can be viewed in the application overview.

[](https://ai.youdao.com/images/serve_singleton.png)

https://ai.youdao.com/doc.s#guide

== Volcano Engine

#### Step 1: Become a Developer

Please log in to the [Volcano Engine Console](https://console.volcengine.com/auth/login/) with your Volcano Engine account; if you do not yet have a Volcano Engine account, click [Sign Up Now](https://console.volcengine.com/auth/signup?redirectURI=//www.volcengine.com/) to register as a Volcano user.

[](https://lf6-volc-editor.volccdn.com/obj/volcfe/sop-public/upload_d26f7523c21ef8f28cd0008d7357708e.png)

[](https://lf3-volc-editor.volccdn.com/obj/volcfe/sop-public/upload_9984617d3c4af144c282dfa6f1ad4de0.png)

#### Step 2: Enter the Visual Intelligence Console

Example Entry Point 1

* Click [Visual Intelligence](https://console.volcengine.com/ai/console/info), to enter the Visual Intelligence Console

[](https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_a889d07925d5038ac33be49dfb7beab7.png)

Example Entry Point 2

* Click the [Management Console] button on the visual-related product landing page

[](https://lf6-volc-editor.volccdn.com/obj/volcfe/sop-public/upload_32871d39e485111ce66039264856a4c2.png)

Example Entry Point 3

* Click the visual-related products in the AI platform's navigation list to enter the Visual Intelligence Console page

[](https://lf3-volc-editor.volccdn.com/obj/volcfe/sop-public/upload_2ab1ccb501a1345a3cf90055a4329adc.png)

#### Step 3: Real-name Authentication and Service Activation

STEP1: Click [Go to Authentication] on the welcome card at the top to complete real-name authentication before activating services. If real-name authentication is not completed, a pop-up window will appear prompting for authentication.

[](https://lf6-volc-editor.volccdn.com/obj/volcfe/sop-public/upload_f01f78cd9672eb0db63bcb172ace7094.png)

[](https://lf3-volc-editor.volccdn.com/obj/volcfe/sop-public/upload_915b51d1f04bb495d28e64f9fb65b78a.png)

STEP2: After completing the authentication, enter the Visual Intelligence Console and choose the capabilities to integrate.

[](https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_297a72f14b481766baae8079694448ef.png)

[](https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_23670c5d7aea4386eee69564b0dc58e6.png)

[](https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_30ae3a108f712d90274aaa1247a4001b.png)

You can also directly find a specific service you need on the page and click to activate it.

[](https://portal.volccdn.com/obj/volcfe/cloud-universal-doc/upload_cc39d6874e0b5e68d541d81c8d028851.png)

#### Step 4: Obtain AK/SK

Before calling various capabilities of the Volcano Engine Visual Intelligence Console, ensure that you have generated an access key (AccessKey). The AccessKey includes AccessKeyID (AK) and AccessKeySecret (SK), where AccessKeyID identifies the user, and AccessKeySecret is used to verify the user's identity. Please keep it safe.

To obtain: Click the account in the upper right corner, select [Key Management] from the drop-down list, and click the [Create New Key] button to get the AK/SK, which can be used as credentials to call interfaces of the applications you have integrated.

[](https://lf6-volc-editor.volccdn.com/obj/volcfe/sop-public/upload_88753005e8633cb897faa097223a05fd.png)

[](https://lf3-volc-editor.volccdn.com/obj/volcfe/sop-public/upload_9d0ce0314c4f43f00b8298497e27742f.png)

[](https://lf6-volc-editor.volccdn.com/obj/volcfe/sop-public/upload_ab865eca01c5cef188c4841d22d747fa.png)

https://www.volcengine.com/docs/6790/116978

== Xunfei

### Step 1: Register as a Developer

Enter the [Xunfei Open Platform Quick Login Page](https://passport.xfyun.cn/login), log in via WeChat scan code or mobile quick login to quickly become a registered developer on the Xunfei Open Platform. Or go to the [Xunfei Open Platform Registration Page](https://passport.xfyun.cn/register) to register a complete open platform account and become a registered developer on the Xunfei Open Platform.

### Step 2: Create Your First Application and Start Using Services

Log in to the platform and go to the console through the "Console" in the upper right corner, or the "My Applications" in the drop-down menu in the upper right corner. If your account has never created an application, we will guide you to create your first application.

[](https://www.xfyun.cn/doc/assets/img/creatapp.7d53afaa.png)

Name your application and fill in the relevant information. After clicking the submit button, your application will be created.

> [!WARNING]
>In the old version of the console, you needed to specify the operating system platform type of the application for subsequent SDK or API integration. However, after the update to the new version, this operation is no longer required, and all interfaces can be managed through one application.

After the application is created, you can choose the service you want to use through the service list on the left. In the service management panel, you will see the available quota, historical usage, verification information for the service interface, and the APIs and SDKs that can be called.

[](https://www.xfyun.cn/doc/assets/img/manage1.469e7fa3.png)

[](https://www.xfyun.cn/doc/assets/img/manage2.cc025e41.png)


> [!WARNING]
>Not every service management panel is the same. Different services have different compositions of their management panels. Also, not all services have both SDK and API interfaces; some services only have API interfaces, while others only have SDKs. Specifics can be found on the corresponding service management page.


The Xunfei Open Platform supports creating multiple applications with one account. To return to the application list page and switch applications, click the return button above the application name in the upper left corner of the page, or the "My Applications" in the personal menu in the top right. In the application list, select an application and click its name to enter the service management page corresponding to that application.

The same application APPID can be used across multiple businesses without restriction, but since multiple businesses sharing one APPID cannot track usage separately, it is recommended to use a separate application APPID for each business.

[](https://www.xfyun.cn/doc/assets/img/BACK.75999ee8.png)

> [!WARNING]
>If your account has multiple applications, the last application you operated will be recorded and set as the default application when you return to the Xunfei Open Platform for various service operations.

https://www.xfyun.cn/doc/platform/quickguide.html

== Google Cloud Vision

https://cloud.google.com/vision/docs

== Ocr.space

https://ocr.space/

== General Large Model Interface

Same as [Translation](/en/guochandamoxing.html)

:::

## Offline OCR

::: tabs

== Local OCR

The built-in package includes a Japanese recognition model. 

If you need to recognize other languages, you must download the corresponding language recognition model from `Resource Download`.

== SnippingTool

If you are using the latest version of Windows 11, you can use it directly. 

Otherwise, you need to install this module from `Resource Download` to enable its functionality.

== Manga-OCR

>[!WARNING]
>This OCR engine performs poorly in recognizing horizontal text.

CPU Integration Package https://lunatranslator.org/Resource/IntegrationPack/manga_ocr/cpu

GPU Integration Package https://lunatranslator.org/Resource/IntegrationPack/manga_ocr/gpu

== WeChat/QQ OCR

Requires installation of WeChat or the latest version of QQ


== WindowsOCR

>[!WARNING]
> WindowsOCR only supports Windows 10 and Windows 11 operating systems.

### How to Install Additional Language Support for WindowsOCR?

#### How to query for OCR language packs

To return the list of all supported language packs, open PowerShell as an Administrator (right-click, then select "Run as Administrator") and enter the following command:

```
Get-WindowsCapability -Online | Where-Object { $_.Name -Like 'Language.OCR*' }
```

An example output:

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

The language and location is abbreviated, so "en-US" would be "English-United States" and "en-GB" would be "English-Great Britain". If a language is not available in the output, then it's not supported by OCR. `State: NotPresent` languages must be installed first.

#### How to install an OCR language pack

The following commands install the OCR pack for "en-US":

```
$Capability = Get-WindowsCapability -Online | Where-Object { $_.Name -Like 'Language.OCR*en-US*' }`
$Capability | Add-WindowsCapability -Online
```

#### How to remove an OCR language pack

The following commands remove the OCR pack for "en-US":

```
$Capability = Get-WindowsCapability -Online | Where-Object { $_.Name -Like 'Language.OCR*en-US*' }
$Capability | Remove-WindowsCapability -Online
```

https://learn.microsoft.com/en-us/windows/powertoys/text-extractor#supported-languages

== Tesseract5

https://github.com/tesseract-ocr/tesseract/releases

:::