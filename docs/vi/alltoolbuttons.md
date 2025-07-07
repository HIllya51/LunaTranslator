# Các nút công cụ

::: info
 Tất cả các nút có thể được ẩn hoặc hiển thị trong `Cài đặt hiển thị` -> `Nút công cụ`.

Tất cả các nút có thể được điều chỉnh vị trí tự do. Các nút có thể được đặt vào các nhóm căn chỉnh `Trái` `Giữa` `Phải`, và việc điều chỉnh vị trí tương đối sẽ bị giới hạn trong nhóm căn chỉnh.

Màu sắc của các nút có thể được tùy chỉnh trong `Cài đặt hiển thị` -> `Cài đặt giao diện` -> `Thanh công cụ` -> `Màu nút`.

Một số nút có hai biểu tượng để biểu thị hai trạng thái khác nhau. Một số nút chỉ có một biểu tượng, nhưng chúng sử dụng các màu khác nhau để biểu thị các trạng thái khác nhau.
:::

<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.6.0/css/all.min.css"> 

<style>
    i{
        color:blue;
        width:20px;
    }
    .fa-icon {
  visibility: hidden;
}
.btnstatus2{
    color:deeppink;
}
</style>

1. #### <i class="fa fa-rotate-right"></i> <i class="fa fa-icon fa-rotate-right"></i> Dịch thủ công {#anchor-retrans}
    Ý nghĩa thực tế là đọc đầu vào một lần từ nguồn đầu vào văn bản hiện tại và thực hiện dịch thuật.
    
    Ví dụ, nếu chế độ hiện tại là OCR, nó sẽ thực hiện OCR lại.

1. #### <i class="fa fa-forward"></i> <i class="btnstatus2 fa fa-forward"></i> Dịch tự động {#anchor-automodebutton}
    Ý nghĩa thực tế là tạm dừng/tiếp tục tự động đọc văn bản từ nguồn đầu vào văn bản hiện tại.

    Ví dụ, nếu chế độ hiện tại là HOOK, nó sẽ tạm dừng đọc văn bản trò chơi; nếu chế độ hiện tại là OCR, nó sẽ tạm dừng nhận diện hình ảnh tự động; nếu chế độ hiện tại là chế độ clipboard, nó sẽ tạm dừng đọc tự động từ clipboard.

1. #### <i class="fa fa-gear"></i> <i class="fa fa-icon fa-rotate-right"></i> Mở Cài đặt {#anchor-setting}
    N/A
1. #### <i class="fa fa-file"></i> <i class="fa fa-icon fa-rotate-right"></i> Đọc bảng nháp {#anchor-copy_once}
    Ý nghĩa thực tế là đọc văn bản một lần từ clipboard bất kể nguồn đầu vào văn bản mặc định hiện tại và chuyển nó đến quá trình dịch/tts/... tiếp theo

    Nhấp chuột phải vào nút sẽ thêm văn bản đã đọc vào văn bản hiện tại.
1. #### <i class="fa fa-futbol"></i> <i class="fa fa-icon fa-rotate-right"></i> Cài đặt trò chơi {#anchor-open_game_setting}
    Khi sử dụng chế độ HOOK để kết nối với trò chơi, hoặc sử dụng chế độ OCR để liên kết cửa sổ trò chơi, bạn có thể trực tiếp mở cửa sổ cài đặt trò chơi hiện tại thông qua nút này
1. #### <i class="fa fa-mouse-pointer"></i> <i class="btnstatus2 fa fa-mouse-pointer"></i> Chuột xuyên qua cửa sổ {#anchor-mousetransbutton}
    Sau khi kích hoạt nút này, cửa sổ dịch sẽ không phản hồi các lần nhấp chuột, nhưng sẽ chuyển sự kiện nhấp chuột đến cửa sổ bên dưới.

    Khi đặt cửa sổ dịch lên trên hộp văn bản của cửa sổ trò chơi và kích hoạt nút này, bạn có thể trực tiếp nhấp vào hộp văn bản của trò chơi thay vì cửa sổ dịch.

    Khi chuột di chuyển đến **khu vực của nút Cửa sổ xuyên chuột và một nút bên trái và phải**, nó sẽ tự động thoát ra để sử dụng các nút công cụ; nó sẽ tự động khôi phục xuyên qua khi di chuyển ra khỏi khu vực.

