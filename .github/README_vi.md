# LunaTranslator

> **Công cụ dịch Visual Novel**

### [简体中文](README.md) | [English](README_en.md) | [繁體中文](README_cht.md) | [한국어](README_ko.md) | [日本語](README_ja.md) | Tiếng Việt

### Nếu bạn gặp khó khăn khi sử dụng phần mềm, có thể tham khảo [Hướng dẫn sử dụng](https://docs.lunatranslator.org) hoặc tham gia [Discord](https://discord.com/invite/ErtDwVeAbB) của chúng tôi.

## Tính năng hỗ trợ

#### Nhập văn bản

- **HOOK** Hỗ trợ lấy văn bản bằng phương pháp HOOK. Với một số engine, còn hỗ trợ [dịch nhúng](https://docs.lunatranslator.org/embedtranslate.html). Đồng thời hỗ trợ trích xuất văn bản từ game chạy trên các [Trình giả lập](https://docs.lunatranslator.org/emugames.html). Với các game chưa được hỗ trợ hoặc hỗ trợ chưa tốt, vui lòng [gửi phản hồi](https://github.com/HIllya51/LunaTranslator/issues/new?assignees=&labels=enhancement&projects=&template=01_game_request.yaml)

- **OCR** hỗ trợ **[OCR offline](https://docs.lunatranslator.org/useapis/ocrapi.html)** và **[OCR online](https://docs.lunatranslator.org/useapis/ocrapi.html)**

- **Clipboard** Hỗ trợ lấy văn bản từ clipboard để dịch và cũng có thể xuất văn bản trích xuất ra clipboard.

- **Khác** cũng hỗ trợ **[nhận dạng giọng nói](https://docs.lunatranslator.org/sr.html)** và **dịch file**

#### Dịch thuật

Hỗ trợ hầu hết các engine dịch có thể nghĩ đến, bao gồm:

- **Dịch online** Hỗ trợ nhiều giao diện dịch online có thể sử dụng không cần đăng ký, đồng thời hỗ trợ **[dịch truyền thống](https://docs.lunatranslator.org/useapis/tsapi.html)** và **[dịch bằng mô hình lớn](https://docs.lunatranslator.org/guochandamoxing.html)** sử dụng API do người dùng đăng ký

- **Dịch offline** Hỗ trợ các engine **dịch truyền thống** thông dụng và **[dịch bằng mô hình lớn](https://docs.lunatranslator.org/offlinellm.html)** để triển khai offline

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

<details>
<summary>Các dự án tham khảo</summary>

* ![img](https://img.shields.io/github/license/opencv/opencv) [opencv/opencv](https://github.com/opencv/opencv)
* ![img](https://img.shields.io/github/license/microsoft/onnxruntime) [microsoft/onnxruntime](https://github.com/microsoft/onnxruntime)
* ![img](https://img.shields.io/github/license/Artikash/Textractor) [Artikash/Textractor](https://github.com/Artikash/Textractor)
* ![img](https://img.shields.io/github/license/RapidAI/RapidOcrOnnx) [RapidAI/RapidOcrOnnx](https://github.com/RapidAI/RapidOcrOnnx)
* ![img](https://img.shields.io/github/license/PaddlePaddle/PaddleOCR) [PaddlePaddle/PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)
* ![img](https://img.shields.io/github/license/Blinue/Magpie) [Blinue/Magpie](https://github.com/Blinue/Magpie)
* ![img](https://img.shields.io/github/license/nanokina/ebyroid) [nanokina/ebyroid](https://github.com/nanokina/ebyroid)
* ![img](https://img.shields.io/github/license/xupefei/Locale-Emulator) [xupefei/Locale-Emulator](https://github.com/xupefei/Locale-Emulator)
* ![img](https://img.shields.io/github/license/InWILL/Locale_Remulator) [InWILL/Locale_Remulator](https://github.com/InWILL/Locale_Remulator)
* ![img](https://img.shields.io/github/license/zxyacb/ntlea) [zxyacb/ntlea](https://github.com/zxyacb/ntlea)
* ![img](https://img.shields.io/github/license/Chuyu-Team/YY-Thunks) [Chuyu-Team/YY-Thunks](https://github.com/Chuyu-Team/YY-Thunks)
* ![img](https://img.shields.io/github/license/Chuyu-Team/VC-LTL5) [Chuyu-Team/VC-LTL5](https://github.com/Chuyu-Team/VC-LTL5)
* ![img](https://img.shields.io/github/license/uyjulian/AtlasTranslate) [uyjulian/AtlasTranslate](https://github.com/uyjulian/AtlasTranslate)
* ![img](https://img.shields.io/github/license/ilius/pyglossary) [ilius/pyglossary](https://github.com/ilius/pyglossary)
* ![img](https://img.shields.io/github/license/ikegami-yukino/mecab) [ikegami-yukino/mecab](https://github.com/ikegami-yukino/mecab)
* ![img](https://img.shields.io/github/license/AngusJohnson/Clipper2) [AngusJohnson/Clipper2](https://github.com/AngusJohnson/Clipper2)
* ![img](https://img.shields.io/github/license/rapidfuzz/rapidfuzz-cpp) [rapidfuzz/rapidfuzz-cpp](https://github.com/rapidfuzz/rapidfuzz-cpp)
* ![img](https://img.shields.io/github/license/TsudaKageyu/minhook) [TsudaKageyu/minhook](https://github.com/TsudaKageyu/minhook)
* ![img](https://img.shields.io/github/license/lobehub/lobe-icons) [lobehub/lobe-icons](https://github.com/lobehub/lobe-icons)
* ![img](https://img.shields.io/github/license/kokke/tiny-AES-c) [kokke/tiny-AES-c](https://github.com/kokke/tiny-AES-c)
* ![img](https://img.shields.io/github/license/TPN-Team/OCR) [TPN-Team/OCR](https://github.com/TPN-Team/OCR)
* ![img](https://img.shields.io/github/license/AuroraWright/owocr) [AuroraWright/owocr](https://github.com/AuroraWright/owocr)
* ![img](https://img.shields.io/github/license/b1tg/win11-oneocr) [b1tg/win11-oneocr](https://github.com/b1tg/win11-oneocr)
* ![img](https://img.shields.io/github/license/mity/md4c) [mity/md4c](https://github.com/mity/md4c)
* ![img](https://img.shields.io/github/license/swigger/wechat-ocr) [swigger/wechat-ocr](https://github.com/swigger/wechat-ocr)
* ![img](https://img.shields.io/github/license/rupeshk/MarkdownHighlighter) [rupeshk/MarkdownHighlighter](https://github.com/rupeshk/MarkdownHighlighter)
* ![img](https://img.shields.io/github/license/sindresorhus/github-markdown-css) [sindresorhus/github-markdown-css](https://github.com/sindresorhus/github-markdown-css)
* ![img](https://img.shields.io/github/license/gexgd0419/NaturalVoiceSAPIAdapter) [gexgd0419/NaturalVoiceSAPIAdapter](https://github.com/gexgd0419/NaturalVoiceSAPIAdapter)
* ![img](https://img.shields.io/github/license/microsoft/PowerToys) [microsoft/PowerToys](https://github.com/microsoft/PowerToys)
</details>
