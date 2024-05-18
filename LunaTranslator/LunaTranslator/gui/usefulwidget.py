from PyQt5.QtWidgets import (
    QLineEdit,
    QMainWindow,
    QApplication,
    QPushButton,
    QMessageBox,
    QDialog,
    QLabel,
    QSizePolicy,
    QHBoxLayout,
    QWidget,
    QLayout,
)

from webviewpy import (
    webview_native_handle_kind_t,
    Webview,
    declare_library_path,
)
from PyQt5.QtGui import QCloseEvent, QColor, QTextCursor, QResizeEvent
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from myutils.config import _TR, globalconfig
from PyQt5.QtWidgets import (
    QColorDialog,
    QSpinBox,
    QDoubleSpinBox,
    QPushButton,
    QComboBox,
    QLabel,
    QDialogButtonBox,
    QLineEdit,
    QApplication,
    QVBoxLayout,
)
from traceback import print_exc
import qtawesome, functools, threading, time
from myutils.wrapper import Singleton
from winsharedutils import showintab, HTMLBrowser
import windows, os, platform


@Singleton
class dialog_showinfo(QDialog):

    def __init__(self, parent, title, info) -> None:
        super().__init__(parent, Qt.WindowCloseButtonHint)
        self.setWindowTitle(title)
        l = QLabel(info)
        layout = QHBoxLayout()
        layout.addWidget(l)
        self.setLayout(layout)
        self.show()


def getQMessageBox(
    parent=None,
    title="",
    text="",
    useok=True,
    usecancel=False,
    okcallback=None,
    cancelcallback=None,
    tr=True,
):
    msgBox = QMessageBox(parent)
    if tr:
        title, text = _TR(title), _TR(text)
    msgBox.setWindowTitle((title))
    msgBox.setText((text))
    btn = 0
    if useok:
        btn |= QMessageBox.Ok
    if usecancel:
        btn |= QMessageBox.Cancel

    msgBox.setStandardButtons(btn)
    msgBox.setDefaultButton(QMessageBox.Ok)
    ret = msgBox.exec()

    if ret == QMessageBox.Ok and okcallback:
        okcallback()
    elif ret == QMessageBox.Cancel and cancelcallback:
        cancelcallback()


def isinrect(pos, rect):
    x, y = pos.x(), pos.y()
    x1, x2, y1, y2 = rect
    return x >= x1 and x <= x2 and y <= y2 and y >= y1


def makerect(_):
    x, y, w, h = _
    return [x, x + w, y, y + h]


class saveposwindow(QMainWindow):
    def __init__(self, parent, dic=None, key=None, flags=None) -> None:
        if flags:
            super().__init__(parent, flags=flags)
        else:
            super().__init__(parent)
        d = QApplication.primaryScreen()
        self.dic, self.key = dic, key
        if self.dic:
            dic[key][2] = max(0, min(dic[key][2], d.size().width()))
            dic[key][3] = max(0, min(dic[key][3], d.size().height()))
            dic[key][0] = min(max(dic[key][0], 0), d.size().width() - dic[key][2])
            dic[key][1] = min(max(dic[key][1], 0), d.size().height() - dic[key][3])
            self.setGeometry(*dic[key])

    def resizeEvent(self, a0) -> None:
        if self.dic:
            if self.isMaximized() == False:
                self.dic[self.key] = list(self.geometry().getRect())

    def moveEvent(self, a0) -> None:
        if self.dic:
            if self.isMaximized() == False:
                self.dic[self.key] = list(self.geometry().getRect())

    def closeEvent(self, event: QCloseEvent):
        if self.dic:
            if self.isMaximized() == False:
                self.dic[self.key] = list(self.geometry().getRect())


class closeashidewindow(saveposwindow):
    showsignal = pyqtSignal()
    realshowhide = pyqtSignal(bool)

    def __init__(self, parent, dic=None, key=None) -> None:
        super().__init__(parent, dic, key)
        self.showsignal.connect(self.showfunction)
        self.realshowhide.connect(self.realshowhidefunction)
        if globalconfig["showintab_sub"]:
            showintab(int(self.winId()), True)

    def realshowhidefunction(self, show):
        if show:
            self.showNormal()
        else:
            self.hide()

    def showfunction(self):
        if self.isMinimized():
            self.showNormal()
        elif self.isHidden():
            self.show()
        else:
            self.hide()

    def closeEvent(self, event: QCloseEvent):
        self.hide()
        event.ignore()
        super().closeEvent(event)


