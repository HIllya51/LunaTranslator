import re, threading
from cishu.cishubase import cishubase
from myutils.utils import get_element_by, simplehtmlparser_all, localcachehelper


class jisho(cishubase):
    backgroundparser = "document.querySelectorAll('.lunajishocsswrapper').forEach((ele) => { ele.style.backgroundColor = {color} });"

    def init(self):
        self.style = localcachehelper("cishucss/jisho")
        self.klass = "lunajishocsswrapper"

    def generatehtml_tabswitch(self, allres):
        btns = []
        contents = []
        idx = 0
        for title, res in allres:
            btns.append(
                """<button type="button" onclick="onclickbtn_xxxxxx_internal('buttonid_xxxxx_internal{idx}')" id="buttonid_xxxxx_internal{idx}" class="tab-button_xxxx_internal{klass}" data-tab="tab_xxxxx_internal{idx}">{title}</button>""".format(
                    idx=idx, title=title, klass="" if idx != 0 else " active"
                )
            )
            contents.append(
                """<div id="tab_xxxxx_internal{idx}" class="tab-pane_xxxxx_internal{klass}">{res}</div>""".format(
                    idx=idx, res=res, klass="" if idx != 0 else " active"
                )
            )
            idx += 1
        commonstyle = """
<script>
function onclickbtn_xxxxxx_internal(_id) {
    tabPanes = document.querySelectorAll('.tab-widget_xxxxxx_internal .tab-pane_xxxxx_internal');
    tabButtons = document.querySelectorAll('.tab-widget_xxxxxx_internal .tab-button_xxxx_internal');
        for (i = 0; i < tabButtons.length; i++)
            tabButtons[i].classList.remove('active');
        for (i = 0; i < tabPanes.length; i++)
            tabPanes[i].classList.remove('active');

        document.getElementById(_id).classList.add('active');

        tabId = document.getElementById(_id).getAttribute('data-tab');
        tabPane = document.getElementById(tabId);
        tabPane.classList.add('active');
    }
</script>
<style>
.centerdiv_xxxxxx_internal {
    display: flex;
    justify-content: center;
}
.tab-widget_xxxxxx_internal .tab-button_xxxxxx_internals_xxxxxx_internal {
    display: flex;
}

.tab-widget_xxxxxx_internal .tab-button_xxxx_internal {
    padding: 7px 15px;
    background-color: #cccccccc;
    border: none;
    cursor: pointer;
    display: inline-block;
    line-height: 20px;
}

.tab-widget_xxxxxx_internal .tab-button_xxxx_internal.active {
    background-color: #cccccc44;
}

.tab-widget_xxxxxx_internal .tab-content_xxxxxx_internal .tab-pane_xxxxx_internal {
    display: none;
}

.tab-widget_xxxxxx_internal .tab-content_xxxxxx_internal .tab-pane_xxxxx_internal.active {
    display: block;
}
</style>
"""

        res = """
    {commonstyle}
<div class="tab-widget_xxxxxx_internal">

    <div class="centerdiv_xxxxxx_internal"><div>
        {btns}
    </div>
    </div>
    <div>
        <div class="tab-content_xxxxxx_internal">
            {contents}
        </div>
    </div>
</div>
""".format(
            commonstyle=commonstyle, btns="".join(btns), contents="".join(contents)
        )
        res = res.replace('href="/', 'href="https://jisho.org/')
        res = res.replace('src="/', 'src="https://jisho.org/')
        return res

    def paradown(self, word, key, saver):

        link = "https://jisho.org/{}/{}".format(key, word)
        url = link
        html = self.proxysession.get(url).text

        if get_element_by("id", "no-matches", html):
            return
        res = get_element_by("id", "page_container", html)
        if not res:
            return
        res = (
            res.replace('href="//', 'href="https://')
            .replace("<h3>Discussions</h3>", "")
            .replace(
                '<a href="#" class="signin">Log in</a> to talk about this word.', ""
            )
            .replace(get_element_by("id", "other_dictionaries", html), "")
        )
        for link in simplehtmlparser_all(
            res, "a", '<a class="concept_audio concept_light-status_link"'
        ):
            res = res.replace(link, "")
        for link in simplehtmlparser_all(
            res, "a", '<a class="concept_light-status_link"'
        ):
            res = res.replace(link, "")
        for link in simplehtmlparser_all(res, "a", '<a href="#"'):
            res = res.replace(link, "")

        if key == "search":
            ss = re.search(
                'href="https://assets.jisho.org/assets/application(.*)"', html
            )
            link = ss.group()[6:-1]
            if not self.style.get(link):
                self.style[link] = self.parse_stylesheet(
                    self.proxysession.get(link).text, self.klass
                )
            saver["style"] = self.style[link]
            saver["primary"] = get_element_by("id", "result_area", res) + res.replace(
                get_element_by("id", "main_results", res),
                get_element_by("id", "primary", res),
            )
            saver["secondary"] = res.replace(
                get_element_by("id", "main_results", res),
                get_element_by("id", "secondary", res),
            )
        else:
            saver[key] = res

    def search(self, word):

        ts = []
        saver = {}
        for key in ("word", "search"):
            ts.append(threading.Thread(target=self.paradown, args=(word, key, saver), daemon=True))
            ts[-1].start()
        for t in ts:
            t.join()
        res = []
        if saver.get("word"):
            res.append(("Word", saver["word"]))
        if saver.get("primary"):
            res.append(("Words", saver["primary"]))
        if saver.get("secondary"):
            res.append(("Others", saver["secondary"]))
        if not res:
            return
        return '<style>{}</style><div class="{}">{}</div>'.format(
            saver.get("style", ""), self.klass, self.generatehtml_tabswitch(res)
        )
