# Công cụ Tổng hợp Giọng nói

::: tabs

== Windows TTS

Đối với Windows 7 trở lên, bạn có thể thêm gói tổng hợp giọng nói của ngôn ngữ trong cài đặt ngôn ngữ của hệ thống để sử dụng.

Đối với Windows 11, ngoài gói tổng hợp giọng nói của ngôn ngữ, bạn cũng có thể thêm thư viện giọng nói tự nhiên của Trình tường thuật (Narrator) trong cài đặt hệ thống. Tuy nhiên, hiện tại thư viện giọng nói tự nhiên không thể được SAPI nhận dạng, do đó không thể sử dụng trực tiếp trong LunaTranslator. Nhưng, bạn có thể cài đặt [NaturalVoiceSAPIAdapter](https://github.com/gexgd0419/NaturalVoiceSAPIAdapter). Chương trình này có thể chuyển đổi thư viện giọng nói tự nhiên sang giao diện SAPI, nhờ đó cho phép sử dụng chúng trong LunaTranslator.

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