class MySwitch(QPushButton):
    def __init__(self, parent=None, sign=True, enable=True):
        self.status1 = 0
        self.status2 = 0
        self.colors = [
            "#7f7f7f",
            "#afafaf",
            "#FFa9d4",
            "#FF69B4",
        ]
        self.icons = ["fa.times", "fa.check"]
        super().__init__(parent)

        self.setStyleSheet(
            """background-color: rgba(255, 255, 255, 0);
          color: black;
          border: 0px;
          font: 100 10pt;"""
        )

        self.clicked.connect(self.setChecked)
        self.setIconSize(QSize(25, 25))
        self.setEnabled(enable)
        self.setCheckable(True)
        self.setChecked(sign)

    def setChecked(self, a0):
        super().setChecked(a0)
        self.status1 = a0
        self.setIcon(
            qtawesome.icon(
                self.icons[self.status1],
                color=self.colors[self.status1 * 2 + self.status2],
            )
        )

    def setEnabled(self, a0):
        super().setEnabled(a0)
        self.status2 = a0
        self.setIcon(
            qtawesome.icon(
                self.icons[self.status1],
                color=self.colors[self.status1 * 2 + self.status2],
            )
        )


class resizableframeless(saveposwindow):
    def __init__(self, parent, flags, dic, key) -> None:
        super().__init__(parent, dic, key, flags)
        self.setMouseTracking(True)

        self._padding = 5
        # 设置鼠标跟踪判断扳机默认值
        self._move_drag = False
        self._corner_drag = False
        self._bottom_drag = False
        self._lcorner_drag = False
        self._right_drag = False
        self._left_drag = False

    def resizeEvent(self, e):

        if self._move_drag == False:
            self._right_rect = [
                self.width() - self._padding,
                self.width() + 1,
                0,
                self.height() - self._padding,
            ]
            self._left_rect = [-1, self._padding, 0, self.height() - self._padding]
            self._bottom_rect = [
                self._padding,
                self.width() - self._padding,
                self.height() - self._padding,
                self.height() + 1,
            ]
            self._corner_rect = [
                self.width() - self._padding,
                self.width() + 1,
                self.height() - self._padding,
                self.height() + 1,
            ]
            self._lcorner_rect = [
                -1,
                self._padding,
                self.height() - self._padding,
                self.height() + 1,
            ]

    def mousePressEvent(self, event):
        # 重写鼠标点击的事件

        if (event.button() == Qt.LeftButton) and (
            isinrect(event.pos(), self._corner_rect)
        ):
            # 鼠标左键点击右下角边界区域
            self._corner_drag = True
        elif (event.button() == Qt.LeftButton) and (
            isinrect(event.pos(), self._right_rect)
        ):
            # 鼠标左键点击右侧边界区域
            self._right_drag = True
        elif (event.button() == Qt.LeftButton) and (
            isinrect(event.pos(), self._left_rect)
        ):
            # 鼠标左键点击右侧边界区域
            self._left_drag = True
            self.startxp = event.globalPos() - self.pos()
            self.startx = event.globalPos().x()
            self.startw = self.width()
        elif (event.button() == Qt.LeftButton) and (
            isinrect(event.pos(), self._bottom_rect)
        ):
            # 鼠标左键点击下侧边界区域
            self._bottom_drag = True
        elif (event.button() == Qt.LeftButton) and (
            isinrect(event.pos(), self._lcorner_rect)
        ):
            # 鼠标左键点击下侧边界区域
            self._lcorner_drag = True
            self.startxp = event.globalPos() - self.pos()
            self.startx = event.globalPos().x()
            self.startw = self.width()
        # and (event.y() < self._TitleLabel.height()):
        elif event.button() == Qt.LeftButton:
            # 鼠标左键点击标题栏区域
            self._move_drag = True
            self.move_DragPosition = event.globalPos() - self.pos()

    def mouseMoveEvent(self, QMouseEvent):
        # 判断鼠标位置切换鼠标手势

        pos = QMouseEvent.pos()

        if self._move_drag == False:
            if isinrect(pos, self._corner_rect):
                self.setCursor(Qt.SizeFDiagCursor)
            elif isinrect(pos, self._lcorner_rect):
                self.setCursor(Qt.SizeBDiagCursor)
            elif isinrect(pos, self._bottom_rect):
                self.setCursor(Qt.SizeVerCursor)
            elif isinrect(pos, self._right_rect):
                self.setCursor(Qt.SizeHorCursor)
            elif isinrect(pos, self._left_rect):
                self.setCursor(Qt.SizeHorCursor)
            else:
                self.setCursor(Qt.ArrowCursor)
        if Qt.LeftButton and self._right_drag:

            # 右侧调整窗口宽度
            self.resize(pos.x(), self.height())
        elif Qt.LeftButton and self._left_drag:
            # 右侧调整窗口宽度
            self.setGeometry(
                (QMouseEvent.globalPos() - self.startxp).x(),
                self.y(),
                self.startw - (QMouseEvent.globalPos().x() - self.startx),
                self.height(),
            )
            # self.resize(pos.x(), self.height())
        elif Qt.LeftButton and self._bottom_drag:
            # 下侧调整窗口高度
            self.resize(self.width(), QMouseEvent.pos().y())
        elif Qt.LeftButton and self._lcorner_drag:
            # 下侧调整窗口高度
            self.setGeometry(
                (QMouseEvent.globalPos() - self.startxp).x(),
                self.y(),
                self.startw - (QMouseEvent.globalPos().x() - self.startx),
                QMouseEvent.pos().y(),
            )
        elif Qt.LeftButton and self._corner_drag:
            # 右下角同时调整高度和宽度
            self.resize(pos.x(), pos.y())
        elif Qt.LeftButton and self._move_drag:
            # 标题栏拖放窗口位置
            self.move(QMouseEvent.globalPos() - self.move_DragPosition)

    def mouseReleaseEvent(self, QMouseEvent):
        # 鼠标释放后，各扳机复位
        self._move_drag = False
        self._corner_drag = False
        self._bottom_drag = False
        self._lcorner_drag = False
        self._right_drag = False
        self._left_drag = False


