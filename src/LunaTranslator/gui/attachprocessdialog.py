from qtsymbols import *
import os
import windows, qtawesome, gobject
from NativeUtils import GetProcessFirstWindow
from myutils.config import globalconfig, _TR
from myutils.wrapper import Singleton
from myutils.hwnd import (
    ListProcess,
    mouseselectwindow,
    getExeIcon,
    test_injectable,
)
from gui.usefulwidget import saveposwindow
from gui.dynalang import LPushButton, LLabel, LCheckBox


@Singleton
class AttachProcessDialog(saveposwindow):

    setcurrentpidpnamesignal = pyqtSignal(int, int)

    def selectwindowcallback(self, pid, hwnd):
        if pid == os.getpid():
            return mouseselectwindow(self.setcurrentpidpnamesignal.emit)
        self.setEnabled(True)
        self.button.setText("点击此按钮后点击游戏窗口"),
        name = windows.GetProcessFileName(pid)
        if not name:
            QMessageBox.critical(
                self, _TR("错误"), _TR("权限不足，请以管理员权限运行！")
            )
            return
        _pids = ListProcess(name)
        self.processEdit.setText(name)
        self.processIdEdit.setText(",".join([str(pid) for pid in _pids]))
        self.windowtext.setText(windows.GetWindowText(hwnd))
        self.processEdit.setCursorPosition(0)
        self.processIdEdit.setCursorPosition(0)
        self.windowtext.setCursorPosition(0)
        self.selectedp = (_pids, name, hwnd)
        self.testifneedadmin()

    def closeEvent(self, e):
        gobject.base.AttachProcessDialog = None
        super().closeEvent(e)

    def __init__(self, parent, callback, hookselectdialog=None):
        super().__init__(
            parent,
            poslist=globalconfig["attachprocessgeo"],
            flags=Qt.WindowType.WindowStaysOnTopHint,
        )
        self.setcurrentpidpnamesignal.connect(self.selectwindowcallback)

        self.iconcache = {}

        self.callback = callback
        self.hookselectdialog = hookselectdialog
        self.selectedp = None
        self.setWindowTitle(
            "选择进程_当前权限_" + ("管理员" if windows.IsUserAnAdmin() else "非管理员")
        )
        self.setWindowIcon(
            qtawesome.icon(globalconfig["toolbutton"]["buttons"]["selectgame"]["icon"])
        )
        w = QWidget()
        self.layout1 = QVBoxLayout(w)
        self.label = LLabel(
            (
                "如果没看见想要附加的进程，可以尝试点击下方按钮后点击游戏窗口,或者尝试使用管理员权限运行本软件"
            )
        )
        self.label.setWordWrap(True)

        class __LPushButton(LPushButton):
            def sizeHint(self):
                size = super().sizeHint()
                return QSize(size.width(), 2 * size.height())

        self.button = __LPushButton("点击此按钮后点击游戏窗口")
        self.button.setCheckable(True)
        self.button.setStyleSheet("font-weight: bold;")
        self.button.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.button.clicked.connect(
            lambda: (
                self.button.setText("请点击游戏窗口"),
                self.setEnabled(False),
                mouseselectwindow(self.setcurrentpidpnamesignal.emit),
            )
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
        self.currentChanged_Ori = self.processList.currentChanged
        self.processList.currentChanged = self.__change
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
        autoopen = LCheckBox("打开选择文本窗口")
        autoopen.setChecked(globalconfig["autoopenselecttext"])
        autoopen.stateChanged.connect(
            lambda x: globalconfig.__setitem__("autoopenselecttext", x)
        )
        bottomlayout.addStretch(1)
        bottomlayout.addWidget(autoopen)
        bottomlayout.addWidget(self.buttonBox)

        self.layout1.addLayout(bottomlayout)
        self.setCentralWidget(w)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.close)
        self.processIdEdit.textEdited.connect(self.editpid)
        self.processIdEdit.setValidator(
            QRegularExpressionValidator(QRegularExpression("([0-9]+,)*"))
        )
        # self.processEdit.setReadOnly(True)
        self.processEdit.textEdited.connect(self.filterproc)

    @property
    def adminicon(self):
        return QApplication.style().standardIcon(QStyle.StandardPixmap.SP_VistaShield)

    def testifneedadmin(self):
        icon = self.adminicon
        pids: "list[int]" = self.selectedp[0]
        btn = self.buttonBox.button(QDialogButtonBox.StandardButton.Ok)
        btn.setIcon(icon if not test_injectable(pids) else QIcon())

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
                if icon.isNull():
                    img = QPixmap(QSize(100, 100))
                    img.fill(Qt.GlobalColor.transparent)
                    icon = QIcon(img)
                self.iconcache[pexe] = icon
            item = QStandardItem(icon, pexe)
            item.setEditable(False)
            self.model.appendRow(item)

    def showEvent(self, e):
        if self.hookselectdialog:
            self.hookselectdialog.realshowhide.emit(False)
        self.refreshfunction()
        return super().showEvent(e)

    def safesplit(self, process):
        try:
            return list(set([int(_) for _ in process.split(",")]))
        except:
            return []

    def editpid(self, process):
        pids = self.safesplit(process)
        if len(pids) == 0:
            self.windowtext.clear()
            self.processEdit.clear()
            return
        self.selectedp = (
            pids,
            windows.GetProcessFileName(pids[0]),
            self.guesshwnd(pids),
        )
        self.testifneedadmin()
        self.windowtext.setText(windows.GetWindowText(self.selectedp[-1]))
        self.processEdit.setText(self.selectedp[1])
        self.windowtext.setCursorPosition(0)
        self.processEdit.setCursorPosition(0)

    def __change(self, index: QModelIndex, __):
        if not (index and index.isValid()):
            return self.currentChanged_Ori(index, __)
        self.processList.scrollTo(index)
        pexe = self.model.itemFromIndex(index).text()
        pids = self.processlist.get(pexe, [])
        self.processEdit.setText(pexe)
        self.processIdEdit.setText(",".join([str(pid) for pid in pids]))
        self.selectedp = pids, pexe, self.guesshwnd(pids)
        self.testifneedadmin()
        self.windowtext.setText(windows.GetWindowText(self.selectedp[-1]))
        self.processEdit.setCursorPosition(0)
        self.processIdEdit.setCursorPosition(0)
        self.windowtext.setCursorPosition(0)
        return self.currentChanged_Ori(index, __)

    def guesshwnd(self, pids):
        for pid in pids:
            hwnd = GetProcessFirstWindow(pid)
            if (hwnd) != 0:
                return hwnd
        return 0

    def accept(self):
        if self.selectedp is None:
            self.close()
        else:
            if self.selectedp[1] is None:
                QMessageBox.critical(
                    self, _TR("错误"), _TR("权限不足，请以管理员权限运行！")
                )
                return
            self.close()
            self.callback(self.selectedp, self.windowtext.text())
