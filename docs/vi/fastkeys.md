# Phím tắt

::: tip
 Để sử dụng phím tắt, trước tiên bạn cần kích hoạt `Sử dụng phím tắt`, sau đó kích hoạt phím tắt cụ thể bạn muốn sử dụng và thiết lập tổ hợp phím của nó.
:::

::: tabs

== Chung

1. #### Dịch thủ công
    Đọc đầu vào một lần từ nguồn đầu vào văn bản hiện tại và thực hiện dịch thuật.
    Ví dụ, nếu chế độ hiện tại là OCR, nó sẽ thực hiện OCR lại.

1. #### Dịch tự động
    Tạm dừng/tiếp tục tự động đọc văn bản từ nguồn đầu vào văn bản hiện tại.
    Ví dụ, nếu chế độ hiện tại là HOOK, nó sẽ tạm dừng đọc văn bản trò chơi; nếu chế độ hiện tại là OCR, nó sẽ tạm dừng nhận dạng hình ảnh tự động; nếu chế độ hiện tại là clipboard, nó sẽ tạm dừng đọc tự động từ clipboard.

1. #### Mở cài đặt
    Không áp dụng

1. #### Hiển thị/Ẩn văn bản gốc
    Chuyển đổi hiển thị văn bản gốc, có hiệu lực ngay lập tức.

1. #### Hiển thị/Ẩn dịch thuật
    Chuyển đổi việc sử dụng dịch thuật, đây là công tắc chính cho dịch thuật. Tắt nó sẽ dừng mọi dịch thuật.
    Nếu dịch thuật đã được thực hiện, tắt nó sẽ ẩn kết quả dịch, và bật lại sẽ hiển thị lại kết quả dịch hiện tại.
    Nếu không có dịch thuật nào được thực hiện và nó được chuyển từ ẩn sang hiển thị, nó sẽ kích hoạt dịch thuật cho câu hiện tại.

1. #### Hiển thị/Ẩn văn bản lịch sử  
    Mở hoặc đóng cửa sổ văn bản lịch sử.  

1. #### Cửa sổ xuyên chuột
    Chuyển đổi trạng thái của cửa sổ xuyên chuột.
    Tính năng này phải được sử dụng kết hợp với nút công cụ cửa sổ xuyên chuột để hoạt động chính xác.

1. #### Khóa thanh công cụ
    Khi thanh công cụ không bị khóa, nó sẽ tự động ẩn khi chuột di chuyển ra ngoài; kích hoạt điều này sẽ giữ thanh công cụ luôn hiển thị.
    Khi thanh công cụ không bị khóa và `Cửa sổ xuyên chuột` được kích hoạt, thanh công cụ sẽ chỉ hiển thị khi chuột di chuyển đến **nút Cửa sổ xuyên chuột và khu vực bên trái và phải của nó**; nếu không, nó sẽ hiển thị ngay khi chuột vào cửa sổ dịch.
    Nếu hiệu ứng cửa sổ (Aero/Arylic) được sử dụng và thanh công cụ không bị khóa, thanh công cụ sẽ nằm trong khu vực trục z phía trên vùng văn bản, không phải trên trục y phía trên vùng văn bản. Điều này là do Windows, khi sử dụng hiệu ứng cửa sổ, nếu thanh công cụ chỉ bị ẩn thay vì thu nhỏ để giảm chiều cao cửa sổ, thanh công cụ bị ẩn vẫn sẽ được hiển thị với nền Acrylic/Aero, gây ra khu vực trống ở vị trí thanh công cụ.

1. #### Dịch văn bản được chọn
    Dịch văn bản hiện đang được chọn bởi chuột

    Ưu tiên sử dụng UIAutomation để trích xuất văn bản. Nếu điều khiển tiêu điểm của cửa sổ hiện tại không hỗ trợ UIAutomationTextPattern, dẫn đến việc trích xuất văn bản thất bại, thì sẽ đọc từ clipboard.
1. #### Hiển thị/Ẩn cửa sổ dịch
    Không áp dụng

1. #### Thoát
    Không áp dụng

== HOOK

>[!WARNING]
>Chỉ khả dụng trong chế độ HOOK

