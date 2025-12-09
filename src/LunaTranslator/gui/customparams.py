from qtsymbols import *
import functools, json
from myutils.wrapper import tryprint
from gui.usefulwidget import (
    getIconButton,
    VisGridLayout,
    SuperCombo,
    FocusDoubleSpin,
    FocusSpin,
    MySwitch,
)


class typeswitcheditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cacheswitchtypevalue = {}
        self.t = None
        self.l = QHBoxLayout(self)
        self.l.setContentsMargins(0, 0, 0, 0)
        self.w: "FocusDoubleSpin|FocusSpin|QLineEdit|MySwitch|QPlainTextEdit" = None

    def gettype(self):
        return self.t

    @tryprint
    def settype(self, t):
        if self.w:
            self.cacheswitchtypevalue[self.t] = self.getvalue()
            self.w.deleteLater()
        self.t = t
        if t == "int":
            self.w = FocusSpin()
            self.w.setMaximum(0x7FFFFFFF)
            self.w.setMinimum(-0x7FFFFFFF)
        elif t == "number":
            self.w = FocusDoubleSpin()
            self.w.setMaximum(0x7FFFFFFF)
            self.w.setMinimum(-0x7FFFFFFF)
        elif t == "bool":
            self.w = MySwitch()
        elif t == "other":
            self.w = QPlainTextEdit()
        else:
            self.w = QLineEdit()
        self.l.addWidget(self.w)
        self.setvalue(self.cacheswitchtypevalue.get(self.t))

    @tryprint
    def setvalue(self, v):
        if not self.w:
            return
        if v is None:
            return
        if self.t == "int":
            self.w.setValue(v)
        elif self.t == "number":
            self.w.setValue(v)
        elif self.t == "bool":
            self.w.setChecked(v)
        elif self.t == "other":
            self.w.setPlainText(v)
        else:
            self.w.setText(v)

    @tryprint
    def getvalue(self):
        if not self.w:
            return
        if self.t == "int":
            return self.w.value()
        elif self.t == "number":
            return self.w.value()
        elif self.t == "bool":
            return self.w.isChecked()
        elif self.t == "other":
            return self.w.toPlainText()
        else:
            return self.w.text()


class customparams(QWidget):
    def createline(self, lay: VisGridLayout, i, d: dict):
        k = d.get("key", "")
        v = d.get("value")
        t_ = d.get("type", "string" if self.stringonly else "number")
        self.ks.insert(i, QLineEdit(k))
        ts = typeswitcheditor()
        ts.settype(t_)
        ts.setvalue(v)
        self.vs.insert(i, ts)
        lb = QLabel(":")
        icon = getIconButton(icon="fa.times")

        def __(ts: typeswitcheditor, t: SuperCombo):
            ts.settype(t.getCurrentData())

        if not self.stringonly:
            vs = ["字符串", "数值", "整数", "布尔", "json/python", "Header"]
            vvs = ["string", "number", "int", "bool", "other", "header"]
            if not self.needheader:
                vs.pop(-1)
                vvs.pop(-1)
            t = SuperCombo()
            t.addItems(items=vs, internals=vvs)

            t.setCurrentData(t_)
            t.currentIndexChanged.connect(functools.partial(__, ts, t))
            ws = (self.ks[i], lb, self.vs[i], t, icon)
        else:
            ws = (self.ks[i], lb, self.vs[i], icon)
        for j in range(len(ws)):
            lay.addWidget(ws[j], i, j)
        icon.clicked.connect(functools.partial(lay.setRowVisible, i, False))

    def addline(self, lay: VisGridLayout, btn):
        lay.addWidget(btn, lay.rowCount(), 0, 1, 5 - self.stringonly)
        self.createline(lay, lay.rowCount() - 2, {})

    def __init__(self, dd: dict, key="customparams", stringonly=False, needheader=True):
        super().__init__()
        self.needheader = needheader
        self.stringonly = stringonly
        self.ks: "list[QLineEdit]" = []
        self.vs: "list[typeswitcheditor]" = []
        lay = VisGridLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        self.lay = lay
        value: list = dd[key]
        for i, d in enumerate(value):
            self.createline(lay, i, d)
        icon = getIconButton(icon="fa.plus", fix=False)
        lay.addWidget(icon, len(value), 0, 1, 5 - self.stringonly)
        icon.clicked.connect(functools.partial(self.addline, lay, icon))

    def updateValues(self):
        collect = []
        for i in range(len(self.ks)):
            if not self.lay.rowVisible(i):
                continue
            k = self.ks[i].text()
            v = self.vs[i].getvalue()
            t = self.vs[i].gettype()
            if not k:
                continue
            collect.append(dict(key=k, value=v, type=t))
        return dict(customparams=collect)


def getcustombodyheaders(customparams: "list[dict]", **kw):
    extrabody = {}
    extraheader = {}
    for other in customparams if customparams else []:
        k = other.get("key")
        v = other.get("value")
        t = other.get("type")
        if t == "header":
            extraheader[k] = v
        else:
            if t == "number":
                try:
                    v = float(v)
                except:
                    continue
            elif t == "int":
                try:
                    v = int(v)
                except:
                    continue
            elif t == "bool":
                try:
                    v = bool(v)
                except:
                    continue
            elif t == "other":
                try:
                    v = json.loads(v)
                except:
                    try:
                        v = eval(v, kw)
                    except:
                        from traceback import print_exc

                        print_exc()
                        continue
            extrabody[k] = v
    return extrabody, extraheader
