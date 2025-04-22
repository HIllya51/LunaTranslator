# Liên Kết Cửa Sổ Trò Chơi trong Chế Độ OCR

Mặc định, tùy chọn `Tự động liên kết cửa sổ sau khi chọn phạm vi OCR` được kích hoạt; khi bốn góc của khung chọn thuộc về một cửa sổ HWND duy nhất, nó sẽ tự động liên kết với cửa sổ đó.

Thông thường, một khía cạnh rất khó chịu khi sử dụng phần mềm OCR khác là phải chú ý đến vị trí của cửa sổ trò chơi và cửa sổ dịch thuật. Điều này có thể gây phiền toái nếu cửa sổ dịch thuật giao nhau với khu vực chụp màn hình hoặc nếu cần chuyển cửa sổ trò chơi ra nền.

Tuy nhiên, cài đặt **Liên Kết Cửa Sổ** của Luna hoàn toàn giải quyết được sự phiền toái này.

Nhấn nút **Liên Kết Cửa Sổ**, sau đó nhấp vào cửa sổ trò chơi. Nút sẽ chuyển sang màu hồng, cho biết rằng cửa sổ trò chơi đã được liên kết thành công.

![img](https://image.lunatranslator.org/zh/gooduseocr/bind.png)

![img](https://image.lunatranslator.org/zh/gooduseocr/bindok.png)

Khi điều này xảy ra, sẽ có một số thay đổi đáng kể:

1. **Ảnh chụp màn hình sẽ chỉ chụp cửa sổ trò chơi và không chụp bất kỳ cửa sổ không phải trò chơi nào khác.** Nhờ đó, cửa sổ dịch thuật có thể được đặt ở bất kỳ đâu mà không gây ra thay đổi lớn do giao nhau với khu vực chụp màn hình. Ngoài ra, khi cửa sổ trò chơi bị che bởi một cửa sổ khác, ảnh chụp màn hình vẫn chỉ chụp cửa sổ trò chơi.

2. **Vùng OCR sẽ di chuyển đồng bộ với cửa sổ trò chơi khi cửa sổ trò chơi di chuyển.** Vì vậy, khi bạn cần di chuyển cửa sổ trò chơi, không cần phải di chuyển khung OCR, đặc biệt nếu bạn đã ẩn khung. Không cần phải hiển thị-di chuyển-ẩn lại.

Ngoài những lợi ích này, còn có các ưu điểm khác khi liên kết cửa sổ trò chơi:

1. Tính năng chụp màn hình trò chơi có thể chụp chính xác hơn cửa sổ trò chơi.

2. Chức năng theo dõi thời gian chơi có thể ghi lại thời gian chính xác hơn.

3. Bạn có thể sử dụng Magpie tích hợp hoặc gọi Magpie đã tải xuống của riêng bạn thông qua nút công cụ.

4. Bạn có thể lấy vị trí và ID nội bộ của trò chơi từ handle cửa sổ, cho phép tùy chỉnh một số cài đặt cá nhân cho trò chơi, bao gồm ngôn ngữ/TTS/dịch thuật tối ưu hóa/xử lý văn bản/cài đặt Anki chuyên dụng, v.v.