1. #### Chọn trò chơi
    Hiển thị cửa sổ chọn quy trình trò chơi để chọn quy trình trò chơi để HOOK.

1. #### Chọn văn bản
    Hiển thị cửa sổ chọn văn bản trò chơi để chọn văn bản HOOKed nào để dịch.
    Tuy nhiên, cửa sổ chọn văn bản sẽ tự động hiện lên sau khi chọn quy trình, và thực tế được sử dụng để thay đổi văn bản đã chọn hoặc sửa đổi một số cài đặt.

== OCR

1. #### Chọn phạm vi OCR
    **Chỉ khả dụng trong chế độ OCR**
    
    Trong chế độ OCR, chọn vùng OCR, hoặc thay đổi vùng OCR, hoặc khi kích hoạt `Cài đặt OCR` -> `Khác` -> `Chế độ nhiều vùng`, thêm vùng OCR mới.

1. #### Hiển thị/Ẩn hộp phạm vi
    **Chỉ khả dụng trong chế độ OCR**
    
    Khi không có phạm vi OCR nào được chọn, sử dụng phím tắt này sẽ hiển thị phạm vi OCR và tự động đặt phạm vi OCR thành OCR được chọn cuối cùng.

1. ###### Xóa phạm vi OCR
    **Chỉ khả dụng trong chế độ OCR**
    
    Xóa tất cả các phạm vi đã chọn

1. #### Thực hiện OCR một lần
    Tương tự như `Đọc Clipboard`, bất kể nguồn đầu vào văn bản mặc định hiện tại, nó sẽ chọn phạm vi OCR trước, sau đó thực hiện OCR một lần, và sau đó tiến hành quá trình dịch.
    Thường được sử dụng trong chế độ HOOK, để tạm thời sử dụng OCR để dịch các nhánh lựa chọn khi gặp phải, hoặc trong chế độ OCR, để tạm thời nhận dạng một vị trí mới thỉnh thoảng xuất hiện.

1. #### Thực hiện OCR lại
    Sau khi sử dụng `Thực hiện OCR một lần`, sử dụng phím tắt này sẽ thực hiện OCR lại ở vị trí ban đầu mà không cần chọn lại vùng nhận dạng.

== Clipboard

1. #### Đọc Clipboard
    Ý nghĩa thực tế là bất kể nguồn đầu vào văn bản mặc định hiện tại, nó đọc văn bản một lần từ clipboard và truyền nó đến quá trình dịch/TTS/... tiếp theo.

1. #### Sao chép vào Clipboard
    Sao chép văn bản hiện đang được trích xuất vào clipboard một lần. Nếu bạn muốn tự động trích xuất vào clipboard, bạn nên kích hoạt `Đầu vào văn bản` -> `Đầu ra văn bản` -> `Clipboard` -> `Đầu ra tự động`.

1. #### Sao chép bản dịch vào Clipboard
    Sao chép bản dịch thay vì văn bản gốc vào clipboard.

== TTS

1. #### Tự động đọc
    Chuyển đổi tự động đọc to.

1. #### Đọc
    Thực hiện chuyển văn bản thành giọng nói trên văn bản hiện tại.
    Việc đọc này sẽ bỏ qua `Bỏ qua` (nếu mục tiêu văn bản hiện tại được khớp là `Bỏ qua` trong `Gán giọng nói`, sử dụng phím tắt để đọc sẽ bỏ qua việc bỏ qua và buộc đọc).

1. #### Ngắt đọc
    Ngắt quá trình đọc.

== Trò chơi

