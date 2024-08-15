from myutils.config import savehook_new_data, globalconfig
import gobject, re, functools
from qtsymbols import *
from gui.usefulwidget import threebuttons, TableViewW
from myutils.wrapper import Singleton_close
from myutils.utils import postusewhich
from gui.dynalang import LDialog, LPushButton, LStandardItemModel
from myutils.config import uid2gamepath
from myutils.hwnd import getExeIcon


@Singleton_close
class noundictconfigdialog_private(LDialog):
    def closeEvent(self, a0: QCloseEvent) -> None:
        self.button.setFocus()
        self.apply()

    def apply(self):
        # self.table.dedumpmodel(0)
        rows = self.model.rowCount()
        self.configdict.clear()

        for row in range(rows):
            k, v = self.model.item(row, 0).text(), self.model.item(row, 1).text()

            self.configdict.append([k, v])

    def __init__(
        self, parent, configdict, title, label=["原文", "翻译"], _=None
    ) -> None:
        super().__init__(parent, Qt.WindowType.WindowCloseButtonHint)

        self.setWindowTitle(title)
        # self.setWindowModality(Qt.ApplicationModal)

        formLayout = QVBoxLayout(self)  # 配置layout

        model = LStandardItemModel(len(configdict), 1, self)
        row = 0
        for key in configdict:  # 2
            item = QStandardItem(key[0])
            model.setItem(row, 0, item)
            item = QStandardItem(key[1])
            model.setItem(row, 1, item)
            row += 1
        model.setHorizontalHeaderLabels(label)
        table = TableViewW(self)
        table.setModel(model)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setsimplemenu()
        button = threebuttons(texts=["添加行", "删除行", "上移", "下移", "立即应用"])
        self.table = table
        button.btn1clicked.connect(table.insertplainrow)
        button.btn2clicked.connect(table.removeselectedrows)
        button.btn3clicked.connect(functools.partial(table.moverank, -1))
        button.btn4clicked.connect(functools.partial(table.moverank, 1))
        button.btn5clicked.connect(self.apply)

        search = QHBoxLayout()
        searchcontent = QLineEdit()
        search.addWidget(searchcontent)
        button4 = LPushButton("搜索")

        def clicked4():
            text = searchcontent.text()

            rows = model.rowCount()
            cols = model.columnCount()
            for row in range(rows):
                ishide = True
                for c in range(cols):
                    if text in model.item(row, c).text():
                        ishide = False
                        break
                table.setRowHidden(row, ishide)

        button4.clicked.connect(clicked4)
        search.addWidget(button4)

        formLayout.addWidget(table)
        formLayout.addLayout(search)
        formLayout.addWidget(button)
        self.button = button
        self.model = model
        self.configdict = configdict
        self.resize(QSize(600, 400))
        self.show()

    def copysetmd5(self):
        if len(self.table.selectedIndexes()) == 0:
            return
        row = self.table.selectedIndexes()[0].row()
        skip = []
        for index in self.table.selectedIndexes():
            if index.row() in skip:
                continue
            skip.append(index.row())
            self.model.insertRow(
                row,
                [
                    QStandardItem(self.model.item(index.row(), 1).text()),
                    QStandardItem(self.model.item(index.row(), 2).text()),
                ],
            )


class Process:
    def __init__(self) -> None:
        self.cachemd5 = {}

    @staticmethod
    def get_setting_window_gameprivate(parent_window, gameuid):
        return noundictconfigdialog_private(
            parent_window,
            savehook_new_data[gameuid]["noundictconfig"],
            "专有名词翻译_占位符_-_" + savehook_new_data[gameuid]["title"],
        ).setWindowIcon(getExeIcon(uid2gamepath[gameuid], cache=True))

    @staticmethod
    def get_setting_window(parent_window):
        return (
            noundictconfigdialog_private(
                parent_window,
                globalconfig["noundictconfig"],
                "专有名词翻译_占位符_设置",
            ),
        )

    @property
    def using_X(self):
        return postusewhich("noundict") != 0

    def usewhich(self) -> dict:
        which = postusewhich("noundict")
        if which == 1:
            return globalconfig["noundictconfig"]
        elif which == 2:
            gameuid = gobject.baseobject.textsource.gameuid
            return savehook_new_data[gameuid]["noundictconfig"]
        elif which == 3:
            gameuid = gobject.baseobject.textsource.gameuid
            return (
                savehook_new_data[gameuid]["noundictconfig"]
                + globalconfig["noundictconfig"]
            )

    def process_before(self, content):
        def __createfake():
            ___idx = 1
            if ___idx == 1:
                xx = "ZX{}Z".format(chr(ord("B") + gobject.baseobject.zhanweifu))
            elif ___idx == 2:
                xx = "{{{}}}".format(gobject.baseobject.zhanweifu)
            elif ___idx == 3:
                xx = v
            gobject.baseobject.zhanweifu += 1
            return xx

        mp1 = {}
        dic = self.usewhich()

        for k, v in dic:
            if not k:
                continue
            xx = __createfake()
            content = content.replace(k, xx)
            mp1[xx] = v
        return content, mp1

    def process_after(self, res, mp1):
        for key in mp1:
            reg = re.compile(re.escape(key), re.IGNORECASE)
            res = reg.sub(mp1[key], res)
        return res