class Prompt_dialog(QDialog):
    def __init__(self, parent, title, info, items) -> None:
        super().__init__(parent)
        self.setWindowFlags(
            self.windowFlags()
            & ~Qt.WindowContextHelpButtonHint
            & ~Qt.WindowCloseButtonHint
            | Qt.WindowStaysOnTopHint
        )
        self.setWindowTitle(title)
        self.setWindowIcon(qtawesome.icon("fa-question"))

        _layout = QVBoxLayout()

        _layout.addWidget(QLabel(info))

        self.text = []
        for _ in items:

            le = QLineEdit()
            le.setText(_[1])
            self.text.append((le))
            hl = QHBoxLayout()
            hl.addWidget(QLabel(_[0]))
            hl.addWidget(le)
            _layout.addLayout(hl)
        button = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button.accepted.connect(self.accept)
        button.rejected.connect(self.reject)
        _layout.addWidget(button)
        self.setLayout(_layout)
        self.resize(400, 1)


def callbackwrap(d, k, call, _):
    d[k] = _
    if call:
        try:
            call(_)
        except:
            print_exc()


def getsimplecombobox(lst, d, k, callback=None):
    s = QComboBox()
    s.addItems(lst)
    if (k not in d) or (d[k] >= len(lst)):
        d[k] = 0
    s.setCurrentIndex(d[k])
    s.currentIndexChanged.connect(functools.partial(callbackwrap, d, k, callback))
    return s


def getlineedit(d, key, callback=None, readonly=False):
    s = QLineEdit()
    s.setText(d[key])
    s.setReadOnly(readonly)
    s.textChanged.connect(functools.partial(callbackwrap, d, key, callback))
    return s


