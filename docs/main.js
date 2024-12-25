const supportlangs = { zh: '简体中文', en: 'English', ja: '日本語' }
const langs = {
    clipboardok: {
        zh: '已复制到剪贴板',
        en: 'Copy to clipboard',
        ja: 'クリップボードにコピーされました'
    },
    homepage: {
        zh: '官方网站',
        en: 'HomePage',
        ja: '公式サイト'

    },
    downloadlink: {
        zh: '软件下载',
        en: 'Download',
        ja: 'ダウンロード'
    },
    vediotutorial: {
        zh: '视频教学',
        en: 'Vedio Tutorial',
        ja: 'ビデオチュー'
    },
    contactme: {
        zh: 'QQ群963119821',
        en: 'Discord',
        ja: 'Discord'
    },
    bit64link: {
        zh: '64位',
        en: '64-bit',
        ja: '64ビット'
    },
    bit32link: {
        zh: '32位',
        en: '32-bit',
        ja: '32ビット'
    },
}

const languagelinks = {
    contactme: {
        zh: 'https://qm.qq.com/q/I5rr3uEpi2',
        en: 'https://discord.com/invite/ErtDwVeAbB',
        ja: 'https://discord.com/invite/ErtDwVeAbB',
    },
    vediotutorial: {
        zh: 'https://space.bilibili.com/592120404/video',
        en: 'https://www.youtube.com/results?search_query=LunaTranslator',
        ja: 'https://www.youtube.com/results?search_query=LunaTranslator',
    }
}
window.$docsify = {
    // homepage: '/redirect.html',
    requestHeaders: {
        'cache-control': 'max-age=0, no-store, no-cache, must-revalidate',
    },
    notFoundPage: 'redirect.html',
    pagination: {
        previousText: '上一节',
        nextText: '下一节',
        crossChapter: true,
        crossChapterText: true,
    },
    repo: 'https://github.com/HIllya51/LunaTranslator',

    alias: {
        '/zh/_sidebar.md': '/zh/sidebar.md',
        '/en/_sidebar.md': '/en/sidebar.md',
        '/ja/_sidebar.md': '/ja/sidebar.md',
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
        function (hook, vm) {
            hook.doneEach(() => {
                if (document.getElementById('manytables') == null) return
                import('/manyapis.js')
            })
        },
        function (hook, vm) {
            hook.doneEach(() => {
                if (!window.location.hostname.startsWith('docs')) return
                let replacetarget = window.location.protocol + '//image.' + window.location.hostname.substring(5);
                var images = document.getElementsByTagName('img');

                for (var i = 0; i < images.length; i++) {

                    images[i].src = images[i].src.replace('https://image.lunatranslator.org', replacetarget)
                }
            })
        },
        function (hook, vm) {
            hook.doneEach(() => {
                var elements = document.querySelectorAll('code');
                elements.forEach(function (element) {
                    if (!(window.location.href.endsWith('guochandamoxing') || window.location.href.endsWith('baipiaojiekou'))) return
                    element.addEventListener('click', function () {
                        copyToClipboard(element.innerText)
                    });
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

for (let lang in supportlangs) {
    console.log(lang)
    let a = document.createElement('a')
    a.classList.add('goodlink')
    a.classList.add('buttonsize')
    a.innerText = supportlangs[lang]
    a.addEventListener('click', function () {
        switchlang(lang)
    })
    document.getElementById('languageswitch').appendChild(a)
}
function getcurrlang(url) {
    for (let key in supportlangs) {
        if (url.includes(`/${key}/`)) {
            return key
        }
    }
    return ''
}
function switchlang(lang) {
    window.location.href = window.location.href.replace('/' + currentlang + '/', '/' + lang + '/')
}
function browserlang() {
    let l = navigator.language
    if (l.includes('-')) l = l.split('-')[0]
    if (supportlangs[l]) return l
    return 'en'
}
const titleids = ['homepage', 'downloadlink', 'vediotutorial', 'contactme', 'bit64link', 'bit32link']


window.onpopstate = function (event) {

    let url = window.location.href;
    if (url.endsWith('.redirect')) {
        window.location.href = url.substring(0, url.length - 9);
        return
    }
    if (url.endsWith('/#/')) {
        let lang = window.localStorage.currentlang ? window.localStorage.currentlang : browserlang()
        window.location.href += lang + '/'
        return
    }
    for (let key in supportlangs) {
        if (url.endsWith(`/${key}/`)) {
            window.location.href += 'README'
            return
        }
    }
    let thislang = getcurrlang(url)
    window.localStorage.currentlang = thislang
    if (thislang != currentlang) {
        currentlang = thislang
        titleids.forEach(key => {
            document.getElementById(key).innerText = langs[key][currentlang]
        });
    }
    document.getElementById('homepage').href = window.location.protocol + '//' + window.location.hostname.substring(5)
    for (let _id in languagelinks) {
        document.getElementById(_id).href = languagelinks[_id][currentlang]
    }
};

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function () {
        showToast(langs.clipboardok[currentlang] + '\n' + text);
    });
}
showtoastsig = null
function showToast(message) {
    var toast = document.getElementById("clickcopytoast");
    toast.style.display = "block";
    toast.innerHTML = message;
    let thissig = Math.random()
    showtoastsig = thissig
    setTimeout(function () {
        if (showtoastsig == thissig)
            toast.style.display = "none";
    }, 3000);
} 