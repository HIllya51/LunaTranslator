from qtsymbols import *
import os, platform, functools, threading, time
from traceback import print_exc
import windows, qtawesome, winsharedutils
from webviewpy import (
    webview_native_handle_kind_t,
    Webview,
    declare_library_path,
)
from winsharedutils import HTMLBrowser
from myutils.config import _TR, globalconfig
from myutils.wrapper import Singleton, Singleton_close
from myutils.utils import nowisdark


class FocusCombo(QComboBox):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def wheelEvent(self, e: QWheelEvent) -> None:

        if not self.hasFocus():
            e.ignore()
            return
        else:
            return super().wheelEvent(e)


class FocusFontCombo(QFontComboBox, FocusCombo):
    pass


class FocusSpin(QSpinBox):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def wheelEvent(self, e: QWheelEvent) -> None:

        if not self.hasFocus():
            e.ignore()
            return
        else:
            return super().wheelEvent(e)


class FocusDoubleSpin(QDoubleSpinBox):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def wheelEvent(self, e: QWheelEvent) -> None:

        if not self.hasFocus():
            e.ignore()
            return
        else:
            return super().wheelEvent(e)


@Singleton
class dialog_showinfo(QDialog):

    def __init__(self, parent, title, info) -> None:
        super().__init__(parent, Qt.WindowType.WindowCloseButtonHint)
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

    def __checked_savepos(self):
        if not self.dic:
            return
        if windows.IsZoomed(int(self.winId())) != 0:
            return
        # self.isMaximized()会在event结束后才被设置，不符合预期。
        self.dic[self.key] = list(self.geometry().getRect())

    def resizeEvent(self, a0) -> None:
        self.__checked_savepos()

    def moveEvent(self, a0) -> None:
        self.__checked_savepos()

    def closeEvent(self, event: QCloseEvent):
        self.__checked_savepos()


class closeashidewindow(saveposwindow):
    showsignal = pyqtSignal()
    realshowhide = pyqtSignal(bool)

    def __init__(self, parent, dic=None, key=None) -> None:
        super().__init__(parent, dic, key)
        self.showsignal.connect(self.showfunction)
        self.realshowhide.connect(self.realshowhidefunction)

    def realshowhidefunction(self, show):
        if show:
            self.showNormal()
        else:
            self.hide()

    def showfunction(self):
        if self.isMinimized():
            self.showNormal()
        elif self.isVisible():
            self.hide()
        else:
            self.show()

    def closeEvent(self, event: QCloseEvent):
        self.hide()
        event.ignore()
        super().closeEvent(event)