1. #### <i class="fa fa-lightbulb"></i> <i class="btnstatus2 fa fa-lightbulb"></i> Trong suốt cửa sổ nền {#anchor-backtransbutton}
    Chức năng của nút này là chuyển độ mờ của cửa sổ dịch sang 0 chỉ với một lần nhấp. Công tắc này sẽ không làm quên các cài đặt độ mờ ban đầu.
    
1. #### <i class="fa fa-lock"></i> <i class="btnstatus2 fa fa-unlock"></i> Khóa thanh công cụ {#anchor-locktoolsbutton}
    Sau khi kích hoạt, thanh công cụ sẽ luôn được hiển thị.

    Khi thanh công cụ không bị khóa, nó sẽ tự động ẩn khi chuột di chuyển ra xa, và nó sẽ xuất hiện lại khi chuột vào cửa sổ. Nếu khóa thanh công cụ bị hủy bằng cách sử dụng nút chuột phải, thanh công cụ sẽ chỉ xuất hiện lại khi chuột vào **khu vực của nút khóa thanh công cụ và các nút liền kề ở hai bên**.

    Khi thanh công cụ không bị khóa, nếu `Cửa sổ xuyên chuột` được kích hoạt, thanh công cụ sẽ chỉ được hiển thị khi chuột di chuyển đến **khu vực của nút Cửa sổ xuyên chuột và một nút bên trái và phải**; nếu không, miễn là chuột vào cửa sổ dịch, thanh công cụ sẽ được hiển thị.

    Nếu hiệu ứng cửa sổ (Aero/Arylic) hiện đang được sử dụng và thanh công cụ không bị khóa, thanh công cụ sẽ nằm trong khu vực phía trên khu vực văn bản trên trục z, không phải trên trục y phía trên khu vực văn bản. Điều này là do Windows, khi sử dụng hiệu ứng cửa sổ, nếu thanh công cụ chỉ bị ẩn thay vì giảm chiều cao cửa sổ của nó, thanh công cụ bị ẩn vẫn sẽ được hiển thị với nền acrylic/Aero, dẫn đến một khu vực trống nơi thanh công cụ được đặt.
1. #### <i class="fa fa-link"></i> <i class="fa fa-icon fa-rotate-right"></i> Chọn trò chơi {#anchor-selectgame}
    **Nút này chỉ có sẵn trong chế độ HOOK**

    Nhấp vào nút sẽ hiển thị cửa sổ chọn quy trình trò chơi để chọn quy trình trò chơi để HOOK.
1. #### <i class="fa fa-tasks"></i> <i class="fa fa-icon fa-rotate-right"></i> Chọn văn bản {#anchor-selecttext}
    **Nút này chỉ có sẵn trong chế độ HOOK**

    Nhấp vào nút sẽ hiển thị cửa sổ chọn văn bản trò chơi để chọn văn bản nào để dịch mà đã được HOOK.

    Tuy nhiên, cửa sổ chọn văn bản sẽ tự động hiển thị sau khi chọn quy trình, và nút này thực sự được sử dụng để thay thế văn bản đã chọn hoặc chỉnh sửa một số cài đặt.
1. #### <i class="fa fa-crop"></i> <i class="fa fa-icon fa-rotate-right"></i> Chọn dải OCR {#anchor-selectocrrange}
    **Nút này chỉ có sẵn trong chế độ OCR**

    Trong chế độ OCR, chọn khu vực OCR, hoặc thay đổi khu vực OCR, hoặc khi kích hoạt `Cài đặt OCR` -> `Khác` -> `Chế độ nhiều khu vực`, thêm một khu vực OCR mới

    Khi nhấn nút phải, tất cả các phạm vi đã chọn sẽ bị xóa trước khi thêm các khu vực mới.
