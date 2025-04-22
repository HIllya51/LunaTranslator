# Dịch Nhúng

## Cách sử dụng

::: danger
 Trước tiên, không phải tất cả các trò chơi đều hỗ trợ nhúng. Thứ hai, việc nhúng có thể khiến trò chơi bị treo.
:::

::: details Nếu dòng 'Nhúng' không khả dụng trong lựa chọn văn bản, điều đó có nghĩa là không hỗ trợ nhúng.
![img](https://image.lunatranslator.org/zh/embed/noembed.png) 
![img](https://image.lunatranslator.org/zh/embed/someembed.png) 
:::

Đối với các trò chơi hỗ trợ nhúng, hãy chọn các mục văn bản hỗ trợ nhúng và kích hoạt nó.

![img](https://image.lunatranslator.org/zh/embed/select.png) 

Đối với các mục hỗ trợ nhúng, bạn có thể tự do chọn kích hoạt cả **Hiển thị** và **Nhúng**. Khi cả hai được kích hoạt, bản dịch sẽ được nhúng vào trò chơi và nhiều bản dịch hơn sẽ được hiển thị trong cửa sổ phần mềm; nếu chỉ kích hoạt nhúng, chỉ các bản dịch nhúng sẽ được hiển thị trong trò chơi, và cửa sổ phần mềm sẽ không hiển thị gì.

Khi bắt đầu dịch nhúng, thường xảy ra lỗi hiển thị văn bản. Lỗi này thường do **bộ ký tự** và **phông chữ**. Đối với các trò chơi tiếng Anh, lỗi thường do thiếu **phông chữ tiếng Trung**, ví dụ:

![img](https://image.lunatranslator.org/zh/embed/luanma.png) 

Lúc này, bạn cần kích hoạt **Chỉnh sửa Phông chữ Trò chơi** và chọn một phông chữ phù hợp để hiển thị ký tự tiếng Trung.

![img](https://image.lunatranslator.org/zh/embed/ziti.png) 

Sau khi chỉnh sửa phông chữ, ký tự tiếng Trung có thể được hiển thị chính xác:

![img](https://image.lunatranslator.org/zh/embed/okembed.png) 

Đối với nhiều trò chơi galgame Nhật Bản cổ điển, chúng sử dụng bộ ký tự shift ji tích hợp để xử lý ký tự tiếng Trung chính xác. Bạn có thể thử **chuyển đổi ký tự tiếng Trung sang ký tự truyền thống/tiếng Nhật** để giảm lỗi hiển thị.

Đối với các công cụ trò chơi mới hơn và hầu hết các trò chơi tiếng Anh, các bộ ký tự Unicode như utf-8 hoặc utf-16 thường được sử dụng (như **KiriKiri**, **Renpy**, **TyranoScript**, **RPGMakerMV**, v.v.), và ngay cả khi xảy ra lỗi hiển thị, thường là vấn đề phông chữ, không phải vấn đề bộ ký tự.

![img](https://image.lunatranslator.org/zh/embed/fanti.png) 

Sau khi bỏ chọn cài đặt này, tiếng Trung giản thể có thể được hiển thị chính xác. Tuy nhiên, đối với một số trò chơi không thể hiển thị tiếng Trung giản thể chính xác, bạn có thể thử kích hoạt tùy chọn này để xem liệu nó có thể hiển thị bình thường không.

![img](https://image.lunatranslator.org/zh/embed/good.png) 

## Cài đặt Dịch Nhúng

1. #### Chế độ Hiển thị

    ![img](https://image.lunatranslator.org/zh/embed/keeporigin.png) 

    Do giới hạn số dòng văn bản mà trò chơi có thể hiển thị, theo mặc định, không có ngắt dòng được thêm giữa bản dịch và văn bản gốc. Nếu bạn chắc chắn rằng nó có thể chứa, bạn có thể thêm ngắt dòng trước bản dịch bằng cách thêm regex trong **Tối ưu hóa Dịch thuật** -> **Chỉnh sửa Kết quả Dịch**.

    ![img](https://image.lunatranslator.org/zh/embed/addspace.png) 

1. #### Thời gian Chờ Dịch thuật

    Nguyên tắc của dịch nhúng là tạm dừng trò chơi trong một chức năng nhất định trước khi trò chơi hiển thị văn bản, gửi văn bản cần dịch đến trình dịch, chờ dịch, chỉnh sửa bộ nhớ văn bản từ văn bản đã dịch, và sau đó để trò chơi tiếp tục hiển thị bản dịch. Do đó, **khi sử dụng dịch thuật chậm hơn, chắc chắn sẽ gây ra hiện tượng giật lag trong trò chơi**. Bạn có thể tránh hiện tượng giật lag lâu dài do dịch thuật chậm bằng cách giới hạn thời gian chờ.

1. #### Chuyển đổi Ký tự sang Truyền thống/Nhật Bản

    Bỏ qua

1. #### Giới hạn Số ký tự mỗi Dòng

    Đôi khi một số trò chơi có giới hạn số ký tự mỗi dòng, và nội dung vượt quá độ dài sẽ được hiển thị ngoài hộp văn bản bên phải và không thể hiển thị. Bạn có thể tự ngắt dòng để tránh tình trạng này thông qua cài đặt này.

    ![img](https://image.lunatranslator.org/zh/embed/limitlength.png) 

1. #### Chỉnh sửa Phông chữ Trò chơi

    Bỏ qua

1. #### Kiểm tra An toàn Nhúng

    Đối với các trò chơi như Renpy, văn bản được trích xuất thường bao gồm các ký tự của các phần tử cú pháp như `{` `}` `[` `]`. Nếu nguồn dịch không xử lý đúng các nội dung này, nó sẽ phá vỡ cú pháp và khiến trò chơi bị treo. Do đó, phần mềm mặc định **bỏ qua dịch thuật** của một số tổ hợp ký tự có thể gây ra lỗi trò chơi bằng cách khớp regex. Nếu bạn không lo lắng về lỗi trò chơi, bạn có thể hủy cài đặt này, hoặc thay thế thủ công một số khớp regex chi tiết hơn để giảm bỏ qua không cần thiết.

    ![img](https://image.lunatranslator.org/zh/embed/safeskip.png)
    
1. #### Xóa Văn bản Hiển thị trong Trò chơi

    Sau khi bật tùy chọn này, nội dung dự định hiển thị dưới dạng văn bản nhúng trong trò chơi sẽ bị xóa.

    Tùy chọn này có thể đáp ứng các nhu cầu sau:

    1. Đôi khi, bản dịch nhúng gặp phải các vấn đề không thể giải quyết được với mã hóa ký tự và phông chữ không thể hiển thị chính xác. Bằng cách bật tùy chọn này và sau đó phủ cửa sổ phần mềm lên vị trí mà văn bản thường xuất hiện trong trò chơi, nó có thể tạo ra ảo giác về một bản dịch nhúng.

    1. Đôi khi, thay vì nhúng bản dịch, chúng ta có thể sử dụng các công cụ dịch thuật bên ngoài. Trong những trường hợp như vậy, đặt cửa sổ dịch thuật lên khu vực văn bản có thể gây chồng chéo với văn bản gốc, trong khi di chuyển nó đến nơi khác có thể che khuất màn hình trò chơi.
    
    1. Đôi khi, chúng ta chỉ muốn sử dụng trò chơi để học tiếng Nhật, nhưng văn bản trò chơi không có các tính năng như chú thích furigana hoặc hiển thị song ngữ.