class MySwitch(QPushButton):
    def __init__(
        self, parent=None, sign=True, enable=True, icons=None, size=25, colors=None
    ):
        self.status1 = 0
        self.status2 = 0
        if colors is None:
            colors = [
                "#7f7f7f",
                "#afafaf",
                "#FFa9d4",
                "#FF69B4",
            ]
        self.colors = colors
        if icons is None:
            icons = ["fa.times", "fa.check"]
        self.icons = icons

        super().__init__(parent)

        self.setStyleSheet(
            """background-color: rgba(255, 255, 255, 0);
          color: black;
          border: 0px;
          font: 100 10pt;"""
        )

        self.clicked.connect(self.setChecked)
        self.setIconSize(QSize(size, size))
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
        super().resizeEvent(e)

    def mousePressEvent(self, event: QMouseEvent):
        # 重写鼠标点击的事件
        if isqt5:
            gpos = event.globalPos()
        else:
            gpos = event.globalPosition().toPoint()
        if (event.button() == Qt.MouseButton.LeftButton) and (
            isinrect(event.pos(), self._corner_rect)
        ):
            # 鼠标左键点击右下角边界区域
            self._corner_drag = True
        elif (event.button() == Qt.MouseButton.LeftButton) and (
            isinrect(event.pos(), self._right_rect)
        ):
            # 鼠标左键点击右侧边界区域
            self._right_drag = True
        elif (event.button() == Qt.MouseButton.LeftButton) and (
            isinrect(event.pos(), self._left_rect)
        ):
            # 鼠标左键点击右侧边界区域
            self._left_drag = True
            self.startxp = gpos - self.pos()
            self.startx = gpos.x()
            self.startw = self.width()
        elif (event.button() == Qt.MouseButton.LeftButton) and (
            isinrect(event.pos(), self._bottom_rect)
        ):
            # 鼠标左键点击下侧边界区域
            self._bottom_drag = True
        elif (event.button() == Qt.MouseButton.LeftButton) and (
            isinrect(event.pos(), self._lcorner_rect)
        ):
            # 鼠标左键点击下侧边界区域
            self._lcorner_drag = True
            self.startxp = gpos - self.pos()
            self.startx = gpos.x()
            self.startw = self.width()
        # and (event.y() < self._TitleLabel.height()):
        elif event.button() == Qt.MouseButton.LeftButton:
            # 鼠标左键点击标题栏区域
            self._move_drag = True
            self.move_DragPosition = gpos - self.pos()

    def mouseMoveEvent(self, event):
        # 判断鼠标位置切换鼠标手势

        pos = event.pos()
        if isqt5:
            gpos = event.globalPos()
        else:
            gpos = event.globalPosition().toPoint()
        if self._move_drag == False:
            if isinrect(pos, self._corner_rect):
                self.setCursor(Qt.CursorShape.SizeFDiagCursor)
            elif isinrect(pos, self._lcorner_rect):
                self.setCursor(Qt.CursorShape.SizeBDiagCursor)
            elif isinrect(pos, self._bottom_rect):
                self.setCursor(Qt.CursorShape.SizeVerCursor)
            elif isinrect(pos, self._right_rect):
                self.setCursor(Qt.CursorShape.SizeHorCursor)
            elif isinrect(pos, self._left_rect):
                self.setCursor(Qt.CursorShape.SizeHorCursor)
            else:
                self.setCursor(Qt.CursorShape.ArrowCursor)
        if Qt.MouseButton.LeftButton and self._right_drag:

            # 右侧调整窗口宽度
            self.resize(pos.x(), self.height())
        elif Qt.MouseButton.LeftButton and self._left_drag:
            # 右侧调整窗口宽度
            self.setGeometry(
                (gpos - self.startxp).x(),
                self.y(),
                self.startw - (gpos.x() - self.startx),
                self.height(),
            )
            # self.resize(pos.x(), self.height())
        elif Qt.MouseButton.LeftButton and self._bottom_drag:
            # 下侧调整窗口高度
            self.resize(self.width(), event.pos().y())
        elif Qt.MouseButton.LeftButton and self._lcorner_drag:
            # 下侧调整窗口高度
            self.setGeometry(
                (gpos - self.startxp).x(),
                self.y(),
                self.startw - (gpos.x() - self.startx),
                event.pos().y(),
            )
        elif Qt.MouseButton.LeftButton and self._corner_drag:
            # 右下角同时调整高度和宽度
            self.resize(pos.x(), pos.y())
        elif Qt.MouseButton.LeftButton and self._move_drag:
            # 标题栏拖放窗口位置
            self.move(gpos - self.move_DragPosition)

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
            & ~Qt.WindowType.WindowCloseButtonHint
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
        button = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
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


def comboboxcallbackwrap(internallist, d, k, call, _):
    _ = internallist[_]
    d[k] = _
    if call:
        try:
            call(_)
        except:
            print_exc()


