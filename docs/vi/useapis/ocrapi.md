# Cài đặt giao diện OCR

## OCR Trực tuyến {#anchor-online}

::: tabs

== Baidu

#### Baidu Intelligent Cloud OCR

https://ai.baidu.com/ai-doc/OCR/1k3h7y3db

#### Baidu Intelligent Cloud Image Translation

https://ai.baidu.com/ai-doc/MT/dkifdqg54

#### Baidu Translation Open Platform Image Translation

https://fanyi-api.baidu.com/product/22

== Tencent

#### Nhận dạng Văn bản In Tổng quát

https://cloud.tencent.com/document/product/866/33526

#### Dịch Hình Ảnh

https://cloud.tencent.com/document/product/551/17232

== Youdao

https://ai.youdao.com/doc.s#guide

== Volcano Engine

https://www.volcengine.com/docs/6790/116978

== Xunfei

https://www.xfyun.cn/doc/platform/quickguide.html

== Google Cloud Vision

https://cloud.google.com/vision/docs

== Ocr.space

https://ocr.space/

== General Large Model Interface

Giống như [Dịch thuật](/en/guochandamoxing.html)

:::

## OCR Ngoại tuyến {#anchor-offline}

::: tabs

== OCR tích hợp

Đã bao gồm sẵn **PP-OCRv5_mobile** (mô hình nhận dạng nhẹ cho tiếng Trung, Nhật và Anh). Nếu cần nhận dạng ngôn ngữ khác hoặc muốn sử dụng mô hình khác, bạn cần tải xuống mô hình trong phần cài đặt và thiết lập sử dụng.

![img](https://image.lunatranslator.org/zh/localocr.png)

Phần cài đặt cũng cung cấp một số mô hình độ chính xác cao, ví dụ (PP-OCRv6_medium, PP-OCRv5_server), có thể đạt độ chính xác nhận dạng cực cao, nhưng tốc độ nhận dạng tương đối chậm hơn.


Để cải thiện hiệu suất nhận diện của các mô hình độ chính xác cao, có thể áp dụng các biện pháp sau:

1. Sử dụng Suy luận GPU

    Nếu phiên bản phần mềm đang sử dụng là bản Win10 hoặc hệ thống là Windows 11, có thể thiết lập trực tiếp để chạy mô hình bằng GPU.

    ![img](https://image.lunatranslator.org/zh/dml_gpu.png)

1. Sử dụng Suy luận OpenVINO

    Nếu sử dụng CPU/NPU/GPU của Intel, có thể thay thế công cụ suy luận bằng OpenVINO để tăng tốc nhận diện.
    
    Tải xuống [onnxruntime-openvino](https://globalcdn.nuget.org/packages/intel.ml.onnxruntime.openvino.1.23.0.nupkg). Sau khi giải nén, sao chép đè tất cả tệp trong **runtimes/win-x64/native** vào **LunaTranslator/files/DLL64**, sau đó chọn thiết bị sử dụng.

    ![img](https://image.lunatranslator.org/zh/ov_device.png)

== SnippingTool

>[!WARNING]
>Chỉ hỗ trợ hệ điều hành Windows 10 và Windows 11.

Nếu bạn đang sử dụng phiên bản Windows 11 mới nhất thì có thể sử dụng trực tiếp, nếu không thì cần cài đặt mô-đun này trong phần Cài đặt để sử dụng.
![img](https://image.lunatranslator.org/zh/snip.png)

== Manga-OCR

>[!WARNING]
>Công cụ OCR này hoạt động kém trong việc nhận dạng văn bản ngang.

Gói Tích hợp CPU https://lunatranslator.org/Resource/IntegrationPack/manga_ocr/cpu

Gói Tích hợp GPU https://lunatranslator.org/Resource/IntegrationPack/manga_ocr/gpu

== WeChat/QQ OCR

Yêu cầu cài đặt WeChat hoặc phiên bản mới nhất của QQ

== WindowsOCR

>[!WARNING]
>Hiệu suất kém, không khuyến nghị sử dụng.

>[!WARNING]
>Chỉ hỗ trợ hệ điều hành Windows 10 và Windows 11.

#### Truy vấn && Cài đặt && Gỡ bỏ gói ngôn ngữ OCR  

https://learn.microsoft.com/en-us/windows/powertoys/text-extractor#supported-languages

== Tesseract5

>[!WARNING]
>Hiệu suất kém, không khuyến nghị sử dụng.

https://github.com/tesseract-ocr/tesseract/releases

:::