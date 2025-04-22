# Tải xuống và Khởi chạy

## Tải xuống

### Hệ thống Windows 7 trở lên

<a href="https://lunatranslator.org/Resource/DownloadLuna/64"> 64-bit <img style="display:inline-block" src="https://img.shields.io/badge/download_64bit-blue"/> </a>

<a href="https://lunatranslator.org/Resource/DownloadLuna/32"> 32-bit <img style="display:inline-block" src="https://img.shields.io/badge/download_32bit-blue"/> </a>

### Hệ thống Windows XP & Vista

<a href="https://lunatranslator.org/Resource/DownloadLuna/xp"> 32-bit <img style="display:inline-block" src="https://img.shields.io/badge/download_32bit_XP-blue"/></a>

## Khởi chạy

Sau khi tải xuống, giải nén các tệp vào bất kỳ thư mục nào.

::: warning
Nhưng vui lòng không đặt phần mềm vào các đường dẫn đặc biệt như **C:\Program Files**, nếu không, ngay cả khi có quyền quản trị viên, bạn có thể không lưu được tệp cấu hình và bộ nhớ đệm hoặc thậm chí không thể chạy chương trình.
:::

- **LunaTranslator.exe** sẽ khởi động ở chế độ bình thường.
- **LunaTranslator_admin.exe** sẽ khởi động với quyền quản trị viên, cần thiết để hook một số trò chơi; chỉ sử dụng khi cần thiết, nếu không hãy khởi động ở chế độ bình thường.
- **LunaTranslator_debug.exe** sẽ hiển thị cửa sổ dòng lệnh.

## Không thể khởi động phần mềm

::: danger
Đôi khi phần mềm có thể bị gắn cờ bởi phần mềm diệt virus. Vui lòng thêm vào danh sách tin cậy và tải xuống, giải nén lại.
:::

### Thiếu các thành phần quan trọng

![img](https://image.lunatranslator.org/zh/cantstart/2.jpg) 

Giải pháp: Tắt phần mềm diệt virus. Nếu không thể tắt (như Windows Defender), thêm vào danh sách tin cậy và sau đó tải xuống lại.

Lưu ý: Để thực hiện việc HOOK trích xuất văn bản trò chơi, cần phải tiêm Dll vào trò chơi. Các tệp như shareddllproxy32.exe/LunaHost32.dll thực hiện điều này, do đó rất dễ bị coi là virus. Phần mềm hiện được tự động xây dựng bởi [Github Actions](https://github.com/HIllya51/LunaTranslator/actions). Trừ khi máy chủ Github bị nhiễm, không thể chứa virus, vì vậy có thể an tâm thêm vào danh sách tin cậy.

::: details Đối với Windows Defender, phương pháp là: “Bảo vệ chống vi-rút & mối đe dọa” -> “Loại trừ” -> “Thêm hoặc xóa loại trừ” -> “Thêm loại trừ” -> “Thư mục”, thêm thư mục của Luna vào
![img](https://image.lunatranslator.org/zh/cantstart/4.png) 
![img](https://image.lunatranslator.org/zh/cantstart/3.png) 
::: 

### Lỗi/PermissionError

Nếu phần mềm được đặt trong các thư mục đặc biệt như `C:\Program Files`, có thể không hoạt động đúng cách.

<img src="https://image.lunatranslator.org/zh/cantstart/6.png"  width=400>
