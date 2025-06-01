import { defineConfig } from 'vitepress'

export const viSearch = {
  vi: {
    placeholder: 'Tìm kiếm tài liệu',
    translations: {
      button: {
        buttonText: 'Tìm kiếm tài liệu',
        buttonAriaLabel: 'Tìm kiếm tài liệu'
      },
      modal: {
        searchBox: {
          resetButtonTitle: 'Xóa truy vấn',
          resetButtonAriaLabel: 'Xóa truy vấn',
          cancelButtonText: 'Hủy bỏ',
          cancelButtonAriaLabel: 'Hủy bỏ'
        },
        startScreen: {
          recentSearchesTitle: 'Lịch sử tìm kiếm',
          noRecentSearchesText: 'Không có lịch sử tìm kiếm',
          saveRecentSearchButtonTitle: 'Lưu vào lịch sử tìm kiếm',
          removeRecentSearchButtonTitle: 'Xóa khỏi lịch sử tìm kiếm',
          favoriteSearchesTitle: 'Yêu thích'
        },
        errorScreen: {
          titleText: 'Không thể lấy kết quả',
          helpText: 'Bạn có thể cần kiểm tra kết nối mạng'
        },
        footer: {
          selectText: 'Chọn',
          navigateText: 'Điều hướng',
          closeText: 'Đóng',
          searchByText: 'Tìm kiếm bởi'
        },
        noResultsScreen: {
          noResultsText: 'Không tìm thấy kết quả',
          suggestedQueryText: 'Bạn có thể thử tìm kiếm',
          reportMissingResultsText: 'Bạn cho rằng truy vấn này nên có kết quả?',
          reportMissingResultsLinkText: 'Báo cáo'
        }
      }
    }
  }
}

export const vi = defineConfig({

  themeConfig: {
      footer: {
          copyright: `Phát hành theo giấy phép <a href="https://github.com/HIllya51/LunaTranslator/blob/main/LICENSE">GPLv3</a>`
      },
      nav: [
          { text: "Trang chủ", link: "https://lunatranslator.org/" },
          { text: "Discord", link: "https://discord.com/invite/ErtDwVeAbB" },
          { text: "Tài trợ", link: "/vi/support" },
      ],
      editLink: {
          pattern: 'https://github.com/vuejs/vitepress/edit/main/docs/:path',
          text: 'Chỉnh sửa trang này trên GitHub'
      },
      sidebar: [
          {
              text: 'Cơ bản',
              items: [
                  { text: 'Tải xuống và khởi chạy', link: '/vi/README' },
                  { text: 'Sử dụng cơ bản', link: '/vi/basicuse' },
                  { text: 'Cập nhật phần mềm', link: '/vi/update' },
                  { text: 'Tài trợ', link: '/vi/support' }
              ]
          },
          {
              text: 'Chi tiết',
              items: [
                  {
                      text: 'Cài đặt liên quan đến HOOK', link: '/vi/hooksettings',
                      collapsed: true,
                      items: [
                          { text: 'Cài đặt HOOK', link: '/vi/hooksettings' },
                          { text: 'Dịch nhúng', link: '/vi/embedtranslate' },
                          { text: 'Hỗ trợ trò chơi giả lập', link: '/vi/emugames' },
                      ]
                  },
                  {
                      text: 'Cài đặt liên quan đến OCR', link: '/vi/useapis/ocrapi',
                      collapsed: true,
                      items: [
                          { text: 'Cài đặt giao diện OCR', link: '/vi/useapis/ocrapi' },
                          { text: 'Phương pháp thực thi tự động OCR', link: '/vi/ocrparam' },
                          { text: 'Gắn cửa sổ trò chơi trong chế độ OCR', link: '/vi/gooduseocr' }
                      ]
                  },
                  {
                      text: 'Cài đặt giao diện dịch thuật', link: '/vi/useapis/tsapi',
                      collapsed: true,
                      items: [
                          { text: 'Giao diện dịch mô hình lớn', link: '/vi/guochandamoxing' },
                          { text: 'Giao diện dịch thuật trực tuyến truyền thống', link: '/vi/useapis/tsapi' },
                      ]
                  },
                  {
                      text: 'Xử lý văn bản & Tối ưu hóa dịch thuật', link: '/vi/textprocess',
                      collapsed: true,
                      items: [
                          { text: 'Chức năng và cách sử dụng các phương pháp xử lý văn bản', link: '/vi/textprocess' },
                          { text: 'Chức năng của các tối ưu hóa dịch thuật', link: '/vi/transoptimi' }
                      ]
                  },
                    {
                        text: '语音合成', link: '/vi/ttsengines',
                        collapsed: true,
                        items: [
                            { text: '语音合成引擎', link: '/vi/ttsengines' },
                            { text: 'Sử dụng giọng nói khác nhau cho từng nhân vật', link: '/vi/ttsofname' }
                        ]
                    },
                  {
                      text: 'Phân đoạn & Từ điển & Anki', link: '/vi/qa1',
                      collapsed: true,
                      items: [
                          { text: 'Sử dụng Mecab để phân đoạn & tô màu theo loại từ', link: '/vi/qa1' },
                          { text: 'Tích hợp Anki', link: '/vi/qa2' }
                      ]
                  },
                  { text: 'Nút công cụ', link: '/vi/alltoolbuttons' },
                  { text: 'Phím tắt', link: '/vi/fastkeys' },
                  { text: 'Dịch vụ mạng', link: '/vi/apiservice' },
                  { text: 'Nhận dạng giọng nói', link: '/vi/sr' },

              ]
          }
      ]
  }
})
