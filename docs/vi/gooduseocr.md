# Liên kết cửa sổ trò chơi trong chế độ OCR

Theo mặc định, `Tự động liên kết cửa sổ sau khi chọn phạm vi OCR` được kích hoạt; khi bốn góc của khung chọn thuộc về một HWND cửa sổ duy nhất, nó sẽ tự động liên kết với cửa sổ đó.

Thông thường, một khía cạnh rất gây thất vọng khi sử dụng phần mềm OCR khác là thường phải chú ý đến vị trí của cửa sổ trò chơi và cửa sổ dịch. Có thể gây khó chịu nếu cửa sổ dịch giao nhau với khu vực chụp màn hình hoặc nếu cửa sổ trò chơi cần được chuyển ra nền.

Tuy nhiên, cài đặt **Liên kết cửa sổ** của Luna giải quyết hoàn hảo sự khó chịu này.

Nhấp vào nút **Liên kết cửa sổ**, sau đó nhấp vào cửa sổ trò chơi. Nút chuyển sang màu hồng, cho biết rằng cửa sổ trò chơi đã được liên kết thành công.

![img](https://image.lunatranslator.org/zh/gooduseocr/bind.png)

![img](https://image.lunatranslator.org/zh/gooduseocr/bindok.png)

Khi điều này xảy ra, sẽ có một số thay đổi đáng kể:

1. **Ảnh chụp màn hình sẽ chỉ chụp cửa sổ trò chơi và không chụp bất kỳ cửa sổ nào khác không phải trò chơi.** Bằng cách này, cửa sổ dịch có thể được đặt ở bất kỳ đâu mà không gây ra thay đổi đáng kể do giao nhau với khu vực chụp màn hình. Ngoài ra, khi cửa sổ trò chơi bị che khuất bởi một cửa sổ khác, ảnh chụp màn hình vẫn sẽ chỉ chụp cửa sổ trò chơi.

2. **Vùng OCR sẽ di chuyển đồng bộ với cửa sổ trò chơi khi cửa sổ trò chơi di chuyển.** Do đó, khi bạn cần di chuyển cửa sổ trò chơi đôi khi, không cần phải di chuyển khung OCR, đặc biệt nếu bạn đã ẩn khung. Sẽ không cần phải hiển thị-di chuyển-ẩn nó lại.

Ngoài những lợi ích này, còn có những ưu điểm khác khi liên kết cửa sổ trò chơi:

1. Tính năng chụp màn hình trò chơi có thể chụp cửa sổ trò chơi chính xác hơn.

2. Chức năng theo dõi thời gian chơi có thể ghi lại thời gian chính xác hơn.

3. Bạn có thể sử dụng Magpie tích hợp hoặc gọi Magpie đã tải xuống của riêng bạn thông qua nút công cụ.

4. Bạn có thể lấy vị trí của trò chơi và ID nội bộ từ handle cửa sổ, cho phép một số cài đặt cá nhân hóa cho trò chơi, bao gồm cài đặt ngôn ngữ/TTS/tối ưu hóa dịch thuật/xử lý văn bản/Anki chuyên dụng, v.v.