# Tải xuống phần mềm & Câu hỏi thường gặp

## Tải xuống

| Hệ điều hành | 64-bit |
| - | - |
| Windows 11 & 10(1803+) | <downloadbtn href="https://lunatranslator.org/Resource/DownloadLuna/x64_win10?doc=1"/> |

::: details Phiên bản tương thích hệ điều hành cũ  

>[!WARNING]  
Các phiên bản này có hiệu suất kém hơn, chạy không ổn định, thiếu một số tính năng và chức năng, và dễ bị phần mềm diệt virus báo sai. Không khuyến nghị sử dụng trừ khi có nhu cầu đặc biệt.

| Hệ điều hành | 32-bit | 64-bit |
| - | - | - |
| Windows 7 trở lên | <downloadbtn href="https://lunatranslator.org/Resource/DownloadLuna/x86_win7?doc=1"/> | <downloadbtn href="https://lunatranslator.org/Resource/DownloadLuna/x64_win7?doc=1"/> |
| Windows XP & Vista | <downloadbtn href="https://lunatranslator.org/Resource/DownloadLuna/x86_winxp?doc=1"/> | |

:::

## Cộng đồng & Hỗ trợ tác giả {#anchor-support}
 
Nếu bạn gặp bất kỳ khó khăn nào khi sử dụng phần mềm, bạn có thể tham gia [Discord](https://discord.com/invite/ErtDwVeAbB) của chúng tôi.

<a href="https://discord.gg/invite/ErtDwVeAbB"><img src="https://img.shields.io/discord/1262692128031772733?style=for-the-badge&logo=discord&logoColor=white&label=Discord&color=5865F2" alt="Discord"></a>


Bảo trì phần mềm không dễ dàng, nếu bạn cảm thấy phần mềm này hữu ích, vui lòng hỗ trợ tôi qua [patreon](https://patreon.com/HIllya51). Sự hỗ trợ của bạn sẽ là động lực để duy trì phần mềm lâu dài, cảm ơn~

<a href="https://patreon.com/HIllya51" target='_blank'><img width="200" src="/become_a_patron_4x1_black_logo_white_text_on_coral.svg"></a>

## Khởi chạy & Cập nhật

Sau khi tải xuống, giải nén các tệp vào bất kỳ thư mục nào.

::: warning
Nhưng vui lòng không đặt phần mềm vào các đường dẫn đặc biệt như **C:\Program Files**, nếu không, ngay cả khi có quyền quản trị viên, bạn có thể không lưu được tệp cấu hình và bộ nhớ đệm hoặc thậm chí không thể chạy chương trình.
:::

| LunaTranslator.exe | LunaTranslator_admin.exe | LunaTranslator_debug.bat |
| - | - | - |
| sẽ khởi động ở chế độ bình thường. | sẽ khởi động với quyền quản trị viên, cần thiết để hook một số trò chơi; chỉ sử dụng khi cần thiết, nếu không hãy khởi động ở chế độ bình thường. | sẽ hiển thị cửa sổ dòng lệnh. |


Mặc định sẽ tự động cập nhật. Nếu tự động cập nhật thất bại, có thể cập nhật thủ công.

Nếu muốn cập nhật thủ công, chỉ cần tải phiên bản mới và giải nén đè lên thư mục trước đó.

Nếu muốn xóa và tải lại, chú ý không xóa thư mục userconfig, nếu không sẽ mất thiết lập trước đó!!!


## Lỗi Thường Gặp {#anchor-commonerrors}

### Thiếu các thành phần quan trọng / Missing embedded Python3

::: danger
Đôi khi phần mềm có thể bị gắn cờ bởi phần mềm diệt virus. Vui lòng thêm vào danh sách tin cậy và tải xuống, giải nén lại.
:::

![img](https://image.lunatranslator.org/zh/cantstart/2.jpg) 

![img](https://image.lunatranslator.org/zh/missingpython.png) 

Giải pháp: Tắt phần mềm diệt virus. Nếu không thể tắt (như Windows Defender), thêm vào danh sách tin cậy và sau đó tải xuống lại.

Lưu ý: Để thực hiện việc HOOK trích xuất văn bản trò chơi, cần phải tiêm Dll vào trò chơi. Các tệp như LunaSubprocess32.exe/LunaHost32.dll thực hiện điều này, do đó rất dễ bị coi là virus. Phần mềm hiện được tự động xây dựng bởi [Github Actions](https://github.com/HIllya51/LunaTranslator/actions). Trừ khi máy chủ Github bị nhiễm, không thể chứa virus, vì vậy có thể an tâm thêm vào danh sách tin cậy.

::: details Đối với Windows Defender, phương pháp là: “Bảo vệ chống vi-rút & mối đe dọa” -> “Loại trừ” -> “Thêm hoặc xóa loại trừ” -> “Thêm loại trừ” -> “Thư mục”, thêm thư mục của Luna vào
![img](https://image.lunatranslator.org/zh/cantstart/4.png) 
![img](https://image.lunatranslator.org/zh/cantstart/3.png) 
::: 

### Đang chờ đợi DLL được tiêm vào trò chơi... {#anchor-waitdll}

Cách khắc phục giống như trên.

### Error/FileNotFoundError

Nếu không thêm vào danh sách tin cậy trước, có thể sau một thời gian phần mềm chạy, một số thành phần quan trọng sẽ bị phần mềm diệt virus xóa. Sau đó khi chọn tiến trình trong chế độ HOOK, lỗi này sẽ xuất hiện. Cách khắc phục giống như trên.

<img src="https://image.lunatranslator.org/zh/notfound.png" width=400>

### Error/PermissionError

Nếu phần mềm được đặt trong các thư mục đặc biệt như `C:\Program Files`, có thể không hoạt động đúng cách.

<img src="https://image.lunatranslator.org/zh/cantstart/6.png"  width=400>

## ChangeLog

::: details
<RemoteMarkdown />

:::