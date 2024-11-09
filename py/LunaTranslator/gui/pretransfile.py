from qtsymbols import *
import sqlite3, os, json, functools
from traceback import print_exc
from myutils.config import globalconfig, _TR
from myutils.utils import autosql, getannotatedapiname
from gui.usefulwidget import getQMessageBox, SuperCombo
from gui.dynalang import LFormLayout, LPushButton, LDialog
from textsource.texthook import splitembedlines
from collections import Counter
from myutils.wrapper import tryprint


@tryprint
def sqlite2json2(
    self, sqlitefile, targetjson=None, existsmerge=False, isforembed=False
):
    try:
        sql = autosql(sqlite3.connect(sqlitefile, check_same_thread=False))
        ret = sql.execute("SELECT * FROM artificialtrans  ").fetchall()
        js_format2 = {}
        collect = []
        for _aret in ret:
            if len(_aret) == 4:
                _id, source, mt, source_origin = _aret
                if targetjson:
                    source = source_origin
                js_format2[source] = mt
            elif len(_aret) == 3:
                _id, source, mt = _aret
                js_format2[source] = mt
            try:
                mtjs = json.loads(mt)
            except:
                mtjs = mt
            js_format2[source] = mtjs

            collect.extend(list(mtjs.keys()))
    except:
        print_exc()
        getQMessageBox(self, "错误", "所选文件格式错误！")
        return
    _collect = []
    for _, __ in Counter(collect).most_common():
        if _ in globalconfig["fanyi"]:
            _collect.append(_)
    dialog = LDialog(self, Qt.WindowType.WindowCloseButtonHint)  # 自定义一个dialog
    dialog.setWindowTitle("导出翻译记录为json文件")
    dialog.resize(QSize(800, 10))
    formLayout = LFormLayout(dialog)  # 配置layout
    dialog.setLayout(formLayout)

    combo = SuperCombo()
    combo.addItems([getannotatedapiname(_) for _ in _collect], _collect)

    formLayout.addRow("首选翻译", combo)
    e = QLineEdit(sqlitefile[: -(len(".sqlite"))])

    bu = LPushButton("选择路径")

    def __selectsavepath():
        ff = QFileDialog.getSaveFileName(
            dialog, directory=sqlitefile[: -(len(".sqlite"))]
        )
        if ff[0] == "":
            return
        e.setText(ff[0])

    bu.clicked.connect(__selectsavepath)
    hori = QHBoxLayout()
    hori.addWidget(e)
    hori.addWidget(bu)

    if targetjson is None:
        formLayout.addRow("保存路径", hori)

    button = QDialogButtonBox(
        QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
    )
    formLayout.addRow(button)
    button.rejected.connect(dialog.close)

    def __savefunction(target, existsmerge, isforembed):
        if len(_collect) > 0:
            transkirokuuse = combo.getIndexData(combo.currentIndex())
            for k in js_format2:
                js_format2[k] = js_format2[k].get(transkirokuuse, "")

        if target is None:
            target = e.text() + ".json"
        if existsmerge and os.path.exists(target):
            try:
                with open(target, "r", encoding="utf8") as ff:
                    existsjs = json.load(ff)
            except:
                existsjs = {}
            for k in existsjs:
                if k not in js_format2 or js_format2[k] == "":
                    js_format2[k] = existsjs[k]
        if isforembed:
            for _ in js_format2:
                js_format2[_] = splitembedlines(js_format2[_])
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "w", encoding="utf8") as ff:
            ff.write(
                json.dumps(js_format2, ensure_ascii=False, sort_keys=False, indent=4)
            )
        dialog.close()

    button.accepted.connect(
        functools.partial(__savefunction, targetjson, existsmerge, isforembed)
    )
    button.button(QDialogButtonBox.StandardButton.Ok).setText(_TR("确定"))
    button.button(QDialogButtonBox.StandardButton.Cancel).setText(_TR("取消"))
    dialog.show()


def sqlite2json(self):
    f = QFileDialog.getOpenFileName(directory="translation_record", filter="*.sqlite")
    if f[0] == "":
        return

    sqlite2json2(self, f[0])
