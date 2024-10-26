import requests
from urllib.parse import quote
import re, threading
from cishu.cishubase import cishubase
from myutils.utils import get_element_by, simplehtmlparser_all


class jisho(cishubase):

    def generatehtml_tabswitch(self, allres):
        btns = []
        contents = []
        idx = 0
        for title, res in allres:
            idx += 1
            btns.append(
                f"""<button type="button" onclick="onclickbtn_xxxxxx_internal('buttonid_xxxxx_internal{idx}')" id="buttonid_xxxxx_internal{idx}" class="tab-button_xxxx_internal" data-tab="tab_xxxxx_internal{idx}">{title}</button>"""
            )
            contents.append(
                f"""<div id="tab_xxxxx_internal{idx}" class="tab-pane_xxxxx_internal">{res}</div>"""
            )
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
    padding: 10px 20px;
    background-color: #cccccccc;
    border: none;
    cursor: pointer;
    display: inline-block;
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

        res = f"""
    {commonstyle}
<div class="tab-widget_xxxxxx_internal">

    <div class="centerdiv_xxxxxx_internal"><div>
        {''.join(btns)}
    </div>
    </div>
    <div>
        <div class="tab-content_xxxxxx_internal">
            {''.join(contents)}
        </div>
    </div>
</div>
<script>
if(document.querySelectorAll('.tab-widget_xxxxxx_internal .tab-button_xxxx_internal').length)
document.querySelectorAll('.tab-widget_xxxxxx_internal .tab-button_xxxx_internal')[0].click()
</script>
"""
        return res

    def paradown(self, word, key, saver):

        link = "https://jisho.org/{}/{}".format(key, quote(word))
        url = link
        html = requests.get(
            url,
            proxies=self.proxy,
        ).text

        if get_element_by("id", "no-matches", html):
            return
        res = get_element_by("id", "page_container", html)
        if res is None:
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
            stl = requests.get(ss.group()[6:-1], proxies=self.proxy).text
            saver["style"] = stl
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
            ts.append(threading.Thread(target=self.paradown, args=(word, key, saver)))
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
        return "<style>{}</style>".format(
            saver.get("style", "")
        ) + self.generatehtml_tabswitch(res)
