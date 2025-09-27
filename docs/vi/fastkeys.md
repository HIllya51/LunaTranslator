# Phím Tắt
::: tip
 Để sử dụng phím tắt, trước tiên bạn cần kích hoạt `Sử dụng phím tắt`, sau đó kích hoạt phím tắt cụ thể mà bạn muốn sử dụng và thiết lập tổ hợp phím của nó.
:::

## Chung

1. #### Dịch thủ công {#anchor-_1}
    Đọc đầu vào một lần từ nguồn đầu vào văn bản hiện tại và thực hiện dịch.
    Ví dụ: nếu chế độ hiện tại là OCR, nó sẽ thực hiện OCR lại.

1. #### Dịch tự động {#anchor-_2}
    Tạm dừng/tiếp tục đọc văn bản tự động từ nguồn đầu vào văn bản hiện tại.
    Ví dụ: nếu chế độ hiện tại là HOOK, nó sẽ tạm dừng đọc văn bản trò chơi; nếu chế độ hiện tại là OCR, nó sẽ tạm dừng nhận diện hình ảnh tự động; nếu chế độ hiện tại là clipboard, nó sẽ tạm dừng đọc tự động từ clipboard.

1. #### Mở Cài đặt {#anchor-_3}
    Không áp dụng.

1. #### Hiển thị/ẩn văn bản gốc {#anchor-_5}
    Chuyển đổi việc hiển thị văn bản gốc, có hiệu lực ngay lập tức.

1. #### Hiện/ẩn bản dịch {#anchor-_51}
    Chuyển đổi việc sử dụng dịch thuật, đây là công tắc chính cho dịch thuật. Tắt nó sẽ dừng mọi dịch thuật.
    Nếu dịch thuật đã được thực hiện, tắt nó sẽ ẩn kết quả dịch, và bật lại sẽ hiển thị lại kết quả dịch hiện tại.
    Nếu chưa có dịch thuật nào được thực hiện và nó được chuyển từ ẩn sang hiển thị, nó sẽ kích hoạt dịch thuật cho câu hiện tại.

1. #### Hiển thị / ẩn văn bản lịch sử {#anchor-_6}
    Mở hoặc đóng cửa sổ văn bản lịch sử.  

1. #### Chuột xuyên qua cửa sổ {#anchor-_8}
    Chuyển đổi trạng thái cửa sổ xuyên chuột.
    Tính năng này phải được sử dụng cùng với nút công cụ cửa sổ xuyên chuột để hoạt động chính xác.

1. #### Khóa thanh công cụ {#anchor-_9}
    Khi thanh công cụ không bị khóa, nó sẽ tự động ẩn khi chuột di chuyển ra ngoài; kích hoạt tính năng này sẽ giữ thanh công cụ luôn hiển thị.
    Khi thanh công cụ không bị khóa và `Cửa Sổ Xuyên Chuột` được kích hoạt, thanh công cụ sẽ chỉ hiển thị khi chuột di chuyển đến **nút Cửa Sổ Xuyên Chuột và khu vực bên trái và phải của nó**; nếu không, nó sẽ hiển thị ngay khi chuột vào cửa sổ dịch thuật.
    Nếu sử dụng hiệu ứng cửa sổ (Aero/Acrylic) và thanh công cụ không bị khóa, thanh công cụ sẽ nằm trong khu vực trục z phía trên khu vực văn bản, không phải trên trục y phía trên khu vực văn bản. Điều này là do, với Windows, khi sử dụng hiệu ứng cửa sổ, nếu thanh công cụ chỉ bị ẩn thay vì thu nhỏ để giảm chiều cao cửa sổ, thanh công cụ bị ẩn vẫn sẽ được hiển thị với nền Acrylic/Aero, gây ra một khu vực trống nơi thanh công cụ nằm.

1. #### Dịch thuật lấy từ {#anchor-38}
    Dịch văn bản hiện được chọn bởi chuột.

    Ưu tiên sử dụng UIAutomation để trích xuất văn bản. Nếu điều khiển tiêu điểm của cửa sổ hiện tại không hỗ trợ UIAutomationTextPattern, dẫn đến thất bại trong việc trích xuất văn bản, thì sẽ đọc từ clipboard.
1. #### Hiện/ẩn cửa sổ dịch {#anchor-_16}
    Không áp dụng.

1. #### Thoát {#anchor-_17}
    Không áp dụng.

1. #### Trình nhấp chuột tự động {#anchor-44}
    Không áp dụng.

1. #### Thiết lập lại trạng thái dịch thuật. {#anchor-45}
    Đặt lại trạng thái dịch, chủ yếu nhằm đáp ứng nhu cầu dịch bằng mô hình lớn ngày càng tăng, có thể xóa ngữ cảnh đã lưu và các thông tin khác.
    
1. #### Lưu cấu hình ngay lập tức {#anchor-50}
    Lưu ngay cấu hình người dùng hiện tại thay vì đợi đến khi thoát.

## HOOK

>[!WARNING]
>Chỉ khả dụng trong chế độ HOOK

