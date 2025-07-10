# OCR 인터페이스 설정

## 온라인 OCR {#anchor-online}

::: tabs

== 바이두

#### 바이두 지능형 클라우드 OCR

https://ai.baidu.com/ai-doc/OCR/1k3h7y3db

#### 바이두 지능형 클라우드 이미지 번역

https://ai.baidu.com/ai-doc/MT/dkifdqg54

#### 바이두 번역 오픈 플랫폼 이미지 번역

https://fanyi-api.baidu.com/product/22

== 텐센트

#### OCR 일반 인쇄체 인식

https://cloud.tencent.com/document/product/866/33526

#### 이미지 번역

https://cloud.tencent.com/document/product/551/17232

== 유다오 사전

https://www.patreon.com/posts/high-precision-133319068

== 유다오

https://ai.youdao.com/doc.s#guide

== 화산

https://www.volcengine.com/docs/6790/116978

== 쉰페이

https://www.xfyun.cn/doc/platform/quickguide.html


== Google Cloud Vision

https://cloud.google.com/vision/docs

== ocrspace

https://ocr.space/

== 대형 모델 통합 인터페이스

[번역](/zh/guochandamoxing.html)과 동일

:::


## 오프라인 OCR {#anchor-offline}


::: tabs

== 로컬 OCR

기본적으로 중국어, 일본어, 영어 경량 인식 모델이 내장되어 있습니다. 다른 언어를 인식하려면 '리소스 다운로드'에서 해당 언어의 인식 모델을 추가해야 합니다.

`리소스 다운로드`에는 중국어, 일본어, 영어 고정밀 모델도 제공됩니다. 사용 중인 소프트웨어 버전이 Win10 버전이거나 시스템이 Windows11인 경우, GPU를 사용하여 모델을 실행하도록 설정할 수 있어 고정밀 모델의 인식 효율을 높일 수 있습니다.

== SnippingTool

>[!WARNING]
Win10-Win11 운영체제만 지원됩니다.

최신 버전의 Windows 11 시스템이라면 바로 사용할 수 있지만, 그렇지 않다면 `리소스 다운로드`에서 해당 모듈을 설치해야 사용할 수 있습니다.

== manga-ocr

>[!WARNING]
>이 OCR 엔진은 가로쓰기 텍스트 인식에 효과적이지 않습니다.

CPU 통합 패키지 https://lunatranslator.org/Resource/IntegrationPack/manga_ocr/cpu

GPU 통합 패키지 https://lunatranslator.org/Resource/IntegrationPack/manga_ocr/gpu

#### 중국 내 mangaocr 통합 패키지가 실행되지 않을 경우 해결 방법

start.bat을 처음 실행할 때 huggingface에서 모델을 다운로드하려 시도하지만, 중국 내 상황은 아시다시피 어렵습니다.

![img](https://image.lunatranslator.org/zh/mangaocr/err1.png)

![img](https://image.lunatranslator.org/zh/mangaocr/err2.png)

해결 방법은 두 가지가 있습니다

1. VPN 사용 (TUN 프록시 설정이 필요할 수 있음)

1. vscode를 사용하여，"폴더 열기"로 통합 패키지 폴더를 엽니다。


![img](https://image.lunatranslator.org/zh/mangaocr/fix2.png)

그런 다음 검색 기능을 사용하여 "huggingface.co"를 모두 "hf-mirror.com"으로 교체합니다. 교체할 항목이 많기 때문에 잠시 기다려야 합니다.

![img](https://image.lunatranslator.org/zh/mangaocr/fix.png)

그런 다음 start.bat을 다시 실행하면 이후에는 국내 미러 사이트를 통해 모델을 다운로드하며, VPN이 필요 없습니다.


![img](https://image.lunatranslator.org/zh/mangaocr/succ.png)


첫 실행 시 모델 다운로드와 매번 실행 시 필요한 모델 로딩을 잠시 기다립니다. "`* Running on http://127.0.0.1:5665`"가 표시되면 서비스가 정상적으로 시작된 것입니다.

== WeChat/QQ OCR

위챗(WeChat) 또는 최신 버전 QQ가 설치되어 있어야 합니다.

== WindowsOCR

>[!WARNING]
win10-win11 운영체제만 지원합니다

#### 조회 && 설치 && 제거 OCR 언어 패키지

https://learn.microsoft.com/zh-cn/windows/powertoys/text-extractor#supported-languages

== Tesseract5

>[!WARNING]
>효과가 너무 나빠 사용을 권장하지 않습니다.

https://github.com/tesseract-ocr/tesseract/releases

:::