def getsimplecombobox(lst, d, k, callback=None, fixedsize=False, internallist=None):
    s = FocusCombo()
    s.addItems(lst)

    if internallist:
        if (k not in d) or (d[k] not in internallist):
            d[k] = internallist[0]
        s.setCurrentIndex(internallist.index(d[k]))
        s.currentIndexChanged.connect(
            functools.partial(comboboxcallbackwrap, internallist, d, k, callback)
        )
    else:
        if (k not in d) or (d[k] >= len(lst)):
            d[k] = 0
        s.setCurrentIndex(d[k])
        s.currentIndexChanged.connect(functools.partial(callbackwrap, d, k, callback))

    if fixedsize:
        s.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
    return s


def D_getsimplecombobox(lst, d, k, callback=None, fixedsize=False, internallist=None):
    return lambda: getsimplecombobox(lst, d, k, callback, fixedsize, internallist)


def getlineedit(d, key, callback=None, readonly=False):
    s = QLineEdit()
    s.setText(d[key])
    s.setReadOnly(readonly)
    s.textChanged.connect(functools.partial(callbackwrap, d, key, callback))
    return s


def getspinbox(mini, maxi, d, key, double=False, step=1, callback=None, dec=1):
    if double:
        s = FocusDoubleSpin()
        s.setDecimals(dec)
    else:
        s = FocusSpin()
        d[key] = int(d[key])
    s.setMinimum(mini)
    s.setMaximum(maxi)
    s.setSingleStep(step)
    s.setValue(d[key])
    s.valueChanged.connect(functools.partial(callbackwrap, d, key, callback))
    return s


def D_getspinbox(mini, maxi, d, key, double=False, step=1, callback=None, dec=1):
    return lambda: getspinbox(mini, maxi, d, key, double, step, callback, dec)


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
    if callback:
        b.clicked.connect(callback)
    b.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
    if name:
        setattr(parent, name, b)
    return b


