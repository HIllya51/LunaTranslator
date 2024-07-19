
window.$docsify = {
    // homepage: '/redirect.html',
    requestHeaders: {
        'cache-control': 'max-age=0',
    },
    notFoundPage: 'redirect.html',
    pagination: {
        previousText: '上一节',
        nextText: '下一节',
        crossChapter: true,
        crossChapterText: true,
    },
    repo: 'https://lunatranslator.xyz/Github/LunaTranslator',

    alias: {
        '/zh/_sidebar.md': '/zh/sidebar.md',
        '/ru/_sidebar.md': '/ru/sidebar.md',
        '/en/_sidebar.md': '/en/sidebar.md',
        '/_navbar.md': '/navbar.md',
        '/_coverpage.md': '/coverpage.md',
    },
    // loadNavbar: true,
    loadSidebar: true,

    auto2top: true,

    search: {
        noData: {
            '/zh/': '没有结果!',
            '/': 'No results!',
        },
        paths: 'auto',
        placeholder: {
            '/zh/': '搜索',
            '/': 'Search',
        }
    },

    executeScript: true,
    plugins: [
        function (hook, vm) {
            hook.doneEach(() => {
                var sidebar = document.getElementsByClassName("sidebar")[0];
                var resizeBar = document.createElement('div');
                resizeBar.classList.add('sidebarresizer')
                sidebar.appendChild(resizeBar);

                var startX, startWidth;
                resizeBar.addEventListener('mousedown', function (e) {
                    startX = e.clientX;
                    startWidth = sidebar.offsetWidth;
                    e.preventDefault();
                });

                document.addEventListener('mousemove', function (e) {
                    if (startX) {
                        var newWidth = startWidth + (e.clientX - startX);
                        document.documentElement.style.setProperty('--sidebar-width', Math.min(1000, Math.max(100, newWidth)) + 'px');
                    }
                });

                document.addEventListener('mouseup', function () {
                    startX = null;
                });
            })
        },
    ]
}

let dropdowns = document.getElementsByClassName('dropdown')
for (let i = 0; i < dropdowns.length; i++) {

    let dropdown = dropdowns[i]
    dropdown.addEventListener('mouseover', function () {
        this.getElementsByClassName('goodlinknormal')[0].classList.add('goodlinkhover')
        let dropdownContent = this.querySelector('.dropdown-content');
        dropdownContent.style.display = 'block';
    });
    dropdown.addEventListener('mouseout', function () {
        this.getElementsByClassName('goodlinknormal')[0].classList.remove('goodlinkhover')
        let dropdownContent = this.querySelector('.dropdown-content');
        dropdownContent.style.display = 'none';
    });
}

var currentlang = "";
const navitexts = {
    zh: {
        homepage: '官方网站',
        downloadlink: '软件下载',
        vediotutorial: '视频教学',
        contactme: '交流群'
    },
    ru: {
        homepage: 'HomePage',
        downloadlink: 'Download',
        vediotutorial: 'Vedio Tutorial',
        contactme: 'Chat Groups'
    },
    en: {
        homepage: 'HomePage',
        downloadlink: 'Download',
        vediotutorial: 'Vedio Tutorial',
        contactme: 'Chat Groups'
    }
}
function getcurrlang(url) {
    for (let key in navitexts) {
        if (url.includes(`/${key}/`)) {
            return key
        }
    }
    return ''
}
function switchlang(lang) {
    window.location.href = window.location.href.replace('/' + currentlang + '/', '/' + lang + '/')
}
window.onpopstate = function (event) {
    let url = window.location.href;
    if (url.endsWith('/#/')) {
        let lang = window.localStorage.currentlang ? window.localStorage.currentlang : 'zh'
        window.location.href += lang + '/'
        return
    }
    for (let key in navitexts) {
        if (url.endsWith(`/${key}/`)) {
            window.location.href += 'README'
            return
        }
    }
    let thislang = getcurrlang(url)
    window.localStorage.currentlang = thislang
    if (thislang != currentlang) {
        currentlang = thislang

        for (let key in navitexts[currentlang]) {
            document.getElementById(key).innerText = navitexts[currentlang][key]

        }
    }
};
