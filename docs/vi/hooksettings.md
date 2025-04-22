# Cài Đặt HOOK

## Cài Đặt Chung

1. #### Mã Trang (Code Page)

    ::: info
    Cài đặt này chỉ có ý nghĩa khi văn bản được trích xuất từ trò chơi là một **chuỗi đa byte với mã hóa không xác định trong engine HOOK**. Khi engine HOOK đã xác định mã trang, hoặc văn bản là một **chuỗi ký tự rộng** hoặc chuỗi **UTF32**, cài đặt này không có ý nghĩa.
    :::
    Thông thường không cần thay đổi cài đặt này. Chỉ cần thiết khi một số engine cũ (ví dụ: Yuris) có thể sử dụng GBK/BIG5/UTF8 trong các phiên bản tiếng Trung chính thức. Nếu bạn không thể tìm thấy văn bản chính xác, vui lòng gửi một [vấn đề](https://lunatranslator.org/Resource/game_support) trực tiếp cho tôi; việc thay đổi cài đặt này thường không hiệu quả.

1. #### Độ Trễ Làm Mới (Refresh Delay)

    Nếu bạn gặp một trong các tình huống sau:

        1. Văn bản được trích xuất từng ký tự một hoặc hai ký tự một lần;
        2. Văn bản được trích xuất theo dòng, đẩy dòng trước đó ra ngoài, và chỉ hiển thị dòng cuối cùng;
        3. Văn bản đúng nhưng được trích xuất rất chậm;

    Bạn cần điều chỉnh tùy chọn này.

    Đối với **1 và 2**, vì văn bản trò chơi hiển thị quá chậm và độ trễ làm mới quá thấp, mỗi lần một hoặc hai ký tự hoặc một dòng văn bản được trích xuất, nó ngay lập tức làm mới. Trong trường hợp này, bạn cần **tăng độ trễ làm mới** hoặc tăng tốc độ hiển thị văn bản của trò chơi.

    Đối với **3**, bạn có thể **giảm độ trễ làm mới một cách hợp lý** trong khi chú ý không gây ra các tình huống **1 và 2**.

1. #### Độ Dài Bộ Đệm Tối Đa (Maximum Buffer Length)

    Đôi khi, văn bản sẽ làm mới liên tục mà không dừng lại. Nếu độ trễ làm mới cao và không thể giảm, nó sẽ tiếp tục nhận văn bản cho đến khi bộ đệm đầy hoặc văn bản ngừng làm mới để đáp ứng độ trễ làm mới (thường khi trò chơi mất tiêu điểm, vì vậy thường chờ đến khi bộ đệm đầy).

    Để giải quyết vấn đề này, bạn có thể giảm độ dài bộ đệm một cách hợp lý, nhưng hãy cẩn thận không làm cho độ dài bộ đệm quá ngắn để nhỏ hơn độ dài văn bản thực tế.

1. #### Độ Dài Văn Bản Được Lưu Trữ Tối Đa (Maximum Cached Text Length)

    Văn bản lịch sử nhận được sẽ được lưu trữ. Khi xem nội dung của một mục văn bản trong cửa sổ chọn văn bản, văn bản lịch sử được lưu trữ sẽ được truy vấn. Nếu có quá nhiều mục văn bản hoặc văn bản làm mới liên tục, nó sẽ gây ra quá nhiều văn bản được lưu trữ, làm cho việc xem văn bản trở nên chậm chạp hơn (đôi khi ngay cả khi không xem). Thực tế, hầu hết văn bản được lưu trữ ở đây là vô ích; văn bản lịch sử hữu ích có thể được xem trong cửa sổ văn bản lịch sử. Bạn có thể giảm giá trị này tùy ý (mặc định là 1000000, nhưng có thể giảm xuống 1000).

## Cài Đặt Dành Riêng Cho Trò Chơi

1. #### Hook Bổ Sung
    1. #### Hook Win32 Toàn Cục
        Sau khi kích hoạt, các hook chức năng Win32 toàn cục sẽ được tiêm vào trò chơi, bao gồm các chức năng GDI, D3DX và các chức năng chuỗi.
        Việc tiêm quá nhiều hook có thể làm chậm trò chơi, vì vậy các hook này không được tiêm theo mặc định.
        Khi không thể trích xuất văn bản chính xác, bạn có thể thử bật hai tùy chọn này.
    1. #### Mã Đặc Biệt
        Mã đặc biệt này chỉ được ghi lại khi **một mã đặc biệt được chèn** và **văn bản của mã đặc biệt được chọn**. Lần tiếp theo khi trò chơi bắt đầu, mã đặc biệt này sẽ được tự động chèn. Cài đặt này ghi lại tất cả các mã đặc biệt đã được ghi trước đó, từ đó bạn có thể thêm hoặc xóa mã đặc biệt.

1. #### Tiêm Trễ (Delayed Injection)
    Đôi khi, vị trí trong trò chơi cần được hook nằm trên một dll, chỉ tải sau khi trò chơi chạy một thời gian ngắn. Chúng ta cũng cần đợi cho đến khi dll tải trước khi tiến hành tiêm.

1. #### Cài Đặt HOOK Dành Riêng
    Các cài đặt được thực hiện trong giao diện cài đặt -> cài đặt HOOK là các cài đặt mặc định. Khi không có cài đặt HOOK dành riêng nào được chỉ định cho trò chơi, các cài đặt mặc định sẽ được sử dụng.
    
    Để thiết lập cài đặt HOOK dành riêng cho một trò chơi, bạn cần vào **Quản Lý Trò Chơi**, mở giao diện **Cài Đặt Trò Chơi**, và chuyển sang thẻ HOOK trong thẻ chọn cài đặt trò chơi. Sau khi bỏ chọn **Theo Mặc Định**, bạn có thể thiết lập cài đặt HOOK dành riêng cho trò chơi.

    ::: details
    ![img](https://image.lunatranslator.org/zh/gamesettings/1.jpg)

    ![img](https://image.lunatranslator.org/zh/gamesettings/2.png)
    :::