def D_getcolorbutton(
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
    return lambda: getcolorbutton(
        d,
        key,
        callback,
        name,
        parent,
        icon,
        constcolor,
        enable,
        transparent,
        qicon,
        sizefixed,
    )


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
    b.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
    b.clicked.connect(functools.partial(callbackwrap, d, key, callback))
    if pair:
        if pair not in dir(parent):
            setattr(parent, pair, {})
        getattr(parent, pair)[name] = b
    elif name:
        setattr(parent, name, b)
    return b


def D_getsimpleswitch(
    d, key, enable=True, callback=None, name=None, pair=None, parent=None, default=None
):
    return lambda: getsimpleswitch(
        d, key, enable, callback, name, pair, parent, default
    )


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


def getboxlayout(
    widgets, lc=QHBoxLayout, margin0=False, makewidget=False, delay=False, both=False
):
    cp_layout = lc()

    def __do(cp_layout, widgets):
        for w in widgets:
            if callable(w):
                w = w()
            if isinstance(w, QWidget):
                cp_layout.addWidget(w)
            elif isinstance(w, QLayout):
                cp_layout.addLayout(w)

    _do = functools.partial(__do, cp_layout, widgets)
    if margin0:
        cp_layout.setContentsMargins(0, 0, 0, 0)
    if not delay:
        _do()
    if makewidget:
        w = QWidget()
        w.setLayout(cp_layout)
    if delay:
        return w, _do
    if both:
        return w, cp_layout
    if makewidget:
        return w
    return cp_layout


def getvboxwidget():
    return getboxlayout([], lc=QVBoxLayout, margin0=True, makewidget=True, both=True)


def textbrowappendandmovetoend(textOutput, sentence, addspace=True):
    scrollbar = textOutput.verticalScrollBar()
    atBottom = (
        scrollbar.value() + 3 > scrollbar.maximum()
        or scrollbar.value() / scrollbar.maximum() > 0.975
    )
    cursor = QTextCursor(textOutput.document())
    cursor.movePosition(QTextCursor.MoveOperation.End)
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


class abstractwebview(QWidget):
    on_load = pyqtSignal(str)
    on_ZoomFactorChanged = pyqtSignal(float)
    html_limit = 2 * 1024 * 1024

    # 必须的接口
    def _setHtml(self, html):
        pass

    def navigate(self, url):
        pass

    #
    def _parsehtml(self, html):
        return self._parsehtml_dark_auto(html)

    def set_zoom(self, zoom):
        pass

    def set_transparent_background(self):
        pass

    def clear(self):
        self.navigate("about:blank")

    def setHtml(self, html):
        html = self._parsehtml(html)
        if len(html) < self.html_limit:
            self._setHtml(html)
        else:
            os.makedirs("cache/temp", exist_ok=True)
            lastcachehtml = os.path.abspath("cache/temp/" + str(time.time()) + ".html")
            with open(lastcachehtml, "w", encoding="utf8") as ff:
                ff.write(html)
            self.navigate(lastcachehtml)

    def _parsehtml_dark(self, html):
        if nowisdark():
            html = (
                html
                + """
    <style>
        body 
        { 
            background-color: rgb(44,44,44);
            color: white; 
        }
    </style>"""
            )
        return html

    def _parsehtml_dark_auto(self, html):
        return (
            html
            + """
<style>
@media (prefers-color-scheme: dark) 
{
    :root {
        color-scheme: dark;
    }
    body 
    { 
        background-color: rgb(44,44,44);
        color: white; 
    }
}
</style>
"""
        )


class WebivewWidget(abstractwebview):

    def __del__(self):
        winsharedutils.remove_ZoomFactorChanged(
            self.webview.get_native_handle(
                webview_native_handle_kind_t.WEBVIEW_NATIVE_HANDLE_KIND_BROWSER_CONTROLLER
            ),
            self.__token,
        )

    def get_controller(self):
        return self.webview.get_native_handle(
            webview_native_handle_kind_t.WEBVIEW_NATIVE_HANDLE_KIND_BROWSER_CONTROLLER
        )

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
        zoomfunc = winsharedutils.add_ZoomFactorChanged_CALLBACK(
            self.on_ZoomFactorChanged.emit
        )
        self.__token = winsharedutils.add_ZoomFactorChanged(
            self.get_controller(), zoomfunc
        )
        self.keepref = [zoomfunc]
        self.webview.bind("__on_load", self._on_load)
        self.webview.init("""window.__on_load(window.location.href)""")

        self.__darkstate = None
        t = QTimer(self)
        t.setInterval(100)
        t.timeout.connect(self.__darkstatechecker)
        t.timeout.emit()
        t.start()

    def __darkstatechecker(self):
        dl = globalconfig["darklight2"]
        if dl == self.__darkstate:
            return
        self.__darkstate = dl
        winsharedutils.put_PreferredColorScheme(self.get_controller(), dl)

    def set_zoom(self, zoom):
        self.put_ZoomFactor(zoom)

    def get_ZoomFactor(self):
        return winsharedutils.get_ZoomFactor(self.get_controller())

    def put_ZoomFactor(self, zoom):
        winsharedutils.put_ZoomFactor(self.get_controller(), zoom)

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

    def _setHtml(self, html):
        self.webview.set_html(html)

    def set_transparent_background(self):
        winsharedutils.set_transparent_background(self.get_controller())


class QWebWrap(abstractwebview):

    def __init__(self) -> None:
        super().__init__()
        from PyQt5.QtWebEngineWidgets import QWebEngineView

        self.internal = QWebEngineView(self)
        self.internal.page().urlChanged.connect(
            lambda qurl: self.on_load.emit(qurl.url())
        )
        self.internal_zoom = 1
        t = QTimer(self)
        t.setInterval(100)
        t.timeout.connect(self.__getzoomfactor)
        t.timeout.emit()
        t.start()

    def set_zoom(self, zoom):
        self.internal_zoom = zoom
        self.internal.setZoomFactor(zoom)

    def __getzoomfactor(self):
        z = self.internal.zoomFactor()
        if z != self.internal_zoom:
            self.internal_zoom = z
            self.on_ZoomFactorChanged.emit(z)

    def navigate(self, url: str):
        from PyQt5.QtCore import QUrl

        if not url.lower().startswith("http"):
            url = url.replace("\\", "/")
        self.internal.load(QUrl(url))

    def _setHtml(self, html):
        self.internal.setHtml(html)

    def resizeEvent(self, a0: QResizeEvent) -> None:
        self.internal.resize(a0.size())

    def _parsehtml(self, html):
        return self._parsehtml_dark(html)


class mshtmlWidget(abstractwebview):

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        if HTMLBrowser.version() < 10001:  # ie10之前，sethtml会乱码
            self.html_limit = 0
        self.browser = HTMLBrowser(int(self.winId()))
        self.curr_url = None
        t = QTimer(self)
        t.setInterval(100)
        t.timeout.connect(self.__getcurrenturl)
        t.timeout.emit()
        t.start()

    def __getcurrenturl(self):
        _u = self.browser.get_current_url()
        if self.curr_url != _u:
            self.curr_url = _u
            self.on_load.emit(_u)

    def navigate(self, url):
        self.browser.navigate(url)

    def resizeEvent(self, a0: QResizeEvent) -> None:
        size = getscaledrect(a0.size())
        self.browser.resize(0, 0, size[0], size[1])

    def _setHtml(self, html):
        self.browser.set_html(html)

    def _parsehtml(self, html):
        html = self._parsehtml_dark(html)
        html = """<html><head><meta http-equiv="Content-Type" content="text/html;charset=UTF-8" /></head><body style=" font-family:'{}'">{}</body></html>""".format(
            QFontDatabase.systemFont(QFontDatabase.GeneralFont).family(), html
        )
        return html


class CustomKeySequenceEdit(QKeySequenceEdit):
    changeedvent = pyqtSignal(str)

    def __init__(self, parent=None):
        super(CustomKeySequenceEdit, self).__init__(parent)

    def keyPressEvent(self, QKeyEvent):
        super(CustomKeySequenceEdit, self).keyPressEvent(QKeyEvent)
        value = self.keySequence()
        if len(value.toString()):
            self.clearFocus()
        self.changeedvent.emit(value.toString().replace("Meta", "Win"))
        self.setKeySequence(QKeySequence(value))


def getsimplekeyseq(dic, key, callback=None):
    key1 = CustomKeySequenceEdit(QKeySequence(dic[key]))

    def __(_d, _k, cb, s):
        _d[_k] = s
        if cb:
            cb()

    key1.changeedvent.connect(functools.partial(__, dic, key, callback))
    return key1


def D_getsimplekeyseq(dic, key, callback=None):
    return lambda: getsimplekeyseq(dic, key, callback)


class auto_select_webview(QWidget):
    on_load = pyqtSignal(str)
    on_ZoomFactorChanged = pyqtSignal(float)

    def clear(self):
        self.internal.clear()

    def navigate(self, url):
        self._maybecreate()
        self.internal.set_zoom(self.internalsavedzoom)
        self.internal.navigate(url)

    def setHtml(self, html):
        self._maybecreate()
        self.internal.set_zoom(self.internalsavedzoom)
        self.internal.setHtml(html)

    def set_zoom(self, zoom):
        self.internalsavedzoom = zoom
        self.internal.set_zoom(zoom)

    def sizeHint(self):
        return QSize(256, 192)

    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.is_fallback = -2
        self.contex = -1
        self.internal = (
            abstractwebview()
        )  # 加个占位的widget，否则等待加载的时候有一瞬间的灰色背景。
        self.lock = threading.Lock()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.internal)
        self.setLayout(layout)
        self.internalsavedzoom = 1

    def internalzoomchanged(self, zoom):
        self.internalsavedzoom = zoom
        self.on_ZoomFactorChanged.emit(zoom)

    def _maybecreate(self):
        with self.lock:
            self._maybecreate_internal()

    def _maybecreate_internal(self):
        if globalconfig["usewebview"] == self.contex:
            return
        if self.is_fallback == globalconfig["usewebview"]:
            return
        if self.internal:
            self.layout().removeWidget(self.internal)
        self.internal = self._createwebview()
        self.internal.set_zoom(self.internalsavedzoom)
        self.internal.on_load.connect(self.on_load)
        self.internal.on_ZoomFactorChanged.connect(self.internalzoomchanged)
        self.layout().addWidget(self.internal)

    def _createwebview(self):
        self.contex = globalconfig["usewebview"]
        try:
            if self.contex == 0:
                browser = mshtmlWidget()
            elif self.contex == 1:
                browser = WebivewWidget(debug=True)
            elif self.contex == 2:
                browser = QWebWrap()
        except:
            print_exc()
            self.is_fallback = self.contex
            browser = mshtmlWidget()
        return browser


