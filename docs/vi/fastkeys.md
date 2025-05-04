# Phím Tắt
::: tip
 Để sử dụng phím tắt, trước tiên bạn cần kích hoạt `Sử dụng phím tắt`, sau đó kích hoạt phím tắt cụ thể mà bạn muốn sử dụng và thiết lập tổ hợp phím của nó.
:::

::: tabs

== Chung

1. #### Dịch Thủ Công
    Đọc đầu vào một lần từ nguồn đầu vào văn bản hiện tại và thực hiện dịch.
    Ví dụ: nếu chế độ hiện tại là OCR, nó sẽ thực hiện OCR lại.

1. #### Dịch Tự Động
    Tạm dừng/tiếp tục đọc văn bản tự động từ nguồn đầu vào văn bản hiện tại.
    Ví dụ: nếu chế độ hiện tại là HOOK, nó sẽ tạm dừng đọc văn bản trò chơi; nếu chế độ hiện tại là OCR, nó sẽ tạm dừng nhận diện hình ảnh tự động; nếu chế độ hiện tại là clipboard, nó sẽ tạm dừng đọc tự động từ clipboard.

1. #### Mở Cài Đặt
    Không áp dụng.

1. #### Hiện/Ẩn Văn Bản Gốc
    Chuyển đổi việc hiển thị văn bản gốc, có hiệu lực ngay lập tức.

1. #### Hiện/Ẩn Dịch Thuật
    Chuyển đổi việc sử dụng dịch thuật, đây là công tắc chính cho dịch thuật. Tắt nó sẽ dừng mọi dịch thuật.
    Nếu dịch thuật đã được thực hiện, tắt nó sẽ ẩn kết quả dịch, và bật lại sẽ hiển thị lại kết quả dịch hiện tại.
    Nếu chưa có dịch thuật nào được thực hiện và nó được chuyển từ ẩn sang hiển thị, nó sẽ kích hoạt dịch thuật cho câu hiện tại.

1. #### Hiện/Ẩn Văn Bản Lịch Sử  
    Mở hoặc đóng cửa sổ văn bản lịch sử.  

1. #### Cửa Sổ Xuyên Chuột
    Chuyển đổi trạng thái cửa sổ xuyên chuột.
    Tính năng này phải được sử dụng cùng với nút công cụ cửa sổ xuyên chuột để hoạt động chính xác.

1. #### Khóa Thanh Công Cụ
    Khi thanh công cụ không bị khóa, nó sẽ tự động ẩn khi chuột di chuyển ra ngoài; kích hoạt tính năng này sẽ giữ thanh công cụ luôn hiển thị.
    Khi thanh công cụ không bị khóa và `Cửa Sổ Xuyên Chuột` được kích hoạt, thanh công cụ sẽ chỉ hiển thị khi chuột di chuyển đến **nút Cửa Sổ Xuyên Chuột và khu vực bên trái và phải của nó**; nếu không, nó sẽ hiển thị ngay khi chuột vào cửa sổ dịch thuật.
    Nếu sử dụng hiệu ứng cửa sổ (Aero/Acrylic) và thanh công cụ không bị khóa, thanh công cụ sẽ nằm trong khu vực trục z phía trên khu vực văn bản, không phải trên trục y phía trên khu vực văn bản. Điều này là do, với Windows, khi sử dụng hiệu ứng cửa sổ, nếu thanh công cụ chỉ bị ẩn thay vì thu nhỏ để giảm chiều cao cửa sổ, thanh công cụ bị ẩn vẫn sẽ được hiển thị với nền Acrylic/Aero, gây ra một khu vực trống nơi thanh công cụ nằm.

1. #### Dịch Văn Bản Được Chọn
    Dịch văn bản hiện được chọn bởi chuột.

    Ưu tiên sử dụng UIAutomation để trích xuất văn bản. Nếu điều khiển tiêu điểm của cửa sổ hiện tại không hỗ trợ UIAutomationTextPattern, dẫn đến thất bại trong việc trích xuất văn bản, thì sẽ đọc từ clipboard.
1. #### Hiện/Ẩn Cửa Sổ Dịch Thuật
    Không áp dụng.

1. #### Thoát
    Không áp dụng.