1. #### <i class="fa fa-square"></i> <i class="fa fa-icon fa-rotate-right"></i> Hiển thị/Ẩn hộp phạm vi {#anchor-hideocrrange}
    **Nút này chỉ có sẵn trong chế độ OCR**

    Khi không có phạm vi OCR nào được chọn, sử dụng nút này để hiển thị phạm vi OCR, nó sẽ tự động đặt phạm vi OCR thành OCR cuối cùng đã chọn.

    Khi nhấn nút phải, tất cả các phạm vi đã chọn sẽ bị xóa
1. #### <i class="fa fa-crop"></i> <i class="fa fa-icon fa-rotate-right"></i> Thực hiện OCR {#anchor-ocr_once}
    Nút này tương tự như `Đọc Clipboard`, bất kể nguồn đầu vào văn bản mặc định hiện tại, nó sẽ đầu tiên chọn phạm vi OCR, sau đó thực hiện OCR một lần, và sau đó tiếp tục với quá trình dịch.

    Nút này thường được sử dụng trong chế độ HOOK, khi gặp các lựa chọn, để tạm thời sử dụng OCR để dịch các lựa chọn. Hoặc trong chế độ OCR, để tạm thời nhận diện một vị trí mới thỉnh thoảng xuất hiện.

1. #### <i class="fa fa-spinner"></i> <i class="fa fa-icon fa-rotate-right"></i> OCR lần nữa {#anchor-ocr_once_follow}
    Sau khi sử dụng `Thực hiện OCR một lần`, sử dụng nút này để thực hiện OCR lại tại vị trí ban đầu mà không cần phải chọn lại khu vực nhận diện.
    
1. #### <i class="fa fa-book"></i> <i class="fa fa-icon fa-rotate-right"></i> Bản dịch của proprietary noun Thay thế trước bản dịch {#anchor-noundict_direct}
1. #### <i class="fa fa-book"></i> <i class="fa fa-icon fa-rotate-right"></i> Bản dịch của proprietary noun {#anchor-noundict}
1. #### <i class="fa fa-won"></i> <i class="fa fa-icon fa-rotate-right"></i> Sửa kết quả dịch {#anchor-fix}
    Ba nút trên có tác dụng tương tự và được sử dụng để nhanh chóng mở cửa sổ cài đặt tối ưu hóa dịch thuật để thêm các thuật ngữ mới được chỉ định.

    Khi nhấp chuột trái, nếu có một trò chơi được liên kết (trò chơi được liên kết HOOK/clipboard, cửa sổ OCR được liên kết), nó sẽ mở cài đặt từ điển dành riêng cho trò chơi. Nếu không, nó sẽ mở cài đặt từ điển toàn cầu.

    Khi nhấp chuột phải, nó luôn mở cài đặt từ điển toàn cầu.
1. #### <i class="fa fa-minus"></i> <i class="fa fa-icon fa-rotate-right"></i> Thu nhỏ vào khay {#anchor-minmize}
    N/A
1. #### <i class="fa fa-times"></i> <i class="fa fa-icon fa-rotate-right"></i> Thoát {#anchor-quit}
    N/A
1. #### <i class="fa fa-hand-paper"></i> <i class="fa fa-icon fa-rotate-right"></i> Di chuyển {#anchor-move}
    Kéo cửa sổ dịch.

    Thực tế, khi không có nút nào trên thanh nút, có thêm khu vực trống, bạn có thể kéo nó tùy ý. Nút này chỉ để dành một vị trí kéo.
1. #### <i class="fa fa-compress"></i> <i class="fa fa-expand"></i> Thu phóng cửa sổ {#anchor-fullscreen}
    Bạn có thể thay đổi tỷ lệ cửa sổ trò chơi chỉ với một lần nhấp bằng Magpie tích hợp.

    Nhấp chuột trái để thay đổi tỷ lệ cửa sổ, và nhấp chuột phải để thay đổi tỷ lệ toàn màn hình.