1. #### Chọn trò chơi {#anchor-_11}
    Hiển thị cửa sổ chọn tiến trình trò chơi để chọn tiến trình trò chơi cần HOOK.

1. #### Chọn văn bản {#anchor-_12}
    Hiển thị cửa sổ chọn văn bản trò chơi để chọn văn bản nào được HOOK để dịch.
    Tuy nhiên, cửa sổ chọn văn bản sẽ tự động hiển thị sau khi chọn tiến trình, và thực sự được sử dụng để thay đổi văn bản đã chọn hoặc sửa đổi một số cài đặt.

## OCR

1. #### Chọn dải OCR {#anchor-_13}
    **Chỉ khả dụng trong chế độ OCR**
    
    Trong chế độ OCR, chọn khu vực OCR, hoặc thay đổi khu vực OCR, hoặc khi `Cài Đặt OCR` -> `Khác` -> `Chế Độ Nhiều Khu Vực` được kích hoạt, thêm một khu vực OCR mới.

1. #### Hiển thị/Ẩn hộp phạm vi {#anchor-_14}
    **Chỉ khả dụng trong chế độ OCR**
    
    Khi không có phạm vi OCR nào được chọn, sử dụng phím tắt này sẽ hiển thị phạm vi OCR và tự động đặt phạm vi OCR thành phạm vi OCR được chọn lần cuối.

1. #### Xóa dải OCR {#anchor-_14_1}
    **Chỉ khả dụng trong chế độ OCR**
    
    Xóa tất cả các phạm vi đã chọn.

1. #### Thực hiện OCR {#anchor-_26}
    Tương tự như `Đọc Clipboard`, bất kể nguồn đầu vào văn bản mặc định hiện tại là gì, nó sẽ đầu tiên chọn phạm vi OCR, sau đó thực hiện OCR một lần, và sau đó tiếp tục với quá trình dịch thuật.
    Thường được sử dụng trong chế độ HOOK, tạm thời sử dụng OCR để dịch các nhánh lựa chọn khi gặp phải, hoặc trong chế độ OCR, tạm thời nhận diện.

1. #### OCR lần nữa {#anchor-_26_1}
    Sau khi sử dụng `Thực Hiện OCR Một Lần`, sử dụng phím tắt này sẽ thực hiện OCR lại tại vị trí ban đầu mà không cần chọn lại khu vực nhận diện.

1. #### Chế độ đa vùng Chuyển sang khu vực trước đó {#anchor-46}
    **Chỉ khả dụng trong chế độ OCR**

    Sau khi kích hoạt chế độ đa vùng, bạn có thể sử dụng phím tắt này để chuyển vùng đang được tập trung sang vùng trước đó và ngay lập tức thực hiện lại OCR.

1. #### Chế độ đa vùng Chuyển sang khu vực tiếp theo {#anchor-47}
    **Chỉ khả dụng trong chế độ OCR**

    Sau khi kích hoạt chế độ đa vùng, bạn có thể sử dụng phím tắt này để chuyển vùng đang được tập trung sang vùng tiếp theo và ngay lập tức thực hiện lại OCR.

1. #### Chế độ đa vùng Chuyển sang khu vực gần chuột {#anchor-48}
    **Chỉ khả dụng trong chế độ OCR**

    Sau khi kích hoạt chế độ đa vùng, bạn có thể sử dụng phím tắt này để chuyển vùng đang được tập trung sang vùng gần con trỏ chuột và ngay lập tức thực hiện lại OCR.

1. #### Chế độ đa vùng Hủy tập trung khu vực {#anchor-49}
    **Chỉ khả dụng trong chế độ OCR**

    Sau khi kích hoạt chế độ đa vùng, bạn có thể sử dụng phím tắt này để hủy tập trung vùng.

## Clipboard

1. #### Đọc bảng nháp {#anchor-36}
    Ý nghĩa thực tế là bất kể nguồn đầu vào văn bản mặc định hiện tại là gì, nó đọc văn bản một lần từ clipboard và chuyển nó đến quá trình dịch/TTS/... tiếp theo.

1. #### Sao chép vào bảng nháp {#anchor-_4}
    Sao chép văn bản hiện được trích xuất vào clipboard một lần. Nếu muốn tự động trích xuất vào clipboard, bật `Nhập văn bản` → `Clipboard` → `Tự động xuất` → `Tự động xuất văn bản`.

1. #### Sao chép vào bảng nháp Dịch {#anchor-_28}
    Sao chép bản dịch thay vì văn bản gốc vào clipboard.

## TTS

1. #### Tự động đọc {#anchor-_32}
    Chuyển đổi việc đọc to tự động.

1. #### Đọc to {#anchor-_7}
    Thực hiện chuyển văn bản thành giọng nói trên văn bản hiện tại.
    Việc đọc này sẽ bỏ qua `Bỏ Qua` (nếu mục tiêu văn bản hiện tại được khớp là `Bỏ Qua` trong `Gán Giọng Nói`, sử dụng phím tắt để đọc sẽ bỏ qua bỏ qua và buộc đọc).

