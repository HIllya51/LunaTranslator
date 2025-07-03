# Công cụ Tổng hợp Giọng nói

::: tabs

== Windows TTS

Đối với Windows 7 trở lên, bạn có thể thêm gói tổng hợp giọng nói của ngôn ngữ trong cài đặt ngôn ngữ của hệ thống để sử dụng.

~~Trên Windows 11, ngoài gói tổng hợp giọng nói của ngôn ngữ, bạn cũng có thể thêm các giọng nói tự nhiên chất lượng cao hơn tại `Trợ năng` -> `Trình tường thuật` -> `Thêm giọng nói tự nhiên`.~~ Do Microsoft đã thay đổi phương pháp mã hóa của gói giọng nói tự nhiên và âm thầm cập nhật, hiện không thể sử dụng trực tiếp các gói giọng nói tự nhiên đã cài đặt trong hệ thống. Vui lòng sử dụng các phương pháp sau hoặc tham khảo [bài viết này](https://www.patreon.com/posts/fixing-use-of-on-133196054).

Trên Windows 11, bạn có thể tải `Microsoft Natural Voice (Giọng nói tự nhiên)` từ [Trang NVDA tiếng Trung](https://www.nvdacn.com/index.php/tts.html) và giải nén vào thư mục phần mềm để sử dụng giọng nói tự nhiên. Trên Windows 10, ngoài việc tải gói giọng nói, bạn cần tải thêm [Runtime Giọng nói tự nhiên](https://lunatranslator.org/Resource/microsoft.cognitiveservices.speech) và giải nén vào thư mục phần mềm.

== VoiceRoid2

Trong phần tải tài nguyên, bạn có thể tải xuống các tài nguyên liên quan, sau đó chọn đường dẫn giải nén là được.

Tuy nhiên, xin lưu ý rằng đối với **nguồn âm thanh bổ sung**, bạn phải tải xuống bất kỳ **gói tích hợp** nào trước, sau đó giải nén nó vào trong gói tích hợp thì mới có thể sử dụng. Bởi vì gói tích hợp chứa các nguồn âm thanh tương đối phổ biến và các runtime cần thiết; việc chỉ tải xuống nguồn âm thanh bổ sung sẽ thiếu runtime của VoiceRoid2.

== VOICEVOX

Cần tải xuống [VOICEVOX](https://github.com/VOICEVOX/voicevox/releases) và chạy nó.

Số cổng mặc định giống với số cổng mặc định của VOICEVOX. Nếu bạn không thay đổi cài đặt của cả hai bên, chỉ cần chạy và kích hoạt là có thể sử dụng.

== GPT-SoVITS

v2 trong `API version` là phiên bản giao diện API của GPT-SoVITS, không phải là phiên bản của mô hình. Trong trường hợp thông thường, sử dụng v2 mặc định là được.

Trong các tham số khác, chỉ có một số ít tham số thường dùng được thêm vào. Nếu bạn cần các tham số khác, bạn có thể tự thêm chúng.

:::