1. #### <i class="fa fa-camera"></i> <i class="fa fa-icon fa-rotate-right"></i> Ảnh chụp cửa sổ {#anchor-grabwindow}
    Bạn có thể chụp ảnh màn hình của cửa sổ được liên kết (nó sẽ chụp hai ảnh màn hình theo mặc định, GDI và Winrt, cả hai đều có một xác suất nhất định để thất bại). Điều tuyệt vời nhất là nếu bạn đang sử dụng Magpie để thay đổi tỷ lệ, nó cũng sẽ chụp ảnh màn hình của cửa sổ đã được phóng to.

    Khi nhấp chuột trái, ảnh chụp màn hình sẽ được lưu vào tệp, và khi nhấp chuột phải, ảnh chụp màn hình sẽ được lưu vào clipboard. Nút giữa mở lớp phủ trong trò chơi.

1. #### <i class="fa fa-volume-off"></i> <i class="btnstatus2 fa fa-volume-up"></i> Im lặng trò chơi {#anchor-muteprocess}
    Sau khi liên kết cửa sổ trò chơi (không chỉ trong chế độ HOOK, chế độ OCR hoặc clipboard cũng có thể, miễn là cửa sổ trò chơi được liên kết), bạn có thể tắt tiếng trò chơi chỉ với một lần nhấp, tiết kiệm rắc rối của việc tắt tiếng trò chơi trong bộ trộn âm lượng hệ thống.
1. #### <i class="fa fa-eye"></i> <i class="btnstatus2 fa fa-eye-slash"></i> Hiển thị/ẩn văn bản gốc {#anchor-showraw}
    Chuyển đổi việc hiển thị văn bản gốc, sẽ có hiệu lực ngay lập tức.

1. #### <i class="fa fa-toggle-on"></i> <i class="btnstatus2 fa fa-toggle-off"></i> Hiện/ẩn bản dịch {#anchor-showtrans}
    Chuyển đổi việc sử dụng dịch thuật, đây là công tắc chính cho dịch thuật. Nếu tắt, không có dịch thuật nào sẽ được thực hiện.

    Nếu một dịch thuật đã được thực hiện, tắt nó sẽ ẩn kết quả dịch, và nó sẽ hiển thị lại kết quả dịch hiện tại khi bật lại.

    Nếu không có dịch thuật nào đã được thực hiện và nó được chuyển từ ẩn sang hiển thị, nó sẽ kích hoạt dịch thuật của câu hiện tại.

1. #### <i class="fa fa-music"></i> <i class="fa fa-icon fa-rotate-right"></i> Đọc to {#anchor-langdu}
    Nhấp chuột trái vào nút sẽ thực hiện chuyển văn bản thành giọng nói trên văn bản hiện tại.

    Nhấp chuột phải vào nút sẽ ngắt đọc.
  
    Việc đọc này sẽ bỏ qua `Bỏ qua` (nếu trong `Cài đặt giọng nói`, mục tiêu văn bản hiện tại được khớp là `Bỏ qua`, thì việc sử dụng nút để đọc sẽ bỏ qua bỏ qua và buộc đọc).
1. #### <i class="fa fa-copy"></i> <i class="fa fa-icon fa-rotate-right"></i> Sao chép vào bảng nháp {#anchor-copy}
    Sao chép văn bản hiện tại đã được trích xuất vào clipboard một lần. Nếu muốn tự động trích xuất vào clipboard, bật `Nhập văn bản` → `Clipboard` → `Tự động xuất` → `Tự động xuất văn bản`.
1. #### <i class="fa fa-rotate-left"></i> <i class="fa fa-icon fa-rotate-right"></i> Hiển thị / ẩn văn bản lịch sử {#anchor-history}
    Mở hoặc đóng cửa sổ văn bản lịch sử.
1. #### <i class="fa fa-gamepad"></i> <i class="fa fa-icon fa-rotate-right"></i> Quản lý trò chơi {#anchor-gamepad_new}
    Mở giao diện quản lý trò chơi.
1. #### <i class="fa fa-edit"></i> <i class="fa fa-icon fa-rotate-right"></i> Chỉnh sửa {#anchor-edit}
    Mở cửa sổ chỉnh sửa để chỉnh sửa văn bản hiện tại đã được trích xuất.

    Trong cửa sổ này, bạn có thể chỉnh sửa văn bản và sau đó thực hiện dịch thuật; hoặc bạn có thể dịch bất kỳ văn bản nào bạn tự nhập.
