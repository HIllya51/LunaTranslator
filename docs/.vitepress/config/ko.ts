import { defineConfig } from 'vitepress'

export const koSearch = {
    ko: {
        placeholder: '문서 검색',
        translations: {
            button: {
                buttonText: '문서 검색',
                buttonAriaLabel: '문서 검색'
            },
            modal: {
                searchBox: {
                    resetButtonTitle: '검색 조건 초기화',
                    resetButtonAriaLabel: '검색 조건 초기화',
                    cancelButtonText: '취소',
                    cancelButtonAriaLabel: '취소'
                },
                startScreen: {
                    recentSearchesTitle: '검색 기록',
                    noRecentSearchesText: '검색 기록이 없습니다',
                    saveRecentSearchButtonTitle: '검색 기록에 저장',
                    removeRecentSearchButtonTitle: '검색 기록에서 제거',
                    favoriteSearchesTitle: '즐겨찾기',
                    removeFavoriteSearchButtonTitle: '즐겨찾기에서 제거'
                },
                errorScreen: {
                    titleText: '결과를 가져올 수 없습니다',
                    helpText: '네트워크 연결을 확인해 주세요'
                },
                footer: {
                    selectText: '선택',
                    navigateText: '전환',
                    closeText: '닫기',
                    searchByText: '검색 제공자'
                },
                noResultsScreen: {
                    noResultsText: '관련 결과를 찾을 수 없습니다',
                    suggestedQueryText: '다음과 같이 검색해 보세요',
                    reportMissingResultsText: '이 검색어에 결과가 있어야 한다고 생각하시나요?',
                    reportMissingResultsLinkText: '클릭하여 피드백'
                }
            }
        }
    }
}

export const ko = defineConfig({
    themeConfig: {
        outline: {
            level: [2, 3],
            label: "페이지 네비게이션"
        },
        footer: {
            copyright: `<a href="https://github.com/HIllya51/LunaTranslator/blob/main/LICENSE">GPLv3</a> 라이선스 하에 배포됨`
        },

        editLink: {
            pattern: 'https://github.com/HIllya51/LunaTranslator/edit/main/docs/:path',
            text: 'GitHub에서 이 페이지 편집'
        },

        docFooter: {
            prev: '이전 페이지',
            next: '다음 페이지'
        },

        lastUpdated: {
            text: '마지막 업데이트',
            formatOptions: {
                dateStyle: 'short',
                timeStyle: 'medium'
            }
        },
        nav: [
            // { text: "공식 웹사이트", link: "https://lunatranslator.org/" },
            { text: "Discord", link: "https://discord.com/invite/ErtDwVeAbB" },
            { text: "작가 지원", link: "/ko/support" },
        ],
        sidebar: [
            {
                text: '기본',
                items: [
                    { text: '소프트웨어 다운로드 & 자주 묻는 질문', link: '/ko/README' },
                    { text: '기본 사용법', link: '/ko/basicuse' },
                    { text: '작가 지원', link: '/ko/support' }
                ]
            },
            {
                text: '상세',
                items: [
                    {
                        text: 'HOOK 관련 설정', link: '/ko/hooksettings',
                        collapsed: true,
                        items: [
                            { text: 'HOOK 설정', link: '/ko/hooksettings' },
                            { text: '내장 번역', link: '/ko/embedtranslate' },
                            { text: '에뮬레이터 게임 지원', link: '/ko/emugames' },
                        ]
                    },
                    {
                        text: 'OCR 관련 설정', link: '/ko/useapis/ocrapi',
                        collapsed: true,
                        items: [
                            { text: 'OCR 인터페이스 설정', link: '/ko/useapis/ocrapi' },
                            { text: 'OCR 자동 실행 방법', link: '/ko/ocrparam' },
                        ]
                    },
                    {
                        text: '번역 인터페이스 설정', link: '/ko/guochandamoxing',
                        collapsed: true,
                        items: [
                            { text: '대형 모델 번역 인터페이스', link: '/ko/guochandamoxing' },
                            { text: '전통 온라인 번역 인터페이스', link: '/ko/useapis/tsapi' },
                        ]
                    },
                    {
                        text: '텍스트 처리&번역 최적화', link: '/ko/textprocess',
                        collapsed: true,
                        items: [
                            { text: '다양한 텍스트 처리 방법의 기능과 사용법', link: '/ko/textprocess' },
                            { text: '다양한 번역 최적화의 기능', link: '/ko/transoptimi' }
                        ]
                    },
                    {
                        text: '음성 합성', link: '/ko/ttsengines',
                        collapsed: true,
                        items: [
                            { text: '음성 합성 엔진', link: '/ko/ttsengines' },
                            { text: '다른 캐릭터에 따라 다른 음성 사용', link: '/ko/ttsofname' }
                        ]
                    },
                    {
                        text: '언어 학습', link: '/ko/qa1',
                        collapsed: true,
                        items: [
                            { text: '일본어 단어 분할 및 가나 발음 표기', link: '/ko/qa1' },
                            { text: '내장 사전 도구 사용 방법', link: '/ko/internaldict' },
                            { text: 'Yomitan 브라우저 확장 프로그램 설치', link: '/ko/yomitan' },
                            { text: 'Anki 통합', link: '/ko/qa2' },
                        ]
                    },
                    { text: '도구 버튼', link: '/ko/alltoolbuttons' },
                    { text: '단축 키', link: '/ko/fastkeys' },
                    { text: '네트워크 서비스', link: '/ko/apiservice' },
                    { text: '음성 인식', link: '/ko/sr' },
                    {
                        text: '실용적인 팁', link: '/ko/gooduse/multiconfigs',
                        collapsed: true,
                        items: [
                            { text: '여러 구성 파일 생성', link: '/ko/gooduse/multiconfigs' },
                            { text: 'HOOK 모드에서 일시적으로 OCR 사용하기', link: '/ko/gooduse/useocrinhook' },
                            { text: 'OCR 모드 게임 창 바인딩', link: '/ko/gooduse/gooduseocr' },
                        ]
                    },
                ]
            }
        ]
    }
})