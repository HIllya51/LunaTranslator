# Chức năng và Cách Sử dụng Các Phương pháp Xử lý Văn bản

::: info
Thông thường, trong chế độ HOOK, đôi khi văn bản không chính xác được đọc, chẳng hạn như văn bản lặp lại hoặc văn bản lộn xộn khác. Trong những trường hợp như vậy, cần xử lý văn bản để giải quyết vấn đề.
:::

::: tip
Nếu có những hình thức lỗi rất phức tạp, bạn có thể kích hoạt nhiều phương pháp xử lý và điều chỉnh thứ tự thực hiện của chúng để có được sự kết hợp phong phú của các phương pháp xử lý.
:::

::: tip
Hầu hết các phương pháp xử lý không có hiệu lực khi nhúng bản dịch để giảm khả năng trò chơi bị sự cố. Các phương pháp có thể được sử dụng bao gồm: `Lọc Ký tự Xuống dòng`, `Thay thế Chuỗi`, `Xử lý Python Tùy chỉnh`, `Lọc Dấu Ngoặc Nhọn <>`, `Xóa Dấu Ngoặc Móc {}`
:::

1. #### Lọc Các Ký tự Không thuộc Bộ Ký tự Tiếng Nhật trong Văn bản

    Đôi khi, văn bản bị lỗi được hook. Vì vấn đề này thường xảy ra trong các trò chơi tiếng Nhật, phương pháp này được thiết lập sẵn để lọc ra **các ký tự không thể được mã hóa bằng bộ ký tự shift-jis**, ví dụ:

    `エマさんԟのイԠラストは全部大好き！` sẽ được xử lý thành `エマさんのイラストは全部大好き！`

1. #### Lọc Ký tự Điều khiển

    Phương pháp này sẽ lọc ra các ký tự điều khiển ASCII trong văn bản, chẳng hạn như `` v.v.

1. #### Lọc Dấu câu tiếng Anh

    Phương pháp này sẽ lọc ra ```!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~``` trong văn bản.

1. #### Lọc Ký tự Bên ngoài「」

    Ví dụ: `こなみ「ひとめぼれってやつだよね……」` sẽ được xử lý thành `「ひとめぼれってやつだよね……」`

1. #### Xóa Dấu Ngoặc Móc {}

    Nhiều kịch bản trò chơi sử dụng {} và một số ký tự khác để thêm furigana vào kanji, ví dụ: `{kanji/furigana}` và `{kanji:furigana}`, chẳng hạn như `「{恵麻/えま}さん、まだ{起き/おき}てる？」` hoặc `「{恵麻:えま}さん、まだ{起き:おき}てる？」` sẽ được xử lý thành `「恵麻さん、まだ起きてる？」`. Nó sẽ trước tiên cố gắng loại bỏ furigana theo các mẫu này, sau đó loại bỏ tất cả các dấu ngoặc móc và nội dung của chúng.

1. #### Trích xuất Số lượng Dòng Cụ thể

    Phương pháp này sẽ trích xuất số dòng được chỉ định bởi **Số Dòng Cần Trích xuất**.

    Nếu **Trích xuất từ Cuối** được kích hoạt, nó sẽ trích xuất số dòng chỉ định từ cuối văn bản.

1. #### Xóa Ký tự Trùng lặp _AAAABBBBCCCC->ABC

    Đây là bộ lọc được sử dụng phổ biến nhất.

    Do cách các trò chơi đôi khi vẽ văn bản (ví dụ: vẽ văn bản, sau đó là bóng, sau đó là viền), chế độ HOOK có thể trích xuất cùng một ký tự nhiều lần. Ví dụ, `恵恵恵麻麻麻さささんんんははは再再再びびび液液液タタタブブブへへへ視視視線線線ををを落落落とととすすす。。。` sẽ được xử lý thành `恵麻さんは再び液タブへ視線を落とす。`. Số lần lặp lại mặc định là `1`, tự động phân tích số lượng ký tự lặp lại, nhưng có thể có sự không chính xác, vì vậy nên chỉ định một số lần lặp lại cụ thể.

1. #### Xóa Dòng Trùng lặp _ABCDABCDABCD->ABCD

    Điều này cũng phổ biến, tương tự như trên, nhưng thường không làm mới lặp lại, mà làm mới nhanh nhiều lần. Hiệu ứng là `恵麻さんは再び液タブへ視線を落とす。恵麻さんは再び液タブへ視線を落とす。恵麻さんは再び液タブへ視線を落とす。` sẽ trở thành `恵麻さんは再び液タブへ視線を落とす。`. Tương tự, số lần lặp lại mặc định là `1`, tự động phân tích số lượng ký tự lặp lại, nhưng có thể có sự không chính xác, vì vậy nên chỉ định một số lần lặp lại cụ thể.

1. #### Xóa Dòng Trùng lặp _S1S1S1S2S2S2->S1S2

    Điều này tương đối phức tạp; đôi khi, số lần làm mới của mỗi câu không hoàn toàn giống nhau, vì vậy chương trình phải phân tích cách loại bỏ trùng lặp. Ví dụ, `恵麻さん……ううん、恵麻ははにかむように私の名前を呼ぶ。恵麻さん……ううん、恵麻ははにかむように私の名前を呼ぶ。恵麻さん……ううん、恵麻ははにかむように私の名前を呼ぶ。なんてニヤニヤしていると、恵麻さんが振り返った。私は恵麻さんの目元を優しくハンカチで拭う。私は恵麻さんの目元を優しくハンカチで拭う。` nơi `恵麻さん……ううん、恵麻ははにかむように私の名前を呼ぶ。` lặp lại 3 lần, `なんてニヤニヤしていると、恵麻さんが振り返った。` không lặp lại, và `私は恵麻さんの目元を優しくハンカチで拭う。` lặp lại 2 lần, phân tích cuối cùng sẽ nhận được `恵麻さん……ううん、恵麻ははにかむように私の名前を呼ぶ。なんてニヤしていると、恵麻さんが振り返った。私は恵麻さんの目元を優しくハンカチで拭う。`, nơi do sự phức tạp, có thể có một vài lỗi phân tích, điều này không thể tránh khỏi, nhưng nói chung, nó có thể nhận được kết quả chính xác.

