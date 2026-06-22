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

### OCR tích hợp {#anchor-localocr}

Đã bao gồm sẵn **PP-OCRv5_mobile** (mô hình nhận dạng nhẹ cho tiếng Trung, Nhật và Anh). Nếu cần nhận dạng ngôn ngữ khác hoặc muốn sử dụng mô hình khác, bạn cần tải xuống mô hình trong phần cài đặt và thiết lập sử dụng.

![img](https://image.lunatranslator.org/zh/localocr.png)

Phần cài đặt cũng cung cấp một số mô hình độ chính xác cao, ví dụ (PP-OCRv6_medium, PP-OCRv5_server), có thể đạt độ chính xác nhận dạng cực cao, nhưng tốc độ nhận dạng tương đối chậm hơn.

| Mô hình | Mô-đun phát hiện Hmean(%) | Mô-đun nhận dạng Avg Accuracy(%) | Ngôn ngữ hỗ trợ | Dung lượng(MB) |
| - | - | - | - | - |
| PP-OCRv6_small | 84.1 | 81.3 | Bất kỳ | 25.2 |
| PP-OCRv6_medium | 86.2 | 83.2 | Bất kỳ | 99.7 |
| PP-OCRv6_tiny | 80.6 | 73.5 | Bất kỳ | 5.45 |
| PP-OCRv5_mobile | 79.0 | 81.29 | Tiếng Trung Giản thể, Tiếng Trung Phồn thể, Tiếng Anh, Tiếng Nhật | 17.7 |
| PP-OCRv5_server | 83.8 | 86.38 | Tiếng Trung Giản thể, Tiếng Trung Phồn thể, Tiếng Anh, Tiếng Nhật | 148 |
| eslav_PP-OCRv5_mobile | 79.0 | 81.6 | Ngôn ngữ Đông Slav | 11.2 |
| korean_PP-OCRv5_mobile | 79.0 | 88.0 | Tiếng Hàn | 12.2 |
| latin_PP-OCRv5_mobile | 79.0 | 84.7 | Ngôn ngữ sử dụng bảng chữ cái Latinh | 11.3 |

Để cải thiện hiệu suất nhận diện của các mô hình độ chính xác cao, có thể áp dụng các biện pháp sau:

1. Sử dụng Suy luận GPU

    Nếu phiên bản phần mềm đang sử dụng là bản Win10 hoặc hệ thống là Windows 11, có thể thiết lập trực tiếp để chạy mô hình bằng GPU.

    ![img](https://image.lunatranslator.org/zh/dml_gpu.png)

1. Sử dụng Suy luận OpenVINO

    Nếu sử dụng CPU/NPU/GPU của Intel, có thể thay thế công cụ suy luận bằng OpenVINO để tăng tốc nhận diện.
    
    Tải xuống [onnxruntime-openvino](https://globalcdn.nuget.org/packages/intel.ml.onnxruntime.openvino.1.23.0.nupkg). Sau khi giải nén, sao chép đè tất cả tệp trong **runtimes/win-x64/native** vào **LunaTranslator/files/DLL64**, sau đó chọn thiết bị sử dụng.

    ![img](https://image.lunatranslator.org/zh/ov_device.png)

### OCR khác

::: tabs

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