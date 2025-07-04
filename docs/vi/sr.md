# Nhận dạng giọng nói

Trên Windows 10 và Windows 11, bạn có thể sử dụng tính năng Nhận dạng giọng nói của Windows.

## Chế độ Gọi Trực tiếp

Chế độ này có thể gọi trực tiếp mô hình nhận dạng giọng nói của Windows, hiệu năng tốt hơn và có thể sử dụng trên Windows 10.

::: warning
Do Microsoft đã thay đổi phương pháp mã hóa đối với các gói ngôn ngữ phiên bản mới, các gói ngôn ngữ đã cài đặt trong hệ thống và các gói ngôn ngữ phiên bản mới tải về không thể sử dụng trực tiếp. Vui lòng tham khảo [bài viết này](https://www.patreon.com/posts/fixing-use-of-on-133196054) để biết cách sử dụng.
:::

Trên Windows 11, hệ thống có thể tự động phát hiện ngôn ngữ đã cài đặt và mô hình nhận dạng giọng nói tương ứng. Trong `Cài đặt cốt lõi` -> `Khác` -> `Nhận dạng giọng nói`, chọn ngôn ngữ bạn muốn nhận dạng và kích hoạt tính năng để bắt đầu sử dụng. Nếu ngôn ngữ bạn cần không xuất hiện trong tùy chọn, hãy cài đặt ngôn ngữ tương ứng trong hệ thống hoặc tìm mô hình nhận dạng cho ngôn ngữ đó và giải nén vào thư mục phần mềm.

Trên Windows 10, hệ thống thiếu các runtime và mô hình nhận dạng cần thiết; hoặc phiên bản Windows 11 quá thấp, phiên bản runtime tích hợp sẵn trong hệ thống quá cũ. Trước tiên, hãy tải xuống [runtime và mô hình nhận dạng ngôn ngữ Trung-Nhật-Anh](https://lunatranslator.org/Resource/DirectLiveCaptions.zip) mà tôi đã đóng gói, giải nén vào thư mục phần mềm, phần mềm sẽ nhận diện runtime và mô hình nhận dạng đã đóng gói, từ đó có thể sử dụng tính năng này.

Nếu cần mô hình nhận dạng ngôn ngữ khác, bạn có thể tự tìm mô hình nhận dạng ngôn ngữ tương ứng. Cách làm như sau:
Tại https://store.rg-adguard.net/, tìm kiếm `MicrosoftWindows.Speech.{LANGUAGE}.1_cw5n1h2txyewy` bằng `PacakgeFamilyName`, trong đó `{LANGUAGE}` là tên ngôn ngữ bạn cần, ví dụ tiếng Pháp là `MicrosoftWindows.Speech.fr-FR.1_cw5n1h2txyewy`. Sau đó, tải xuống phiên bản msix mới nhất và giải nén vào thư mục phần mềm.

::: details store.rg-adguard.net
![img](https://image.lunatranslator.org/zh/srpackage.png)
:::

## Chế độ Đọc Gián tiếp

Chế độ này hoạt động gián tiếp bằng cách đọc văn bản từ cửa sổ **LiveCaptions** và chỉ khả dụng trên Windows 11. Hiệu năng hơi kém hơn nhưng không có vấn đề tương thích về giấy phép hoặc thời gian chạy.

Trên Windows 11, bạn chỉ cần kích hoạt và chuyển sang chế độ này để sử dụng.