1. #### Lọc Dấu Ngoặc Nhọn <>

    Đây thực sự là lọc các thẻ HTML, nhưng tên được viết như vậy để tránh nhầm lẫn cho người mới bắt đầu. Ví dụ, `<div>`, `</div>`, và `<div id="dsds">` sẽ được lọc. Điều này chủ yếu được sử dụng trong các trò chơi TyranoScript nơi chế độ HOOK trích xuất văn bản dưới dạng innerHTML, thường chứa nhiều thẻ như vậy.

1. #### Lọc Ký tự Xuống dòng

    Ban đầu được đặt tên là **Lọc Ký tự Xuống dòng Ngôn ngữ Thích ứng**, **Lọc Ký tự Xuống dòng** cũ đã bị ngừng sử dụng.

    Nếu ngôn ngữ nguồn không phải là tiếng Nhật, khi lọc ký tự xuống dòng, chúng sẽ được thay thế bằng khoảng trắng thay vì bị lọc ra để tránh nhiều từ bị nối liền nhau.

1. #### Lọc Số

    N/A

1. #### Lọc Chữ cái tiếng Anh

    N/A

1. #### Xóa Dòng Trùng lặp _ABCDBCDCDD->ABCD

    Điều này cũng phổ biến. Lý do cho điều này là đôi khi chức năng HOOK để hiển thị văn bản có văn bản hiển thị dưới dạng tham số, được gọi mỗi khi một ký tự được hiển thị, và mỗi lần chuỗi tham số trỏ đến ký tự tiếp theo, dẫn đến việc cuộc gọi đầu tiên đã nhận được văn bản hoàn chỉnh, và các cuộc gọi tiếp theo xuất ra chuỗi con còn lại cho đến khi độ dài giảm xuống 0. Ví dụ, `恵麻さんは再び液タブへ視線を落とす。麻さんは再び液タブへ視線を落とす。さんは再び液タブへ視線を落とす。んは再び液タブへ視線を落とす。は再び液タブへ視線を落とす。再び液タブへ視線を落とす。び液タブへ視線を落とす。液タブへ視線を落とす。タブへ視線を落とす。ブへ視線を落とす。へ視線を落とす。視線を落とす。線を落とす。を落とす。落とす。とす。す。。` sẽ được phân tích để xác định rằng văn bản thực sự nên là `恵麻さんは再び液タブへ視線を落とす。`

1. #### Xóa Dòng Trùng lặp _AABABCABCD->ABCD

    Điều này cũng phổ biến. Lý do cho điều này là mỗi khi một ký tự được vẽ, các ký tự trước đó được vẽ lại khi ký tự tiếp theo được vẽ. Ví dụ, `恵麻恵麻さ恵麻さん恵麻さんは恵麻さんは再恵麻さんは再び恵麻さんは再び液恵麻さんは再び液タ恵麻さんは再び液タブ恵麻さんは再び液タブへ恵麻さんは再び液タブへ視恵麻さんは再び液タブへ視線恵麻さんは再び液タブへ視線を恵麻さんは再び液タブへ視線を落恵麻さんは再び液タブへ視線を落と恵麻さんは再び液タブへ視線を落とす恵麻さんは再び液タブへ視線を落とす。` sẽ được phân tích để xác định rằng văn bản thực sự nên là `恵麻さんは再び液タブへ視線を落とす。`

    Khi có nhiều dòng văn bản, mỗi dòng được xử lý riêng biệt theo logic trên, điều này mang lại nhiều phức tạp hơn. Do sự phức tạp, việc xử lý này thường không thể xử lý chính xác. Nếu gặp phải, nên viết một kịch bản Python tùy chỉnh để giải quyết.

1. #### Xử lý Python Tùy chỉnh

    Viết một kịch bản Python cho việc xử lý phức tạp hơn. Khi kịch bản xử lý không tồn tại, nó sẽ tự động tạo một tệp `mypost.py` và mẫu sau trong thư mục userconfig:

    ```
    def POSTSOLVE(line):
        return line
    ```

1. #### Thay thế Chuỗi

    Không chỉ thay thế mà còn chủ yếu được sử dụng để lọc. Ví dụ, các ký tự bị lỗi cố định, các ký tự tam giác ngược được làm mới lặp lại, v.v., có thể được lọc bằng cách thay thế chúng bằng khoảng trắng.

    Cả hai tùy chọn `Regex` và `Escape` có thể được kích hoạt đồng thời, hoặc chỉ một trong số chúng, hoặc không có cái nào.

    Khi không có cái nào được kích hoạt, sẽ sử dụng thay thế chuỗi thông thường.

    Khi `Escape` được kích hoạt, nội dung nhập sẽ được coi là một chuỗi đã thoát thay vì một chuỗi ký tự. Ví dụ, `\n` có thể được sử dụng để đại diện cho ký tự xuống dòng, do đó cho phép lọc các ký tự chỉ xuất hiện trước hoặc sau ký tự xuống dòng.

    Khi `Regex` được kích hoạt, sẽ sử dụng thay thế biểu thức chính quy.