class threebuttons(QWidget):
    btn1clicked = pyqtSignal()
    btn2clicked = pyqtSignal()
    btn3clicked = pyqtSignal()

    def __init__(self, btns=3, texts=None):
        super().__init__()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        button = QPushButton(self)
        if texts:
            button.setText(texts[0])
        else:
            button.setText(_TR("添加行"))
        button.clicked.connect(self.btn1clicked)
        button2 = QPushButton(self)
        if texts:
            button2.setText(texts[1])
        else:
            button2.setText(_TR("删除行"))
        button2.clicked.connect(self.btn2clicked)
        layout.addWidget(button)
        layout.addWidget(button2)
        if btns == 3:
            button3 = QPushButton(self)
            if texts:
                button3.setText(texts[2])
            else:
                button3.setText(_TR("立即应用"))
            button3.clicked.connect(self.btn3clicked)
            layout.addWidget(button3)


def tabadd_lazy(tab, title, getrealwidgetfunction):
    q = QWidget()
    v = QVBoxLayout()
    q.setLayout(v)
    v.setContentsMargins(0, 0, 0, 0)
    q.lazyfunction = functools.partial(getrealwidgetfunction, v)
    tab.addTab(q, title)


def automakegrid(grid: QGridLayout, lis, save=False, savelist=None):

    maxl = 0
    for nowr, line in enumerate(lis):
        nowc = 0
        for i in line:
            if type(i) == str:
                cols = 1
            elif type(i) != tuple:
                wid, cols = i, 1
            elif len(i) == 2:

                wid, cols = i
            elif len(i) == 3:
                wid, cols, arg = i
            nowc += cols
        maxl = max(maxl, nowc)

    for nowr, line in enumerate(lis):
        nowc = 0
        if save:
            ll = []
        for i in line:
            if type(i) == str:
                cols = 1
                wid = QLabel(_TR(i))
            elif type(i) != tuple:
                wid, cols = i, 1
            elif len(i) == 2:

                wid, cols = i
                if type(wid) == str:
                    wid = QLabel(_TR(wid))
            elif len(i) == 3:
                wid, cols, arg = i
                if type(wid) == str:
                    wid = QLabel((wid))
                    if arg == "link":
                        wid.setOpenExternalLinks(True)
            if cols > 0:
                col = cols
            elif cols == 0:
                col = maxl - nowc
            else:
                col = -maxl // cols
            do = None
            if callable(wid):
                wid = wid()
                if isinstance(wid, tuple):
                    wid, do = wid
            grid.addWidget(wid, nowr, nowc, 1, col)
            if do:
                do()
            if save:
                ll.append(wid)
            nowc += cols
        if save:
            savelist.append(ll)
        grid.setRowMinimumHeight(nowr, 25)


