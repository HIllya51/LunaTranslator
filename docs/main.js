
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
const navitexts = {
    zh: {
        homepage: '官方网站',
        downloadlink: '软件下载',
        vediotutorial: '视频教学',
        contactme: 'QQ群963119821',
        bit64link: '64位',
        bit32link: '32位'

    },
    ru: {
        homepage: 'HomePage',
        downloadlink: 'Download',
        vediotutorial: 'Vedio Tutorial',
        contactme: 'Discord',
        bit64link: '64-bit',
        bit32link: '32-bit'
    },
    en: {
        homepage: 'HomePage',
        downloadlink: 'Download',
        vediotutorial: 'Vedio Tutorial',
        contactme: 'Discord',
        bit64link: '64-bit',
        bit32link: '32-bit'
    }
}
const languagelinks = {
    contactme: {
        zh: 'https://qm.qq.com/q/I5rr3uEpi2',
        ru: 'https://discord.com/invite/ErtDwVeAbB',
        en: 'https://discord.com/invite/ErtDwVeAbB',
    },
    vediotutorial: {
        zh: 'https://space.bilibili.com/592120404/video',
        ru: 'https://www.youtube.com/results?search_query=LunaTranslator',
        en: 'https://www.youtube.com/results?search_query=LunaTranslator',
    },
    homepage: {
        zh: window.location.protocol + '//' + window.location.hostname.substring(5)
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
function browserlang() {
    let l = navigator.language
    if (l.includes('-')) l = l.split('-')[0]
    if (navitexts[l]) return l
    return 'en'
}
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

    for (let _id in languagelinks) {
        let link = languagelinks[_id][currentlang]
        if (link === undefined)
            link = languagelinks[_id].zh
        document.getElementById(_id).href = link
    }
};

function copyToClipboard(text) {
    let url = window.location.href;
    let thislang = getcurrlang(url)
    const langs = {
        zh: {
            ok: '已复制到剪贴板',
            fail: '无法复制:',
        },
        en: {
            ok: 'Copy to clipboard',
            fail: 'Cannot copy:',
        },
        ru: {
            ok: 'Копировать в буфер обмена',
            fail: 'Невозможно скопировать:',
        },
    }

    navigator.clipboard.writeText(text).then(function () {
        showToast(langs[thislang].ok + '\n' + text);
    }, function (err) {
        showToast(langs[thislang].fail + err);
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