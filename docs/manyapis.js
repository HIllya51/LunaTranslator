
function parsevalue(text) {
    if (text == 'undefined') return -1;
    if (text == '') return -1;
    if (text == '✓') return 5;
    if (text == '✗') return 3;

    return parseFloat(text)
}
function sortTable(table, n) {
    var rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;

    switching = true;
    dir = "asc";
    while (switching) {
        switching = false;
        rows = table.rows;
        for (i = 1; i < (rows.length - 1); i++) {
            shouldSwitch = false;
            x = rows[i].getElementsByTagName("TD")[n];
            y = rows[i + 1].getElementsByTagName("TD")[n];
            if (dir == "asc") {
                if (parsevalue(x.innerText) > parsevalue(y.innerText)) {
                    shouldSwitch = true;
                    break;
                }
            } else if (dir == "desc") {
                if (parsevalue(x.innerText) < parsevalue(y.innerText)) {
                    shouldSwitch = true;
                    break;
                }
            }
        }
        if (shouldSwitch) {
            rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
            switching = true;
            switchcount++;
        } else {
            if (switchcount == 0 && dir == "asc") {
                dir = "desc";
                switching = true;
            }
        }
    }
}
const manytables = [
    {
        name: 'LLM翻译',
        titles: [
            { type: 'isfree', name: '免费' },
            // { type: 'effect', name: '效果' },
            { type: 'freetoken', name: '试用token' },
        ],
        rankdatas: [
            { type: 'DeepSeek', isfree: false, freetoken: 5000000 },
            { type: '阿里云百炼大模型', isfree: false },
            { type: '字节跳动豆包大模型', isfree: false },
            { type: '月之暗面', isfree: false },
            { type: '智谱AI', isfree: false },
            { type: '零一万物', isfree: false },
            { type: '硅基流动', isfree: false },
            { type: '讯飞星火大模型', isfree: false },
            { type: '腾讯混元大模型', isfree: false },
            { type: '百度千帆大模型', isfree: false },
            { type: 'gemini', isfree: true },
            { type: 'Sakura大模型', isfree: true },
            { type: 'ChatGPT', isfree: true },
            { type: 'claude', isfree: false },
            { type: 'cohere', isfree: false },
        ]
    },
    {
        name: 'OCR',
        titles: [
            { type: 'isoffline', name: '离线' },
            { type: 'isfree', name: '免费' },
            { type: 'istrial', name: '可试用' },
            { type: 'price', name: '价格' },
            { type: 'effect', name: '效果' },
        ],
        rankdatas: [
            { type: '本地OCR', isoffline: true, isfree: true, effect: 3 },
            { type: 'WeChat/QQ OCR', isoffline: true, isfree: true, effect: 3.5 },
            { type: 'WindowsOCR', isoffline: true, isfree: true, effect: 2.8 },
            { type: 'Tesseract5', isoffline: true, isfree: true, effect: 1.5 },
            { type: 'manga-ocr', isoffline: true, isfree: true, effect: 3.6 },
            { type: 'Google Lens', isoffline: false, isfree: true, effect: 4 },
            { type: 'GeminiOCR', isoffline: false, isfree: false, effect: 5, istrial: false, price: 5 },
            { type: 'Google Cloud Vision', isoffline: false, isfree: false, effect: 5, istrial: false },
            { type: '百度OCR', isoffline: false, isfree: false, istrial: false },
            { type: '百度图片翻译', isoffline: false, isfree: false, istrial: false },
            { type: '腾讯OCR', isoffline: false, isfree: false, istrial: false },
            { type: '腾讯图片翻译', isoffline: false, isfree: false, istrial: false },
            { type: '飞书OCR', isoffline: false, isfree: true },
            { type: 'ocrspace', isoffline: false, isfree: false, istrial: false },
            { type: 'docsumo', isoffline: false, isfree: false, istrial: false },
            { type: '有道OCR', isoffline: false, isfree: false, istrial: true },
            { type: '有道图片翻译', isoffline: false, isfree: false, istrial: true },
            { type: '火山OCR', isoffline: false, isfree: false, istrial: false },
            { type: '讯飞OCR', isoffline: false, isfree: false, istrial: false },
            { type: '有道词典', isoffline: false, isfree: true },
        ]
    }
];

manytables.forEach((atable) => {
    var ele_manytables = document.getElementById('manytables')
    var centertable = document.createElement('div')
    centertable.classList.add('centertable')
    var table = document.createElement('table')
    centertable.appendChild(table)
    table.classList.add('manytables')
    ele_manytables.appendChild(centertable)
    var header = document.createElement('tr')
    table.appendChild(header)
    var tablename = document.createElement('th')
    var div = document.createElement('div')
    tablename.appendChild(div)
    div.classList.add('manytables2')
    div.innerText = atable.name
    header.appendChild(tablename)
    atable.titles.forEach((title, idx) => {
        var th = document.createElement('th')
        var div = document.createElement('div')
        th.appendChild(div)
        div.innerText = title.name
        div.addEventListener('click', function () { sortTable(table, idx + 1) })
        div.classList.add('clickable')
        div.classList.add('manytables2')
        header.appendChild(th)
    })

    atable.rankdatas.forEach(item => {
        var tr = document.createElement('tr')
        table.appendChild(tr)
        var td = document.createElement('td')
        tr.appendChild(td)
        td.innerText = item.type
        td.classList.add('manytables2')
        atable.titles.forEach((title, idx) => {
            var td = document.createElement('td')
            td.classList.add('manytables2')
            tr.appendChild(td)
            if (item[title.type] === true)
                td.innerText = '✓'
            else if (item[title.type] === false)
                td.innerText = ''//'✗'
            else if (item[title.type] === undefined)
                td.innerText = ''
            else
                td.innerText = item[title.type]
        })
    })
})
