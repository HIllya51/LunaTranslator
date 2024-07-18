
window.$docsify = {
    homepage: '/redirect.html',
    requestHeaders: {
        'cache-control': 'max-age=0',
    },

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

    executeScript: true
}



let dropdowns = document.getElementsByClassName('dropdown')
for (let i = 0; i < dropdowns.length; i++) {

    let dropdown = dropdowns[i]
    dropdown.addEventListener('mouseover', function () {
        let dropdownContent = this.querySelector('.dropdown-content');
        dropdownContent.style.display = 'block';
    });
    dropdown.addEventListener('mouseout', function () {
        let dropdownContent = this.querySelector('.dropdown-content');
        dropdownContent.style.display = 'none';
    });
}


function randombg() {
    let list = ['luna2.jpg']// ['luna.jpg', 'luna2.jpg', 'luna3.jpg', 'luna4.jpg'];
    let randomIndex = Math.floor(Math.random() * list.length);
    let selectedItem = list[randomIndex];
    document.querySelector("body > div.backgroud").style.backgroundImage = `url("https://image.lunatranslator.xyz/${selectedItem}")`
}
randombg()
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
window.onpopstate = function (event) {
    let url = window.location.href;
    let thislang = currentlang
    if (url.includes('/zh/')) {
        thislang = 'zh'
    }
    else if (url.includes('/en/')) {
        thislang = 'en'
    }
    else if (url.includes('/ru/')) {
        thislang = 'ru'
    }
    if (thislang != currentlang) {
        currentlang = thislang
        console.log(navitexts[currentlang])

        for (let key in navitexts[currentlang]) {
            document.getElementById(key).innerText = navitexts[currentlang][key]

        }
    }
};