== HOOK

>[!WARNING]
>Chỉ khả dụng trong chế độ HOOK

1. #### Chọn Trò Chơi
    Hiển thị cửa sổ chọn tiến trình trò chơi để chọn tiến trình trò chơi cần HOOK.

1. #### Chọn Văn Bản
    Hiển thị cửa sổ chọn văn bản trò chơi để chọn văn bản nào được HOOK để dịch.
    Tuy nhiên, cửa sổ chọn văn bản sẽ tự động hiển thị sau khi chọn tiến trình, và thực sự được sử dụng để thay đổi văn bản đã chọn hoặc sửa đổi một số cài đặt.

== OCR

1. #### Chọn Phạm Vi OCR
    **Chỉ khả dụng trong chế độ OCR**
    
    Trong chế độ OCR, chọn khu vực OCR, hoặc thay đổi khu vực OCR, hoặc khi `Cài Đặt OCR` -> `Khác` -> `Chế Độ Nhiều Khu Vực` được kích hoạt, thêm một khu vực OCR mới.

1. #### Hiện/Ẩn Hộp Phạm Vi
    **Chỉ khả dụng trong chế độ OCR**
    
    Khi không có phạm vi OCR nào được chọn, sử dụng phím tắt này sẽ hiển thị phạm vi OCR và tự động đặt phạm vi OCR thành phạm vi OCR được chọn lần cuối.

1. #### Xóa Phạm Vi OCR
    **Chỉ khả dụng trong chế độ OCR**
    
    Xóa tất cả các phạm vi đã chọn.

1. #### Thực Hiện OCR Một Lần
    Tương tự như `Đọc Clipboard`, bất kể nguồn đầu vào văn bản mặc định hiện tại là gì, nó sẽ đầu tiên chọn phạm vi OCR, sau đó thực hiện OCR một lần, và sau đó tiếp tục với quá trình dịch thuật.
    Thường được sử dụng trong chế độ HOOK, tạm thời sử dụng OCR để dịch các nhánh lựa chọn khi gặp phải, hoặc trong chế độ OCR, tạm thời nhận diện.

1. #### Thực Hiện OCR Lại
    Sau khi sử dụng `Thực Hiện OCR Một Lần`, sử dụng phím tắt này sẽ thực hiện OCR lại tại vị trí ban đầu mà không cần chọn lại khu vực nhận diện.

== Clipboard

1. #### Đọc Clipboard
    Ý nghĩa thực tế là bất kể nguồn đầu vào văn bản mặc định hiện tại là gì, nó đọc văn bản một lần từ clipboard và chuyển nó đến quá trình dịch/TTS/... tiếp theo.

1. #### Sao Chép Vào Clipboard
    Sao chép văn bản hiện được trích xuất vào clipboard một lần. Nếu bạn muốn tự động trích xuất vào clipboard, bạn nên kích hoạt `Đầu Vào Văn Bản` -> `Đầu Ra Văn Bản` -> `Clipboard` -> `Tự Động Đầu Ra`.

1. #### Sao Chép Dịch Thuật Vào Clipboard
    Sao chép bản dịch thay vì văn bản gốc vào clipboard.

== TTS

1. #### Đọc Tự Động
    Chuyển đổi việc đọc to tự động.

1. #### Đọc
    Thực hiện chuyển văn bản thành giọng nói trên văn bản hiện tại.
    Việc đọc này sẽ bỏ qua `Bỏ Qua` (nếu mục tiêu văn bản hiện tại được khớp là `Bỏ Qua` trong `Gán Giọng Nói`, sử dụng phím tắt để đọc sẽ bỏ qua bỏ qua và buộc đọc).

1. #### Ngắt Đọc
    Ngắt việc đọc.

== Game