def makegrid(grid=None, save=False, savelist=None, savelay=None, delay=False):

    class gridwidget(QWidget):
        pass

    gridlayoutwidget = gridwidget()
    gridlay = QGridLayout()
    gridlay.setAlignment(Qt.AlignmentFlag.AlignTop)
    gridlayoutwidget.setLayout(gridlay)
    gridlayoutwidget.setStyleSheet("gridwidget{background-color:transparent;}")

    def do(gridlay, grid, save, savelist, savelay):
        automakegrid(gridlay, grid, save, savelist)
        if save:
            savelay.append(gridlay)

    __do = functools.partial(do, gridlay, grid, save, savelist, savelay)
    if not delay:
        __do()
        return gridlayoutwidget
    return gridlayoutwidget, __do


def makescroll(widget):
    scroll = QScrollArea()
    # scroll.setHorizontalScrollBarPolicy(1)
    scroll.setStyleSheet("""QScrollArea{background-color:transparent;border:0px}""")
    scroll.setWidgetResizable(True)
    return scroll


def makescrollgrid(grid, lay, save=False, savelist=None, savelay=None):
    wid, do = makegrid(grid, save, savelist, savelay, delay=True)
    swid = makescroll(wid)
    lay.addWidget(swid)
    swid.setWidget(wid)
    do()
    return wid