1. #### Liên kết cửa sổ (Nhấp để hủy)
    Sau khi liên kết cửa sổ trò chơi, `Tỷ lệ cửa sổ`, `Chụp màn hình cửa sổ`, `Tắt tiếng trò chơi`, `Theo dõi cửa sổ trò chơi` -> `Hủy luôn trên cùng khi trò chơi mất tiêu điểm` và `Di chuyển đồng bộ khi cửa sổ trò chơi di chuyển`, cũng như ghi lại thời gian trò chơi, trở nên khả dụng.
    Phím tắt này khả dụng bất kể chế độ HOOK/OCR/clipboard.
    Trong chế độ HOOK, nó sẽ tự động liên kết cửa sổ trò chơi theo trò chơi đã kết nối, nhưng bạn cũng có thể sử dụng phím tắt này để chọn lại cửa sổ khác.
    Trong chế độ OCR, sau khi liên kết cửa sổ, nó còn cho phép vùng OCR và hộp phạm vi di chuyển đồng bộ khi cửa sổ trò chơi di chuyển.
    Trong chế độ OCR/clipboard, sau khi liên kết cửa sổ, nó cũng có thể được liên kết với cài đặt trò chơi hiện tại trong chế độ HOOK, do đó sử dụng từ điển tối ưu hóa dịch riêng của trò chơi, v.v.

1. #### Chụp màn hình cửa sổ
    Có thể chụp màn hình của cửa sổ đã liên kết (mặc định chụp hai ảnh chụp màn hình, GDI và Winrt, cả hai đều có thể thất bại). Phần tốt nhất là nếu Magpie đang được sử dụng để thay đổi tỷ lệ, nó cũng sẽ chụp màn hình của cửa sổ đã được phóng to.

1. #### Tắt tiếng trò chơi
    Sau khi liên kết cửa sổ trò chơi (không chỉ trong chế độ HOOK, mà còn trong chế độ OCR hoặc clipboard, miễn là cửa sổ trò chơi được liên kết), bạn có thể tắt tiếng trò chơi với một cú nhấp, tiết kiệm rắc rối khi tắt tiếng trò chơi trong bộ trộn âm lượng hệ thống.

1. #### Tỷ lệ Magpie
    Cho phép tỷ lệ toàn màn hình cửa sổ trò chơi với một cú nhấp bằng cách sử dụng Magpie tích hợp.

1. #### Tỷ lệ cửa sổ Magpie
    Cho phép tỷ lệ cửa sổ của cửa sổ trò chơi với một cú nhấp bằng cách sử dụng Magpie tích hợp.

1. #### Lớp phủ trong trò chơi Magpie
    Cho phép Magpie tích hợp hiển thị/ẩn lớp phủ trong trò chơi.

== Tra cứu từ điển

1. #### Trích xuất và tìm kiếm từ
    Tìm kiếm từ trong văn bản hiện đang được chọn bằng chuột

    Ưu tiên sử dụng UIAutomation để trích xuất văn bản. Nếu điều khiển tiêu điểm của cửa sổ hiện tại không hỗ trợ UIAutomationTextPattern, dẫn đến việc trích xuất văn bản thất bại, thì đọc từ clipboard.
1. #### Tra cứu từ trong cửa sổ mới  
    Tra cứu văn bản hiện đang được chọn bằng chuột trong một cửa sổ tìm kiếm mới để tránh ghi đè lên tìm kiếm đang diễn ra.

    Ưu tiên sử dụng UIAutomation để trích xuất văn bản. Nếu điều khiển tiêu điểm của cửa sổ hiện tại không hỗ trợ UIAutomationTextPattern, dẫn đến việc trích xuất văn bản thất bại, thì đọc từ clipboard.
1. #### Tìm kiếm từ OCR
    Chọn phạm vi OCR để thực hiện một lần OCR và sau đó tìm kiếm từ

1. #### Ghi âm Anki
    Phím tắt cho chức năng ghi âm trong giao diện thêm Anki trong cửa sổ tra cứu từ điển.

1. #### Ghi âm câu ví dụ Anki
    Phím tắt cho chức năng ghi âm trong giao diện thêm Anki trong cửa sổ tra cứu từ điển, nhưng phím tắt này đặt âm thanh đã ghi vào trường câu ví dụ.

1. #### Thêm vào Anki
    Thêm từ vào Anki.

1. #### Đọc từ
    Đọc từ trong cửa sổ tra cứu từ điển hiện tại.

== Tùy chỉnh

Bạn có thể thêm nhiều phím tắt tùy ý hơn bằng cách tự triển khai hàm `OnHotKeyClicked`, hàm này sẽ được gọi khi phím tắt được kích hoạt.

:::