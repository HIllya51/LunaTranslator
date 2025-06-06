# Nhận dạng giọng nói

Trên Windows 10 và Windows 11, bạn có thể sử dụng tính năng Nhận dạng giọng nói của Windows.

Trên Windows 11, hệ thống có thể tự động phát hiện ngôn ngữ đã cài đặt và mô hình nhận dạng giọng nói tương ứng. Trong `Cài đặt cốt lõi` -> `Khác` -> `Nhận dạng giọng nói`, chọn ngôn ngữ bạn muốn nhận dạng và kích hoạt tính năng để bắt đầu sử dụng. Nếu ngôn ngữ bạn cần không xuất hiện trong tùy chọn, hãy cài đặt ngôn ngữ tương ứng trong hệ thống hoặc tìm mô hình nhận dạng cho ngôn ngữ đó và giải nén vào thư mục phần mềm.

Trên Windows 10, hệ thống thiếu runtime cần thiết và mô hình nhận dạng. Trước tiên, hãy tải xuống [runtime và mô hình nhận dạng tiếng Trung/Nhật đã được đóng gói sẵn](https://1drv.ms/u/c/e598ac1f7a133b29/EaAWXcYACl9KnKHtuzMg2csB0XBGhR2d3-136PhM8B7B8Q?e=zE1dwj) và giải nén vào thư mục phần mềm. Phần mềm sẽ nhận diện runtime và mô hình nhận dạng đã đóng gói, từ đó cho phép sử dụng tính năng này.

:::warning
Nếu bạn đang sử dụng Windows 10, không đặt phần mềm và "runtime và mô hình nhận dạng ngôn ngữ Trung-Nhật" trong đường dẫn không phải tiếng Anh, nếu không nó sẽ không thể nhận dạng.
:::

Nếu bạn cần mô hình nhận dạng ngôn ngữ khác, bạn có thể tự tìm mô hình nhận dạng tương ứng. Phương pháp như sau:
Truy cập https://store.rg-adguard.net/, tìm kiếm `MicrosoftWindows.Speech.{LANGUAGE}.1_cw5n1h2txyewy` bằng `PacakgeFamilyName`, trong đó `{LANGUAGE}` là tên ngôn ngữ bạn cần. Ví dụ, tiếng Anh là `MicrosoftWindows.Speech.en-US.1_cw5n1h2txyewy`. Sau đó, tải xuống phiên bản msix mới nhất ở bên dưới và giải nén vào thư mục phần mềm.

![img](https://image.lunatranslator.org/zh/srpackage.png)