1. #### <i class="fa fa-edit"></i> <i class="fa fa-icon fa-rotate-right"></i> Chỉnh sửa Bản dịch {#anchor-edittrans}
    Mở cửa sổ chỉnh sửa lịch sử dịch thuật cho trò chơi hiện tại.
1. #### <i class="fa fa-download"></i> <i class="fa fa-icon fa-rotate-right"></i> Mô phỏng phím Ctrl {#anchor-simulate_key_ctrl}
1. #### <i class="fa fa-download"></i> <i class="fa fa-icon fa-rotate-right"></i> Mô phỏng phím Enter {#anchor-simulate_key_enter}
    Như trên, nó được sử dụng để gửi một lần nhấn phím mô phỏng đến cửa sổ trò chơi. Nó có một số tác dụng khi sử dụng streaming/tablet.
1. #### <i class="fa fa-list-ul"></i> <i class="fa fa-icon fa-rotate-right"></i> Bản ghi nhớ {#anchor-memory}
    Mở cửa sổ ghi chú cho trò chơi bạn đang chơi.

    Khi bạn nhấp chuột trái, ghi chú cho trò chơi hiện tại sẽ được mở. Khi bạn nhấp chuột phải, ghi chú toàn cầu sẽ được mở.
1. #### <i class="fab fa-windows"></i> <i class="btnstatus2 fab fa-windows"></i> Cửa sổ bị ràng buộc (Click vào tự hủy) {#anchor-bindwindow}
    **Nút này rất quan trọng, nhiều tính năng phụ thuộc vào nút này được đặt trước khi chúng có thể được sử dụng**

    Sau khi liên kết cửa sổ trò chơi, `Tỷ lệ cửa sổ` `Chụp màn hình cửa sổ` `Tắt tiếng trò chơi`, `Theo dõi cửa sổ trò chơi` -> `Bỏ ghim khi trò chơi mất tiêu điểm` và `Đồng bộ hóa với chuyển động của cửa sổ trò chơi`, cũng như ghi lại thời gian chơi trò chơi, v.v., đều có sẵn.
    Nút này có sẵn bất kể chế độ HOOK/OCR/Clipboard.

    Trong chế độ HOOK, nó sẽ tự động liên kết cửa sổ trò chơi theo trò chơi được kết nối, nhưng bạn cũng có thể sử dụng nút này để chọn lại các cửa sổ khác.

    Trong chế độ OCR, sau khi liên kết cửa sổ, nó cũng cho phép khu vực OCR và hộp phạm vi di chuyển tự động đồng bộ với chuyển động của cửa sổ trò chơi.
    Trong chế độ OCR/Clipboard, sau khi liên kết cửa sổ, bạn cũng có thể liên kết với cài đặt trò chơi hiện tại như trong chế độ HOOK, để sử dụng từ điển tối ưu hóa dịch thuật dành riêng cho trò chơi hiện tại, v.v.

1. #### <i class="fa fa-neuter"></i> <i class="btnstatus2 fa fa-neuter"></i> Cửa sổ trên cùng {#anchor-keepontop}
    Hủy bỏ/Luôn ở trên cùng cửa sổ dịch

1. #### <i class="fa fa-i-cursor"></i> <i class="btnstatus2 fa fa-i-cursor"></i> Chọn {#anchor-selectable}
    Làm cho văn bản trong khu vực văn bản của cửa sổ dịch có thể chọn được.

    Nếu nhấp chuột phải trong khi kích hoạt, kéo các khu vực không phải văn bản để di chuyển cửa sổ sẽ bị cấm.

1. #### <i class="fa fa-search"></i> <i class="fa fa-icon fa-rotate-right"></i> Tra từ {#anchor-searchwordW}
    Nếu hiện tại có văn bản được chọn, văn bản đã chọn sẽ được truy vấn và một cửa sổ tìm kiếm từ khóa sẽ được mở. Nếu không, nó sẽ chỉ mở hoặc đóng cửa sổ tìm kiếm từ khóa.