1. #### Gắn Cửa Sổ (Nhấn Để Hủy)
    Sau khi gắn cửa sổ trò chơi, các tính năng như `Tỷ Lệ Cửa Sổ`, `Chụp Màn Hình Cửa Sổ`, `Tắt Âm Trò Chơi`, `Theo Dõi Cửa Sổ Trò Chơi` -> `Hủy Luôn Trên Cùng Khi Trò Chơi Mất Tiêu Điểm` và `Di Chuyển Đồng Bộ Khi Cửa Sổ Trò Chơi Di Chuyển`, cũng như ghi lại thời gian chơi trò chơi, sẽ khả dụng.
    Phím tắt này khả dụng bất kể chế độ HOOK/OCR/clipboard.
    Trong chế độ HOOK, nó sẽ tự động gắn cửa sổ trò chơi theo trò chơi đã kết nối, nhưng bạn cũng có thể sử dụng phím tắt này để chọn lại một cửa sổ khác.
    Trong chế độ OCR, sau khi gắn cửa sổ, nó cho phép khu vực OCR và hộp phạm vi di chuyển đồng bộ khi cửa sổ trò chơi di chuyển.
    Trong chế độ OCR/clipboard, sau khi gắn cửa sổ, nó cũng có thể được liên kết với cài đặt trò chơi hiện tại trong chế độ HOOK, do đó sử dụng từ điển tối ưu hóa dịch thuật riêng của trò chơi, v.v.

1. #### Chụp Màn Hình Cửa Sổ
    Có thể chụp màn hình cửa sổ đã gắn (mặc định chụp hai ảnh, GDI và Winrt, cả hai đều có thể thất bại). Điểm tốt nhất là nếu Magpie hiện đang được sử dụng để tỷ lệ, nó cũng sẽ chụp màn hình cửa sổ đã tỷ lệ.

1. #### Tắt Âm Trò Chơi
    Sau khi gắn cửa sổ trò chơi (không chỉ trong chế độ HOOK, mà còn trong chế độ OCR hoặc clipboard, miễn là cửa sổ trò chơi được gắn), bạn có thể tắt âm trò chơi chỉ với một lần nhấn, tiết kiệm công việc tắt âm trò chơi trong bộ trộn âm lượng hệ thống.

1. #### Tỷ Lệ Magpie
    Cho phép tỷ lệ toàn màn hình cửa sổ trò chơi chỉ với một lần nhấn bằng cách sử dụng Magpie tích hợp.

1. #### Tỷ Lệ Cửa Sổ Magpie
    Cho phép tỷ lệ cửa sổ trò chơi chỉ với một lần nhấn bằng cách sử dụng Magpie tích hợp.

== Tra Từ Điển

1. #### Truy Xuất và Tra Từ
    Tra từ trong văn bản hiện được chọn bởi chuột.

    Ưu tiên sử dụng UIAutomation để trích xuất văn bản. Nếu điều khiển tiêu điểm của cửa sổ hiện tại không hỗ trợ UIAutomationTextPattern, dẫn đến thất bại trong việc trích xuất văn bản, thì sẽ đọc từ clipboard.
1. #### Tra Từ Trong Cửa Sổ Mới  
    Tra từ trong văn bản hiện được chọn bởi chuột trong một cửa sổ tìm kiếm mới để tránh ghi đè tìm kiếm đang diễn ra.

    Ưu tiên sử dụng UIAutomation để trích xuất văn bản. Nếu điều khiển tiêu điểm của cửa sổ hiện tại không hỗ trợ UIAutomationTextPattern, dẫn đến thất bại trong việc trích xuất văn bản, thì sẽ đọc từ clipboard.
1. #### Tra Từ OCR
    Chọn phạm vi OCR để thực hiện OCR một lần và sau đó tra từ.

1. #### Ghi Âm Anki
    Phím tắt cho chức năng ghi âm trong giao diện thêm Anki trong cửa sổ tra từ điển.

1. #### Ghi Âm Câu Ví Dụ Anki
    Phím tắt cho chức năng ghi âm trong giao diện thêm Anki trong cửa sổ tra từ điển, nhưng phím tắt này đặt âm thanh ghi âm vào trường câu ví dụ.

1. #### Thêm Vào Anki
    Thêm từ vào Anki.

1. #### Đọc Từ
    Đọc từ trong cửa sổ tra từ điển hiện tại.

== Tùy Chỉnh

Bạn có thể thêm nhiều phím tắt tùy ý bằng cách tự triển khai hàm `OnHotKeyClicked`, hàm này sẽ được gọi khi phím tắt được kích hoạt.

:::
