from PyQt5.QtWidgets import QWidget
from qtsymbols import *
from rendertext.somefunctions import dataget
import gobject, uuid, json, importlib, base64, os
from urllib.parse import quote, unquote
from myutils.config import globalconfig
from gui.usefulwidget import WebivewWidget

testsavejs = False


# example
def extrastyle(rootdivid):
    with open(
        r"example.png",
        "rb",
    ) as ff:
        b64 = base64.b64encode(ff.read()).decode("utf-8")

    extra = f"""#{rootdivid}::before
        {{
            background-image: url('data:image/jpeg;base64,{b64}') ;
            background-size: 100% auto;
            opacity: 0.5;
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            z-index: -1;
        }}"""
    return extra


class TextBrowser(QWidget, dataget):
    contentsChanged = pyqtSignal(QSize)

    def resizeEvent(self, event: QResizeEvent):
        self.webivewwidget.resize(event.size().width(), event.size().height())

    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.webivewwidget = WebivewWidget(self)
        self.webivewwidget.set_transparent_background()
        self.webivewwidget.webview.bind("calllunaclickedword", self.calllunaclickedword)
        self.webivewwidget.webview.bind(
            "calllunaheightchange", self.calllunaheightchange
        )
        self.rootdivid = f"luna_{uuid.uuid4()}"
        self.saveiterclasspointer = {}
        self.testeval(
            f"""
            document.write(`<div id="{self.rootdivid}"></div>`);
        """
        )
        self.setglobalstyle(self.rootdivid)

    def testeval(self, js):
        js += ";\n"
        if testsavejs:
            with open("1.js", "a", encoding="utf8") as ff:
                ff.write(js)
        self.webivewwidget.webview.eval(js)

    def setglobalstyle(self, rootdivid):

        if 0:
            extra = extrastyle(rootdivid)
        else:
            if os.path.exists("userconfig/extrastyle.py"):
                extrastyle = importlib.import_module("extrastyle").extrastyle
                extra = extrastyle(rootdivid)
            else:
                extra = ""
        self.testeval(
            f"""
            document.write(`<style>
            body{{
                overflow-y:hidden;
                margin: 0;
                #word-break: break-all;
            }}
            {extra}
            </style>`);
        """
        )

    def setselectable(self, b):
        pass

    def calllunaheightchange(self, h):
        self.contentsChanged.emit(
            QSize(self.width(), int(h * self.webivewwidget.get_ZoomFactor()))
        )

    def internalheighchange(self):
        self.webivewwidget.webview.eval(
            f'calllunaheightchange(document.getElementById("{self.rootdivid}").offsetHeight)'
        )

    def iter_append(self, iter_context_class, origin, atcenter, text, color, cleared):

        if iter_context_class not in self.saveiterclasspointer:
            _id = self.createtextlineid()
            self.saveiterclasspointer[iter_context_class] = _id

        _id = self.saveiterclasspointer[iter_context_class]
        self._webview_append(_id, origin, atcenter, text, [], [], color)

        self.internalheighchange()

    def createtextlineid(self):

        _id = f"luna_{uuid.uuid4()}"
        ptext = f'<div id="{_id}"></div>'
        self.testeval(
            f"""
            document.getElementById("{self.rootdivid}").innerHTML+=`{ptext}`;
        """
        )
        return _id

    def append(self, origin, atcenter, text, tag, flags, color, cleared):

        _id = self.createtextlineid()
        self._webview_append(_id, origin, atcenter, text, tag, flags, color)

    def calllunaclickedword(self, packedwordinfo):
        gobject.baseobject.clickwordcallback(json.loads(unquote(packedwordinfo)), False)

    def gen_html(self, *args):
        currenttype = globalconfig["rendertext_using_internal"]["webview"]
        try:
            __ = importlib.import_module(
                f"rendertext.internal.webview.{currenttype}"
            ).TextLine
        except:
            from traceback import print_exc

            print_exc()
            globalconfig["rendertext_using_internal"]["webview"] = currenttype = list(
                globalconfig["rendertext"]["webview"].keys()
            )[0]
            __ = importlib.import_module(
                f"rendertext.internal.webview.{currenttype}"
            ).TextLine
        return __(currenttype, self.webivewwidget.webview, self).gen_html__(*args)

    def _webview_append(self, _id, origin, atcenter, text, tag, flags, color):
        text = text.replace("\n", "<br>").replace("\\", "\\\\")

        fmori, fsori, boldori = self._getfontinfo(origin)
        fmkana, fskana, boldkana = self._getfontinfo_kana()
        kanacolor = self._getkanacolor()
        if len(tag):
            rb, rb2 = "<ruby>", "</ruby>"
            isshowhira, isshow_fenci, isfenciclick = flags
            if isshowhira:
                rt, rt2 = "<rt>", "</rt>"
            else:
                rt, rt2 = "", ""
            text = rb
            for word in tag:
                if word["orig"] == "\n":
                    text = text + rb2 + "<br>" + rb
                    continue
                if isfenciclick:
                    click = f'''onclick="calllunaclickedword('{quote(json.dumps(word))}')"'''
                else:
                    click = ""
                _maskid = f"luna_{uuid.uuid4()}"
                textori = word["orig"].replace("\\", "\\\\")
                textori = self.gen_html(
                    textori,
                    fmori,
                    fsori,
                    boldori,
                    atcenter,
                    color,
                    globalconfig["extra_space"],
                )
                text += f"""<div {click} id="{_maskid}">""" + textori + "</div>"
                if isshow_fenci:
                    color1 = self._randomcolor(word)
                    _style = f"""
                    <style>#{_maskid}{{
                    background-color: {color1};
                    }}</style>"""
                    text += _style
                if (word["orig"] != word["hira"]) and isshowhira:
                    inner = self.gen_html(
                        word["hira"].replace("\\", "\\\\"),
                        fmkana,
                        fskana,
                        boldkana,
                        True,
                        kanacolor,
                        0,
                    )
                else:
                    inner = ""
                text += rt + inner + rt2
            text = text + rb2
            if atcenter:
                text = f'<div style="text-align: center;">{text}</div>'
        else:
            text = self.gen_html(
                text,
                fmori,
                fsori,
                boldori,
                atcenter,
                color,
                globalconfig["extra_space"],
            )
        self.testeval(f"document.getElementById(`{_id}`).innerHTML=`{text}`")
        self.internalheighchange()

    def clear(self):

        self.testeval(
            f"""
            document.getElementById("{self.rootdivid}").innerHTML="";
        """
        )
        self.saveiterclasspointer.clear()