1. #### Đọc to Ngắt {#anchor-_7_1}
    Ngắt việc đọc.

## Game

1. #### Quản lý trò chơi {#anchor-_10}
    Không áp dụng.

1. #### Cửa sổ bị ràng buộc (Click vào tự hủy) {#anchor-_15}
    Sau khi gắn cửa sổ trò chơi, các tính năng như `Tỷ Lệ Cửa Sổ`, `Chụp Màn Hình Cửa Sổ`, `Tắt Âm Trò Chơi`, `Theo Dõi Cửa Sổ Trò Chơi` -> `Hủy Luôn Trên Cùng Khi Trò Chơi Mất Tiêu Điểm` và `Di Chuyển Đồng Bộ Khi Cửa Sổ Trò Chơi Di Chuyển`, cũng như ghi lại thời gian chơi trò chơi, sẽ khả dụng.
    Phím tắt này khả dụng bất kể chế độ HOOK/OCR/clipboard.
    Trong chế độ HOOK, nó sẽ tự động gắn cửa sổ trò chơi theo trò chơi đã kết nối, nhưng bạn cũng có thể sử dụng phím tắt này để chọn lại một cửa sổ khác.
    Trong chế độ OCR, sau khi gắn cửa sổ, nó cho phép khu vực OCR và hộp phạm vi di chuyển đồng bộ khi cửa sổ trò chơi di chuyển.
    Trong chế độ OCR/clipboard, sau khi gắn cửa sổ, nó cũng có thể được liên kết với cài đặt trò chơi hiện tại trong chế độ HOOK, do đó sử dụng từ điển tối ưu hóa dịch thuật riêng của trò chơi, v.v.

1. #### Ảnh chụp cửa sổ {#anchor-_21}
    Sau khi liên kết cửa sổ game, bạn có thể chụp ảnh cửa sổ đã liên kết (mặc định sẽ chụp hai ảnh: GDI và Winrt, cả hai đều có thể thất bại). Nếu đang sử dụng Magpie để phóng to, nó cũng sẽ chụp ảnh cửa sổ đã phóng to.

1. #### Im lặng trò chơi {#anchor-_22}
    Sau khi liên kết cửa sổ game, bạn có thể tắt tiếng game bằng một cú nhấp chuột, tiết kiệm thời gian so với việc tắt tiếng trong bộ trộn âm lượng hệ thống.

1. #### Tạm dừng trò chơi {#anchor-43}
    Sau khi liên kết cửa sổ game, bạn có thể tạm dừng hoặc tiếp tục quá trình game bằng một cú nhấp chuột.

1. #### Magpie Phóng to {#anchor-41}
    Sau khi liên kết cửa sổ game, bạn có thể sử dụng Magpie tích hợp để phóng to cửa sổ game toàn màn hình bằng một cú nhấp chuột.

1. #### Magpie Thu phóng cửa sổ {#anchor-42}
    Sau khi liên kết cửa sổ game, bạn có thể sử dụng Magpie tích hợp để phóng to cửa sổ game dạng cửa sổ bằng một cú nhấp chuột.

## Tra Từ Điển

1. #### Tìm kiếm từ {#anchor-37}
    Tra từ trong văn bản hiện được chọn bởi chuột.

    Ưu tiên sử dụng UIAutomation để trích xuất văn bản. Nếu điều khiển tiêu điểm của cửa sổ hiện tại không hỗ trợ UIAutomationTextPattern, dẫn đến thất bại trong việc trích xuất văn bản, thì sẽ đọc từ clipboard.
1. #### Tìm kiếm từ Trong cửa sổ mới {#anchor-40}
    Tra từ trong văn bản hiện được chọn bởi chuột trong một cửa sổ tìm kiếm mới để tránh ghi đè tìm kiếm đang diễn ra.

    Ưu tiên sử dụng UIAutomation để trích xuất văn bản. Nếu điều khiển tiêu điểm của cửa sổ hiện tại không hỗ trợ UIAutomationTextPattern, dẫn đến thất bại trong việc trích xuất văn bản, thì sẽ đọc từ clipboard.
1. #### OCR Tra từ {#anchor-39}
    Chọn phạm vi OCR để thực hiện OCR một lần và sau đó tra từ.

1. #### Anki Ghi âm {#anchor-_29}
    Phím tắt cho chức năng ghi âm trong giao diện thêm Anki trong cửa sổ tra từ điển.

1. #### Anki Ghi âm Câu ví dụ {#anchor-_30}
    Phím tắt cho chức năng ghi âm trong giao diện thêm Anki trong cửa sổ tra từ điển, nhưng phím tắt này đặt âm thanh ghi âm vào trường câu ví dụ.

1. #### Anki Thêm {#anchor-_35}
    Thêm từ vào Anki.

1. #### Đọc to Từ {#anchor-_33}
    Đọc từ trong cửa sổ tra từ điển hiện tại.

## Tùy Chỉnh

Bạn có thể thêm nhiều phím tắt tùy ý bằng cách tự triển khai hàm `OnHotKeyClicked`, hàm này sẽ được gọi khi phím tắt được kích hoạt.