def makesubtab_lazy(
    titles=None, functions=None, klass=None, callback=None, delay=False
):
    if klass:
        tab = klass()
    else:
        tab = QTabWidget()

    def __(t, i):
        try:
            w = t.currentWidget()
            if "lazyfunction" in dir(w):
                w.lazyfunction()
                delattr(w, "lazyfunction")
        except:
            print_exc()
        if callback:
            callback(i)

    tab.currentChanged.connect(functools.partial(__, tab))

    def __do(tab, titles, functions):
        if titles and functions:
            for i, func in enumerate(functions):
                tabadd_lazy(tab, titles[i], func)

    ___do = functools.partial(__do, tab, titles, functions)
    if not delay:
        ___do()
        return tab
    else:
        return tab, ___do


@Singleton_close
class listediter(QDialog):
    def showmenu(self, p: QPoint):
        r = self.hctable.currentIndex().row()
        if r < 0:
            return
        menu = QMenu(self.hctable)
        remove = QAction(_TR("删除"))
        copy = QAction(_TR("复制"))
        up = QAction(_TR("上移"))
        down = QAction(_TR("下移"))
        menu.addAction(remove)
        menu.addAction(copy)
        menu.addAction(up)
        menu.addAction(down)
        action = menu.exec(self.hctable.cursor().pos())

        if action == remove:
            self.hcmodel.removeRow(self.hctable.currentIndex().row())

        elif action == copy:
            winsharedutils.clipboard_set(
                self.hcmodel.item(
                    self.hctable.currentIndex().row(),
                    self.hctable.currentIndex().column(),
                ).text()
            )

        elif action == up:

            self.moverank(-1)

        elif action == down:
            self.moverank(1)

    def moverank(self, dy):
        target = (self.hctable.currentIndex().row() + dy) % self.hcmodel.rowCount()
        text = self.hcmodel.item(
            self.hctable.currentIndex().row(), self.hctable.currentIndex().column()
        ).text()
        self.hcmodel.removeRow(self.hctable.currentIndex().row())
        self.hcmodel.insertRow(target, [QStandardItem(text)])

    def __init__(
        self, p, title, header, lst, closecallback=None, ispathsedit=None
    ) -> None:
        super().__init__(p)
        self.lst = lst
        self.closecallback = closecallback
        self.ispathsedit = ispathsedit
        try:
            self.setWindowTitle(title)
            model = QStandardItemModel()
            model.setHorizontalHeaderLabels([header])
            self.hcmodel = model

            table = QTableView()
            table.horizontalHeader().setSectionResizeMode(
                QHeaderView.ResizeMode.ResizeToContents
            )
            table.horizontalHeader().setStretchLastSection(True)
            if ispathsedit:
                table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
            table.setSelectionMode((QAbstractItemView.SelectionMode.SingleSelection))
            table.setWordWrap(False)
            table.setModel(model)

            table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            table.customContextMenuRequested.connect(self.showmenu)
            self.hctable = table

            for row, k in enumerate(lst):  # 2
                self.hcmodel.insertRow(row, [QStandardItem(k)])
            formLayout = QVBoxLayout()
            formLayout.addWidget(self.hctable)
            self.buttons = threebuttons(btns=2)
            self.buttons.btn1clicked.connect(self.click1)
            self.buttons.btn2clicked.connect(self.clicked2)

            formLayout.addWidget(self.buttons)
            self.setLayout(formLayout)
            self.resize(600, self.sizeHint().height())
            self.show()
        except:
            print_exc()

    def clicked2(self):
        self.hcmodel.removeRow(self.hctable.currentIndex().row())

    def closeEvent(self, a0: QCloseEvent) -> None:
        self.buttons.setFocus()
        rows = self.hcmodel.rowCount()
        rowoffset = 0
        dedump = set()
        self.lst.clear()
        for row in range(rows):
            k = self.hcmodel.item(row, 0).text()
            if k == "" or k in dedump:
                rowoffset += 1
                continue
            self.lst.append(k)
            dedump.add(k)
        if self.closecallback:
            self.closecallback()

    def __cb(self, path):

        self.hcmodel.insertRow(0, [QStandardItem(path)])

    def click1(self):

        if self.ispathsedit:
            openfiledirectory(
                "",
                multi=False,
                edit=None,
                isdir=self.ispathsedit.get("isdir", False),
                filter1=self.ispathsedit.get("filter1", "*.*"),
                callback=self.__cb,
            )
        else:
            self.hcmodel.insertRow(0, [QStandardItem("")])


