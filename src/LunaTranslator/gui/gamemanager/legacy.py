from qtsymbols import *
import functools, threading
from myutils.config import savehook_new_list, savehook_new_data, get_launchpath
from myutils.hwnd import getExeIcon
from gui.usefulwidget import (
    TableViewW,
    D_getsimpleswitch,
    D_getIconButton,
    getIconButton,
    IconButton,
)
from gui.gamemanager.setting import dialog_setting_game
from gui.dynalang import LPushButton, LStandardItemModel
from gui.gamemanager.common import (
    opendirforgameuid,
    startgamecheck,
    addgamesingle,
    showcountgame,
    addgamebatch_x,
)


class LazyLoadTableView(TableViewW):
    def __init__(self, model: LStandardItemModel) -> None:
        super().__init__()
        self.widgetfunction = []
        self.lock = threading.Lock()
        self.setModel(model)
        self.started = False

    def starttraceir(self):
        self.started = True
        self.model().rowsRemoved.connect(functools.partial(self.insertremove))
        self.model().rowsInserted.connect(functools.partial(self.insert))

    def resizeEvent(self, e):
        self.loadVisibleRows()
        super().resizeEvent(e)

    def insertremove(self, index, start, end):
        off = end - start + 1
        with self.lock:
            collect = []
            for i in range(len(self.widgetfunction)):
                if self.widgetfunction[i][0] > end:
                    self.widgetfunction[i][0] -= off
                elif (
                    self.widgetfunction[i][0] >= start
                    and self.widgetfunction[i][0] <= end
                ):
                    collect.append(i)
            for i in collect:
                self.widgetfunction.pop(i)

        self.loadVisibleRows()

    def insert(self, index, start, end):
        off = end - start + 1
        with self.lock:
            for i in range(len(self.widgetfunction)):
                if self.widgetfunction[i][0] >= start:
                    self.widgetfunction[i][0] += off
                    # print(self.widgetfunction[i])

        self.loadVisibleRows()

    def setIndexWidget(self, index: QModelIndex, widgetf):
        if not self.started:
            self.widgetfunction.append([index.row(), index.column(), widgetf])
            return
        if self.visualRect(index).intersects(self.viewport().rect()):
            w = widgetf()
            super().setIndexWidget(index, w)
        else:
            with self.lock:
                self.widgetfunction.append([index.row(), index.column(), widgetf])

    def scrollContentsBy(self, dx, dy):
        super().scrollContentsBy(dx, dy)
        self.loadVisibleRows()

    def loadVisibleRows(self):
        with self.lock:
            collect = []
            for i, index in enumerate(self.widgetfunction):
                row, col, wf = index
                if self.visualRect(self.model().index(row, col)).intersects(
                    self.viewport().rect()
                ):
                    collect.insert(0, i)

            for i in collect:
                row, col, wf = self.widgetfunction.pop(i)

                w = wf()
                super().setIndexWidget(self.model().index(row, col), w)


class dialog_savedgame_legacy(QWidget):

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        addgamebatch_x(self.addgame, savehook_new_list, files)

    def directshow(self):
        pass

    def showsettingdialog(self, k):
        dialog_setting_game(self, k)

    def clicked2(self):
        try:

            idx = self.table.currentIndex().row()
            savehook_new_list.pop(idx)
            self.savelist.pop(idx)
            self.model.removeRow(self.table.currentIndex().row())
            showcountgame(self.parent_, len(self.savelist))
        except:
            pass

    def addgame(self, uid):
        if uid in self.savelist:
            idx = self.savelist.index(uid)
            self.savelist.pop(idx)
            self.model.removeRow(idx)
        self.newline(0, uid)
        self.table.setCurrentIndex(self.model.index(0, 0))
        showcountgame(self.parent_, len(self.savelist))

    def clicked3(self):
        addgamesingle(self, self.addgame, savehook_new_list)

    def clicked(self):
        startgamecheck(
            self,
            savehook_new_list,
            self.model.item(self.table.currentIndex().row(), 2).savetext,
        )

    def delayloadicon(self, k):
        icon = getExeIcon(get_launchpath(k), cache=True)
        if icon.isNull():
            return
        return getIconButton(functools.partial(opendirforgameuid, k), qicon=icon)

    def callback_leuse(self, k, use):
        if use:
            savehook_new_data[k]["launch_method"] = None
        else:
            savehook_new_data[k]["launch_method"] = "direct"

    def newline(self, row, k):
        keyitem = QStandardItem()
        keyitem.savetext = k
        self.model.insertRow(
            row,
            [
                QStandardItem(),
                QStandardItem(),
                keyitem,
                QStandardItem((savehook_new_data[k]["title"])),
            ],
        )
        self.table.setIndexWidget(
            self.model.index(row, 0),
            D_getsimpleswitch(
                {"1": savehook_new_data[k].get("launch_method") != "direct"},
                "1",
                callback=functools.partial(self.callback_leuse, k),
            ),
        )
        self.table.setIndexWidget(
            self.model.index(row, 1),
            functools.partial(self.delayloadicon, k),
        )

        self.table.setIndexWidget(
            self.model.index(row, 2),
            D_getIconButton(functools.partial(self.showsettingdialog, k)),
        )

    def __init__(self, parent) -> None:
        # if dialog_savedgame._sigleton :
        #         return
        # dialog_savedgame._sigleton=True
        super().__init__(parent)
        self.parent_ = parent
        self.setAcceptDrops(True)
        formLayout = QVBoxLayout(self)  #
        model = LStandardItemModel()
        model.setHorizontalHeaderLabels(["转区", "", "设置", "游戏"])  # ,'HOOK'])

        self.model = model

        table = LazyLoadTableView(model)
        table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        table.horizontalHeader().setStretchLastSection(True)
        # table.setEditTriggers(QAbstractItemView.NoEditTriggers);
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode((QAbstractItemView.SelectionMode.SingleSelection))
        table.setWordWrap(False)
        self.table = table
        self.savelist = []
        for row, k in enumerate(savehook_new_list):  # 2
            self.newline(row, k)
            self.savelist.append(k)

        showcountgame(self.parent_, len(self.savelist))
        self.table.starttraceir()
        bottom = QHBoxLayout()

        button = LPushButton("开始游戏")
        self.button = button
        button.clicked.connect(self.clicked)
        button3 = LPushButton("添加游戏")

        button3.clicked.connect(self.clicked3)
        button2 = LPushButton("删除游戏")

        button2.clicked.connect(self.clicked2)
        bottom.addWidget(button)
        bottom.addWidget(button2)
        bottom.addWidget(button3)
        formLayout.addWidget(IconButton(None))
        formLayout.addWidget(table)
        formLayout.addLayout(bottom)
