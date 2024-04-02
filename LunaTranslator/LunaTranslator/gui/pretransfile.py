from PyQt5.QtWidgets import (
    QComboBox,
    QPushButton,
    QFormLayout,
    QHBoxLayout,
    QDialogButtonBox,
    QDialog,
    QLineEdit,
    QFileDialog,
)

from PyQt5.QtCore import Qt, QSize
import sqlite3, os
import json
from traceback import print_exc
import functools
from myutils.config import globalconfig, _TR
from myutils.utils import autosql
from gui.usefulwidget import getQMessageBox


def sqlite2json2(self, sqlitefile, targetjson=None, existsmerge=False):
    try:
        sql = autosql(sqlite3.connect(sqlitefile, check_same_thread=False))
        ret = sql.execute("SELECT * FROM artificialtrans  ").fetchall()
        js_format2 = {}
        collect = set()
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

            collect = collect.union(set(mtjs.keys()))
        collect = list(collect)
    except:
        print_exc()
        getQMessageBox(self, "错误", "所选文件格式错误！")
        return
    _collect = []
    for _ in collect:
        if _ in globalconfig["fanyi"]:
            _collect.append(_)
    collect = _collect

    dialog = QDialog(self, Qt.WindowCloseButtonHint)  # 自定义一个dialog
    dialog.setWindowTitle(_TR("导出翻译记录为json文件"))
    dialog.resize(QSize(800, 10))
    formLayout = QFormLayout(dialog)  # 配置layout
    dialog.setLayout(formLayout)

    combo = QComboBox()
    combo.addItems([globalconfig["fanyi"][_]["name"] for _ in collect])

    formLayout.addRow(_TR("首选翻译"), combo)

    e = QLineEdit(sqlitefile[: -(len(".sqlite"))])

    bu = QPushButton(_TR("选择路径"))

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
        formLayout.addRow(_TR("保存路径"), hori)

    button = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
    formLayout.addRow(button)
    button.rejected.connect(dialog.close)

    def __savefunction(target, existsmerge):
        if len(collect) > 0:
            transkirokuuse = collect[combo.currentIndex()]
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

        with open(target, "w", encoding="utf8") as ff:
            ff.write(
                json.dumps(js_format2, ensure_ascii=False, sort_keys=False, indent=4)
            )
        dialog.close()

    button.accepted.connect(functools.partial(__savefunction, targetjson, existsmerge))
    button.button(QDialogButtonBox.Ok).setText(_TR("确定"))
    button.button(QDialogButtonBox.Cancel).setText(_TR("取消"))
    dialog.show()


def sqlite2json(self):
    f = QFileDialog.getOpenFileName(directory="./translation_record", filter="*.sqlite")
    if f[0] == "":
        return

    sqlite2json2(self, f[0])