def getspinbox(mini, maxi, d, key, double=False, step=1, callback=None, dec=1):
    if double:
        s = QDoubleSpinBox()
        s.setDecimals(dec)
    else:
        s = QSpinBox()
        d[key] = int(d[key])
    s.setMinimum(mini)
    s.setMaximum(maxi)
    s.setSingleStep(step)
    s.setValue(d[key])
    s.valueChanged.connect(functools.partial(callbackwrap, d, key, callback))
    return s


def getcolorbutton(
    d,
    key,
    callback,
    name=None,
    parent=None,
    icon="fa.paint-brush",
    constcolor=None,
    enable=True,
    transparent=True,
    qicon=None,
    sizefixed=False,
):
    if qicon is None:
        qicon = qtawesome.icon(icon, color=constcolor if constcolor else d[key])
    b = QPushButton()
    b.setIcon(qicon)
    b.setEnabled(enable)
    b.setIconSize(QSize(20, 20))
    if sizefixed:
        b.setFixedSize(QSize(20, 20))
    if transparent:
        b.setStyleSheet(
            """background-color: rgba(255, 255, 255, 0);
            color: black;
            border: 0px;
            font: 100 10pt;"""
        )
    b.clicked.connect(callback)
    b.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    if name:
        setattr(parent, name, b)
    return b


def yuitsu_switch(parent, configdict, dictobjectn, key, callback, checked):
    dictobject = getattr(parent, dictobjectn)
    if checked:
        for k in dictobject:
            configdict[k]["use"] = k == key
            dictobject[k].setChecked(k == key)

    if callback:
        callback(key, checked)


def getsimpleswitch(
    d, key, enable=True, callback=None, name=None, pair=None, parent=None, default=None
):
    if default:
        if key not in d:
            d[key] = default

    b = MySwitch(sign=d[key], enable=enable)
    b.clicked.connect(functools.partial(callbackwrap, d, key, callback))
    b.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    if pair:
        if pair not in dir(parent):
            setattr(parent, pair, {})
        getattr(parent, pair)[name] = b
    elif name:
        setattr(parent, name, b)
    return b


def selectcolor(
    parent, configdict, configkey, button, item=None, name=None, callback=None
):

    color = QColorDialog.getColor(QColor(configdict[configkey]), parent)
    if not color.isValid():
        return
    if button is None:
        button = getattr(item, name)
    button.setIcon(qtawesome.icon("fa.paint-brush", color=color.name()))
    configdict[configkey] = color.name()

    if callback:
        try:
            callback()
        except:
            print_exc()


def getboxlayout(widgets, lc=QHBoxLayout, margin0=False, makewidget=False):
    cp_layout = lc()
    for w in widgets:
        if isinstance(w, QWidget):
            cp_layout.addWidget(w)
        elif isinstance(w, QLayout):
            cp_layout.addLayout(w)
    if margin0:
        cp_layout.setContentsMargins(0, 0, 0, 0)
    if makewidget:
        w = QWidget()
        w.setLayout(cp_layout)
        return w
    return cp_layout


def textbrowappendandmovetoend(textOutput, sentence, addspace=True):
    scrollbar = textOutput.verticalScrollBar()
    atBottom = (
        scrollbar.value() + 3 > scrollbar.maximum()
        or scrollbar.value() / scrollbar.maximum() > 0.975
    )
    cursor = QTextCursor(textOutput.document())
    cursor.movePosition(QTextCursor.End)
    cursor.insertText(
        (("" if textOutput.document().isEmpty() else "\n") if addspace else "")
        + sentence
    )
    if atBottom:
        scrollbar.setValue(scrollbar.maximum())


def getscaledrect(size: QSize):
    rate = QApplication.instance().devicePixelRatio()
    rect = (
        int(rate * size.width()),
        int(rate * (size.height())),
    )
    return rect


