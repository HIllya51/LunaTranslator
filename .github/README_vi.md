### [简体中文](README.md) | [English](README_en.md) | [繁體中文](README_cht.md) | [한국어](README_ko.md) | [日本語](README_ja.md) | Tiếng Việt

# LunaTranslator

> **Công cụ dịch Visual Novel**

### Nếu bạn gặp khó khăn khi sử dụng phần mềm, có thể tham khảo [Hướng dẫn sử dụng](https://docs.lunatranslator.org/vi) hoặc tham gia [Discord](https://discord.com/invite/ErtDwVeAbB) của chúng tôi.

## Tính năng hỗ trợ

#### Nhập văn bản

- **HOOK** Hỗ trợ lấy văn bản bằng phương pháp HOOK. Với một số engine, còn hỗ trợ [dịch nhúng](https://docs.lunatranslator.org/vi/embedtranslate.html). Đồng thời hỗ trợ trích xuất văn bản từ game chạy trên các [Trình giả lập](https://docs.lunatranslator.org/vi/emugames.html). Với các game chưa được hỗ trợ hoặc hỗ trợ chưa tốt, vui lòng [gửi phản hồi](https://github.com/HIllya51/LunaTranslator/issues/new?assignees=&labels=enhancement&projects=&template=01_game_request.yaml)

- **OCR** hỗ trợ **[OCR offline](https://docs.lunatranslator.org/vi/useapis/ocrapi.html)** và **[OCR online](https://docs.lunatranslator.org/vi/useapis/ocrapi.html)**

- **Clipboard** Hỗ trợ lấy văn bản từ clipboard để dịch và cũng có thể xuất văn bản trích xuất ra clipboard.

- **Khác** cũng hỗ trợ **[nhận dạng giọng nói](https://docs.lunatranslator.org/vi/sr.html)** và **dịch file**

#### Dịch thuật

Hỗ trợ hầu hết các engine dịch có thể nghĩ đến, bao gồm:

- **Dịch online** Hỗ trợ nhiều giao diện dịch online có thể sử dụng không cần đăng ký, đồng thời hỗ trợ **[dịch truyền thống](https://docs.lunatranslator.org/vi/useapis/tsapi.html)** và **[dịch bằng mô hình lớn](https://docs.lunatranslator.org/vi/guochandamoxing.html)** sử dụng API do người dùng đăng ký

- **Dịch offline** Hỗ trợ các engine **dịch truyền thống** thông dụng và **[dịch bằng mô hình lớn](https://docs.lunatranslator.org/vi/offlinellm.html)** để triển khai offline

- **Dịch trước** Hỗ trợ đọc file dịch trước, hỗ trợ lưu cache bản dịch

- **Hỗ trợ mở rộng dịch tùy chỉnh** Hỗ trợ mở rộng các giao diện dịch khác bằng ngôn ngữ Python

#### Chức năng khác

- **Chuyển văn bản thành giọng nói** hỗ trợ **TTS offline** và **TTS online**

- **Phân tách từ tiếng Nhật và hiển thị kana** Hỗ trợ phân tách từ và hiển thị kana bằng Mecab, v.v.

- **Tra từ điển** Hỗ trợ **từ điển offline** (MDICT) và **từ điển online** để tra từ

- **Anki** Hỗ trợ thêm từ vào Anki bằng một cú nhấp chuột

- **Tải tiện ích mở rộng trình duyệt** Các tiện ích mở rộng trình duyệt như Yomitan có thể được tải trong phần mềm để hỗ trợ triển khai các tính năng bổ sung.

## Tài trợ

Việc bảo trì phần mềm không dễ dàng. Nếu bạn thấy phần mềm này hữu ích, hãy ủng hộ tôi qua [Patreon](https://patreon.com/HIllya51). Sự ủng hộ của bạn sẽ góp phần duy trì phần mềm lâu dài. Cảm ơn~

<a href="https://patreon.com/HIllya51" target='_blank'><img width="200" src="../docs/become_a_patron_4x1_black_logo_white_text_on_coral.svg"></a>

## Giấy phép mã nguồn mở

LunaTranslator sử dụng giấy phép [GPLv3](../LICENSE).
