# Tải xuống và Khởi chạy

## Tải xuống

### Hệ thống Windows 7 trở lên

<a href="https://lunatranslator.org/Resource/DownloadLuna/64"> 64-bit <img style="display:inline-block" src="https://img.shields.io/badge/download_64bit-blue"/> </a>

<a href="https://lunatranslator.org/Resource/DownloadLuna/32"> 32-bit <img style="display:inline-block" src="https://img.shields.io/badge/download_32bit-blue"/> </a>

### Hệ thống Windows XP & Vista

<a href="https://lunatranslator.org/Resource/DownloadLuna/xp"> 32-bit <img style="display:inline-block" src="https://img.shields.io/badge/download_32bit_XP-blue"/></a>

## Khởi chạy

Sau khi tải xuống, giải nén các tệp vào bất kỳ thư mục nào.

- **LunaTranslator.exe** sẽ khởi động ở chế độ bình thường.
- **LunaTranslator_admin.exe** sẽ khởi động với quyền quản trị viên, điều này cần thiết để hook một số trò chơi; chỉ sử dụng khi cần thiết, nếu không hãy khởi động ở chế độ bình thường.
- **LunaTranslator_debug.exe** sẽ hiển thị cửa sổ dòng lệnh.


## Không thể Khởi động Phần mềm

::: danger
Đôi khi phần mềm có thể bị cảnh báo bởi phần mềm diệt virus. Vui lòng thêm nó vào danh sách tin cậy và tải xuống và giải nén lại.
:::

### Thiếu Các Thành phần Quan trọng

![img](https://image.lunatranslator.org/zh/cantstart/2.jpg) 

Giải pháp: Đóng phần mềm diệt virus. Nếu không thể đóng (như Windows Defender), hãy thêm nó vào danh sách tin cậy và sau đó tải xuống lại.

Lưu ý: Để thực hiện trích xuất văn bản trò chơi bằng HOOK, cần phải chèn Dll vào trò chơi. Các tệp như shareddllproxy32.exe/LunaHost32.dll thực hiện điều này, và do đó đặc biệt có khả năng bị coi là virus. Phần mềm hiện được xây dựng tự động bởi [Github Actions](https://github.com/HIllya51/LunaTranslator/actions). Trừ khi máy chủ Github bị nhiễm virus, không thể chứa virus, vì vậy có thể an toàn thêm vào danh sách tin cậy.

::: details Đối với Windows Defender, phương pháp là: "Bảo vệ virus & mối đe dọa" -> "Loại trừ" -> "Thêm hoặc xóa loại trừ" -> "Thêm loại trừ" -> "Thư mục", thêm thư mục của Luna vào đó
![img](https://image.lunatranslator.org/zh/cantstart/4.png) 
![img](https://image.lunatranslator.org/zh/cantstart/3.png) 
::: 

### Lỗi/PermissionError

Nếu phần mềm được đặt trong các thư mục đặc biệt như `Program Files`, nó có thể không có quyền đọc và ghi. Vui lòng chạy với quyền quản trị viên.

<img src="https://image.lunatranslator.org/zh/cantstart/6.png"  width=400>
