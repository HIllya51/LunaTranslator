# Cài đặt HOOK

## Cài đặt Chung

1. ####  Bảng mã

    ::: info
    Cài đặt này chỉ có ý nghĩa khi văn bản được trích xuất từ trò chơi là **chuỗi đa byte với mã hóa không xác định trong công cụ HOOK**. Khi công cụ HOOK đã chỉ định bảng mã, hoặc văn bản là **chuỗi ký tự rộng** hoặc chuỗi **UTF32**, cài đặt này không có ý nghĩa.
    :::
    Cài đặt này thường không cần phải được sửa đổi. Nó chỉ cần thiết khi một số công cụ cũ (ví dụ: Yuris) có thể có GBK/BIG5/UTF8 trong phiên bản Trung Quốc chính thức. Nếu bạn không thể tìm thấy văn bản chính xác, vui lòng gửi trực tiếp một [vấn đề](https://lunatranslator.org/Resource/game_support) cho tôi; việc sửa đổi cài đặt này thường là vô ích.

1. ####  Độ trễ làm mới

    Nếu bạn gặp một trong các tình huống sau:

        1. Văn bản được trích xuất một hoặc hai ký tự mỗi lần;
        2. Văn bản được trích xuất từng dòng, đẩy dòng trước ra, và chỉ dòng cuối cùng được hiển thị;
        3. Văn bản chính xác nhưng được trích xuất rất chậm;

    Thì bạn cần điều chỉnh tùy chọn này.

    Đối với **1 và 2**, do văn bản trò chơi hiển thị quá chậm, và độ trễ làm mới quá thấp, mỗi lần một hoặc hai ký tự hoặc một dòng văn bản được trích xuất, nó sẽ làm mới ngay lập tức. Trong trường hợp này, bạn cần **tăng độ trễ làm mới** hoặc tăng tốc độ hiển thị văn bản của trò chơi.

    Đối với **3**, bạn có thể **giảm độ trễ làm mới một cách thích hợp** trong khi chú ý không gây ra tình huống **1 và 2**.

1. ####  Độ dài bộ đệm tối đa

    Đôi khi, văn bản sẽ làm mới liên tục không dừng lại. Nếu độ trễ làm mới cao và không thể giảm, nó sẽ tiếp tục nhận văn bản cho đến khi bộ đệm đầy hoặc văn bản ngừng làm mới để đáp ứng độ trễ làm mới (thường là khi trò chơi mất focus, nên nó thường đợi cho đến khi bộ đệm đầy).

    Để giải quyết vấn đề này, bạn có thể giảm độ dài bộ đệm một cách thích hợp, nhưng hãy cẩn thận không làm cho độ dài bộ đệm quá ngắn để ít hơn độ dài văn bản thực tế.

1. ####  Độ dài văn bản được lưu trữ tối đa

    Văn bản lịch sử nhận được được lưu trữ. Khi xem nội dung của một mục văn bản trong cửa sổ lựa chọn văn bản, văn bản lịch sử được lưu trữ sẽ được truy vấn. Nếu có quá nhiều mục văn bản hoặc văn bản làm mới liên tục, nó sẽ gây ra quá nhiều văn bản được lưu trữ, làm cho việc xem văn bản trở nên chậm chạp hơn (đôi khi ngay cả khi không xem). Trên thực tế, hầu hết văn bản được lưu trữ ở đây là vô dụng; văn bản lịch sử hữu ích có thể được xem trong cửa sổ văn bản lịch sử. Bạn có thể tùy ý giảm giá trị này (mặc định là 1000000, nhưng có thể giảm xuống 1000).

## Cài đặt Trò chơi Chuyên biệt

1. #### Các Hook Bổ sung
    1. #### Hook Phổ quát Win32
        Sau khi kích hoạt, các hook hàm phổ quát Win32 sẽ được chèn vào trò chơi, bao gồm các hàm GDI, hàm D3DX và hàm chuỗi.
        Việc chèn quá nhiều hook có thể làm chậm trò chơi, vì vậy các hook này không được chèn theo mặc định.
        Khi không thể trích xuất văn bản chính xác, bạn có thể thử bật hai tùy chọn này.
    1. #### Mã đặc biệt
        Mã đặc biệt này sẽ chỉ được ghi lại khi **một mã đặc biệt được chèn** và **văn bản của mã đặc biệt được chọn**. Lần sau khi trò chơi khởi động, mã đặc biệt này sẽ được tự động chèn. Cài đặt này ghi lại tất cả các mã đặc biệt đã được ghi trước đó, từ đó bạn có thể thêm hoặc xóa mã đặc biệt.

1. #### Chèn Trễ
    Đôi khi, vị trí trong trò chơi cần được hook nằm trên một tệp dll, mà sẽ chỉ tải sau khi trò chơi đã chạy một thời gian ngắn. Chúng ta cũng cần đợi cho đến khi tệp dll tải xong trước khi có thể tiếp tục với việc chèn.

1. #### Cài đặt HOOK Chuyên biệt
    Các cài đặt được thực hiện trong giao diện cài đặt -> cài đặt HOOK là cài đặt mặc định. Khi không có cài đặt HOOK chuyên biệt nào được chỉ định cho trò chơi, cài đặt mặc định sẽ được sử dụng.
    
    Để thiết lập cài đặt HOOK chuyên biệt cho một trò chơi, bạn cần đi đến **Quản lý Trò chơi**, mở giao diện **Cài đặt Trò chơi**, và chuyển đến tab phụ HOOK trong thẻ lựa chọn cài đặt trò chơi. Sau khi bỏ chọn **Theo Mặc định**, bạn có thể thiết lập cài đặt HOOK chuyên biệt cho trò chơi.

    ::: details
    ![img](https://image.lunatranslator.org/zh/gamesettings/1.jpg)

    ![img](https://image.lunatranslator.org/zh/gamesettings/2.png)
    :::