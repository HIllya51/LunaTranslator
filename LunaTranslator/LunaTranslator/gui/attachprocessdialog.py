from qtsymbols import *
import os, functools
import windows, qtawesome, gobject
from winsharedutils import getpidhwndfirst
from myutils.config import globalconfig
from myutils.wrapper import Singleton_close
from myutils.hwnd import (
    getpidexe,
    ListProcess,
    mouseselectwindow,
    getExeIcon,
)
from gui.usefulwidget import saveposwindow, getQMessageBox
from gui.dynalang import LPushButton, LLabel


@Singleton_close
class AttachProcessDialog(saveposwindow):

    setcurrentpidpnamesignal = pyqtSignal(int, int)

    def selectwindowcallback(self, pid, hwnd):
        if pid == os.getpid():
            return
        name = getpidexe(pid)
        _pids = ListProcess(name)
        self.processEdit.setText(name)
        self.processIdEdit.setText(",".join([str(pid) for pid in _pids]))
        self.windowtext.setText(windows.GetWindowText(hwnd))
        self.processEdit.setCursorPosition(0)
        self.processIdEdit.setCursorPosition(0)
        self.windowtext.setCursorPosition(0)
        self.selectedp = (_pids, name, hwnd)

    def closeEvent(self, e):
        gobject.baseobject.AttachProcessDialog = None
        super().closeEvent(e)

    def __init__(self, parent, callback, hookselectdialog=None):
        super().__init__(parent, poslist=globalconfig["attachprocessgeo"])
        self.setcurrentpidpnamesignal.connect(self.selectwindowcallback)

        self.iconcache = {}

        self.callback = callback
        self.hookselectdialog = hookselectdialog
        self.selectedp = None
        self.setWindowTitle(
            "选择进程_当前权限_" + ("管理员" if windows.IsUserAnAdmin() else "非管理员")
        )
        self.setWindowIcon(qtawesome.icon("fa.gear"))
        w = QWidget()
        self.layout1 = QVBoxLayout()
        self.label = LLabel(
            (
                "如果没看见想要附加的进程，可以尝试点击下方按钮后点击游戏窗口,或者尝试使用管理员权限运行本软件"
            )
        )
        self.label.setWordWrap(True)
        self.button = LPushButton("点击此按钮后点击游戏窗口")
        self.button.clicked.connect(
            functools.partial(mouseselectwindow, self.setcurrentpidpnamesignal.emit)
        )
        self.layout1.addWidget(self.label)
        self.layout1.addWidget(self.button)
        self.layout2 = QHBoxLayout()
        self.processIdEdit = QLineEdit()
        self.layout2.addWidget(LLabel(("进程号")))
        self.layout2.addWidget(self.processIdEdit)
        self.processEdit = QLineEdit()
        self.layout3 = QHBoxLayout()
        self.layout3.addWidget(LLabel(("程序名")))
        self.layout3.addWidget(self.processEdit)

        self.windowtext = QLineEdit()
        self.layout2.addWidget(LLabel(("标题")))
        self.layout2.addWidget(self.windowtext)
        self.processList = QListView()
        self.buttonBox = QDialogButtonBox()
        self.buttonBox.setStandardButtons(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.layout1.addLayout(self.layout2)
        self.layout1.addLayout(self.layout3)
        self.layout1.addWidget(self.processList)
        bottomlayout = QHBoxLayout()
        refreshbutton = LPushButton("刷新")
        refreshbutton.clicked.connect(self.refreshfunction)
        bottomlayout.addWidget(refreshbutton)
        bottomlayout.addWidget(self.buttonBox)

        self.layout1.addLayout(bottomlayout)
        w.setLayout(self.layout1)
        self.setCentralWidget(w)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.close)
        self.processList.clicked.connect(self.selectedfunc)
        self.processIdEdit.textEdited.connect(self.editpid)

        # self.processEdit.setReadOnly(True)
        self.processEdit.textEdited.connect(self.filterproc)

    def filterproc(self):
        self.processIdEdit.clear()
        self.windowtext.clear()
        text = self.processEdit.text()
        if len(text) == 0:
            self.refreshfunction()
            return
        for row in range(self.model.rowCount()):
            hide = not (text in self.model.item(row, 0).text())
            self.processList.setRowHidden(row, hide)

    def refreshfunction(self):

        self.windowtext.clear()
        self.processEdit.clear()
        self.processIdEdit.clear()
        self.selectedp = None

        ###########################
        self.model = QStandardItemModel(self.processList)
        self.processlist = ListProcess()
        self.processList.setModel(self.model)
        for pexe in self.processlist:
            if pexe in self.iconcache:
                icon = self.iconcache[pexe]
            else:
                icon = getExeIcon(pexe)
                self.iconcache[pexe] = icon
            item = QStandardItem(icon, pexe)
            item.setEditable(False)
            self.model.appendRow(item)

    def showEvent(self, e):
        if self.hookselectdialog:
            self.hookselectdialog.realshowhide.emit(False)
        self.refreshfunction()

    def safesplit(self, process):
        try:
            return [int(_) for _ in process.split(",")]
        except:
            return []

    def editpid(self, process):
        pids = self.safesplit(process)
        if len(pids) == 0:
            self.windowtext.clear()
            self.processEdit.clear()
            return
        self.selectedp = (pids, getpidexe(pids[0]), self.guesshwnd(pids))
        self.windowtext.setText(windows.GetWindowText(self.selectedp[-1]))
        self.processEdit.setText(self.selectedp[1])
        self.windowtext.setCursorPosition(0)
        self.processEdit.setCursorPosition(0)

    def selectedfunc(self, index: QModelIndex):
        pexe = self.model.itemFromIndex(index).text()
        pids = self.processlist.get(pexe, [])
        self.processEdit.setText(pexe)
        self.processIdEdit.setText(",".join([str(pid) for pid in pids]))
        self.selectedp = pids, pexe, self.guesshwnd(pids)
        self.windowtext.setText(windows.GetWindowText(self.selectedp[-1]))
        self.processEdit.setCursorPosition(0)
        self.processIdEdit.setCursorPosition(0)
        self.windowtext.setCursorPosition(0)

    def guesshwnd(self, pids):
        for pid in pids:
            hwnd = getpidhwndfirst(pid)
            if (hwnd) != 0:
                return hwnd
        return 0

    def accept(self):
        if self.selectedp is None:
            self.close()
        else:
            if self.selectedp[1] is None:
                getQMessageBox(self, "错误", "权限不足，请以管理员权限运行！")
                return
            self.close()
            self.callback(self.selectedp, self.windowtext.text())
