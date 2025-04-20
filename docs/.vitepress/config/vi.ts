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
    outline: {
      level: [2, 3],
      label: "Điều hướng trang"
    },
    footer: {
      copyright: `Phát hành theo giấy phép <a href="https://github.com/HIllya51/LunaTranslator/blob/main/LICENSE">GPLv3</a>`
    },
    editLink: {
      pattern: 'https://github.com/HIllya51/LunaTranslator/edit/main/docs/:path',
      text: 'Chỉnh sửa trang này trên GitHub'
    },
    docFooter: {
      prev: 'Trang trước',
      next: 'Trang tiếp theo'
    },
    lastUpdated: {
      text: 'Cập nhật lần cuối',
      formatOptions: {
        dateStyle: 'short',
        timeStyle: 'medium'
      }
    },
    nav: [
      { text: "Trang chủ", link: "https://lunatranslator.org/" },
      { text: "Discord", link: "https://discord.com/invite/ErtDwVeAbB" },
      { text: "Tài trợ", link: "/vi/support" },
    ],
    sidebar: [
      {
        text: 'Cơ bản',
        items: [
          { text: 'Tải xuống và Khởi chạy', link: '/vi/README' },
          { text: 'Sử dụng Cơ bản', link: '/vi/basicuse' },
          { text: 'Cập nhật Phần mềm', link: '/vi/update' },
          { text: 'Tài trợ', link: '/vi/support' }
        ]
      },
      // Thêm các mục sidebar khác tương tự như các ngôn ngữ khác
    ]
  }
})