class listediterline(QLineEdit):
    clicked = pyqtSignal()

    def __init__(self, name, header, reflist, ispathsedit=None):
        super().__init__()
        self.setReadOnly(True)
        self.reflist = reflist
        self.setText("|".join(reflist))

        self.clicked.connect(
            functools.partial(
                listediter,
                self,
                name,
                header,
                reflist,
                closecallback=self.callback,
                ispathsedit=ispathsedit,
            )
        )

    def callback(self):
        self.setText("|".join(self.reflist))

    def mousePressEvent(self, e):
        self.clicked.emit()
        super().mousePressEvent(e)


def openfiledirectory(directory, multi, edit, isdir, filter1="*.*", callback=None):
    if isdir:
        f = QFileDialog.getExistingDirectory(directory=directory)
        res = f
    else:
        if multi:
            f = QFileDialog.getOpenFileNames(directory=directory, filter=filter1)
        else:
            f = QFileDialog.getOpenFileName(directory=directory, filter=filter1)
        res = f[0]

    if len(res) == 0:
        return
    if edit:
        edit.setText("|".join(res) if multi else res)
    if callback:
        callback(res)


def getsimplepatheditor(
    text=None,
    multi=False,
    isdir=False,
    filter1="*.*",
    callback=None,
    useiconbutton=False,
    reflist=None,
    name=None,
    header=None,
):
    lay = QHBoxLayout()
    lay.setContentsMargins(0, 0, 0, 0)

    if multi:
        e = listediterline(
            name, header, reflist, dict(isdir=isdir, multi=False, filter1=filter1)
        )
        lay.addWidget(e)
    else:
        e = QLineEdit(text)
        e.setReadOnly(True)
        if useiconbutton:
            bu = getcolorbutton("", "", None, icon="fa.gear", constcolor="#FF69B4")
        else:
            bu = QPushButton(_TR("选择" + ("文件夹" if isdir else "文件")))
        bu.clicked.connect(
            functools.partial(
                openfiledirectory,
                text,
                multi,
                e,
                isdir,
                "" if isdir else filter1,
                callback,
            )
        )
        lay.addWidget(e)
        lay.addWidget(bu)
    return lay