class WebivewWidget(QWidget):
    on_load = pyqtSignal(str)

    def __init__(self, parent=None, debug=False) -> None:
        super().__init__(parent)
        declare_library_path(
            os.path.abspath(
                os.path.join(
                    "files/plugins/",
                    ("DLL32", "DLL64")[platform.architecture()[0] == "64bit"],
                    "webview",
                )
            )
        )
        self.webview = None
        self.webview = Webview(debug=debug, window=int(self.winId()))

        self.webview.bind("__on_load", self._on_load)
        self.webview.init("""window.__on_load(window.location.href)""")

    def _on_load(self, href):
        self.on_load.emit(href)

    def navigate(self, url):
        self.webview.navigate(url)

    def resizeEvent(self, a0: QResizeEvent) -> None:
        if self.webview:
            hwnd = self.webview.get_native_handle(
                webview_native_handle_kind_t.WEBVIEW_NATIVE_HANDLE_KIND_UI_WIDGET
            )
            size = getscaledrect(a0.size())
            windows.MoveWindow(hwnd, 0, 0, size[0], size[1], True)

    def setHtml(self, html):
        self.webview.set_html(html)


class mshtmlWidget(QWidget):
    on_load = pyqtSignal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.browser = HTMLBrowser(int(self.winId()))
        threading.Thread(target=self.__getcurrenturl).start()

    def __getcurrenturl(self):
        url = None
        while True:
            _u = self.browser.get_current_url()
            if url != _u:
                url = _u
                try:
                    self.on_load.emit(_u)
                except:  # RuntimeError: wrapped C/C++ object of type mshtmlWidget has been deleted
                    break
            time.sleep(0.5)

    def navigate(self, url):
        self.browser.navigate(url)

    def resizeEvent(self, a0: QResizeEvent) -> None:
        size = getscaledrect(a0.size())
        self.browser.resize(0, 0, size[0], size[1])

    def setHtml(self, html):
        html = html.replace('target="_blank"', "")
        html = "<html><head><meta http-equiv='x-ua-compatible' content='IE=edge'></head><body>{}</body></html>".format(
            html
        )
        self.browser.set_html(html)


class auto_select_webview(QWidget):
    on_load = pyqtSignal(str)

    def clear(self):
        self.navigate("about:blank")

    def navigate(self, url):
        self._maybecreate()
        self.internal.navigate(url)

    def setHtml(self, html):
        self._maybecreate()
        self.internal.setHtml(html)

    def navigate(self, url):
        self._maybecreate()
        self.internal.navigate(url)

    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.cantusewebview2 = False
        self.internal = None
        self.contex = -1
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self._maybecreate()


    def _maybecreate(self):
        if globalconfig["usewebview"] != self.contex:
            if globalconfig["usewebview"] == 1 and self.cantusewebview2:
                return
            if self.internal:
                self.layout().removeWidget(self.internal)
            self.internal = self._createwebview()
            self.layout().addWidget(self.internal)

    def _createwebview(self):
        self.contex = globalconfig["usewebview"]
        if self.contex == 0:
            browser = mshtmlWidget(self)
        elif self.contex == 1:
            try:
                browser = WebivewWidget(self, True)
            except Exception:
                self.cantusewebview2 = True
                browser = mshtmlWidget(self)
        browser.on_load.connect(self.on_load)
        return browser


class threebuttons(QWidget):
    btn1clicked = pyqtSignal()
    btn2clicked = pyqtSignal()
    btn3clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        button = QPushButton(self)
        button.setText(_TR("添加行"))
        button.clicked.connect(self.btn1clicked)
        button2 = QPushButton(self)
        button2.setText(_TR("删除选中行"))
        button2.clicked.connect(self.btn2clicked)
        button3 = QPushButton(self)
        button3.setText(_TR("立即应用"))
        button3.clicked.connect(self.btn3clicked)
        layout.addWidget(button)
        layout.addWidget(button2)
        layout.addWidget(button3)


def tabadd_lazy(tab, title, getrealwidgetfunction):
    q = QWidget()
    v = QVBoxLayout()
    q.setLayout(v)
    v.setContentsMargins(0, 0, 0, 0)
    q.lazyfunction = lambda: v.addWidget(getrealwidgetfunction())
    tab.addTab(q, _TR(title))
