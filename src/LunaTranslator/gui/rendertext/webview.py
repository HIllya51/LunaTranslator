from qtsymbols import *
import gobject, json, functools, time
import windows
import NativeUtils
from myutils.config import globalconfig, _TR
from myutils.wrapper import threader
import uuid
from gui.usefulwidget import WebviewWidget, Exteditor
from gui.RichMessageBox import RichMessageBox
from sometypes import WordSegResult
from gui.rendertext.tooltipswidget import tooltipswidget
from gui.rendertext.textbrowser import get_sorted_toolbuttonitems
from gui.rendertext.webview_common import webview_common
from gui.qevent import TransparentChangedEvent
from NativeUtils import MenuItem


class TextBrowser(WebviewWidget, webview_common):
    contentsChanged = pyqtSignal(QSize)
    _switchcursor = pyqtSignal(Qt.CursorShape)
    _isDragging = pyqtSignal(bool)
    __tooltipshelper = pyqtSignal(object)

    def crashed_callback(self, info: bytes):
        RichMessageBox(
            self,
            _TR("错误"),
            _TR("Webview2崩溃，将切换为Qt显示。") + "\n" + info.decode(),
        )
        globalconfig["rendertext_using"] = "textbrowser"
        gobject.base.translation_ui.translate_text.loadinternal(True, True)
        gobject.base.switchdisplayengine.emit("textbrowser")

    def on_menu(self, selecttext: str):
        if selecttext:
            return [
                MenuItem(
                    text="查词",
                    clicked=functools.partial(self.menusearchword, selecttext.strip()),
                ),
                MenuItem(
                    text="翻译",
                    clicked=functools.partial(
                        gobject.base.textgetmethod, selecttext.strip()
                    ),
                ),
                MenuItem(
                    text="朗读",
                    clicked=functools.partial(
                        gobject.base.read_text, selecttext.strip()
                    ),
                ),
            ]
        else:

            def __cb():
                globalconfig["dragable"] = not globalconfig.get("dragable", True)
                self.setMouseTracking(globalconfig.get("dragable", True))

            def __cb2():
                globalconfig["hidetools"] = not globalconfig.get("hidetools", False)
                gobject.base.translation_ui.enterfunction()

            items = [
                MenuItem(
                    text="清空",
                    clicked=self.___cleartext,
                ),
                MenuItem(
                    text="设置",
                    clicked=gobject.base.settin_ui_showsignal.emit,
                ),
                MenuItem(issep=True),
                MenuItem(
                    text="可拖动的",
                    clicked=__cb,
                    checkable=True,
                    checked=globalconfig.get("dragable", True),
                ),
                MenuItem(
                    text="隐藏工具栏",
                    clicked=__cb2,
                    checkable=True,
                    checked=globalconfig.get("hidetools", False),
                ),
                MenuItem(
                    text="鼠标滚动查看历史文本",
                    clicked=lambda: globalconfig.__setitem__(
                        "enable_wheel_history",
                        not globalconfig.get("enable_wheel_history", True),
                    ),
                    checkable=True,
                    checked=globalconfig.get("enable_wheel_history", True),
                ),
            ]

            gongjulan = MenuItem(text="工具按钮")
            for tip, clicked, _, check in get_sorted_toolbuttonitems():
                gongjulan.appendSub(
                    MenuItem(
                        text=tip,
                        clicked=functools.partial(
                            threader(gobject.base.safeinvokefunction.emit), clicked
                        ),
                        checkable=bool(check),
                        checked=check() if check else None,
                    )
                )
            items.insert(0, gongjulan)
            # 渲染引擎/浏览器插件（同历史文本菜单；处理器在 wrapper 上，
            # 与设置页互相同步）。原生菜单回调上下文里不能直接动 UI：
            # threader 丢线程 + safeinvokefunction 推回主线程执行，
            # 也保证切换引擎销毁本 webview 发生在菜单回调返回之后
            _tomainsafe = lambda f: functools.partial(
                threader(gobject.base.safeinvokefunction.emit), f
            )
            items.append(MenuItem(issep=True))
            items.append(
                MenuItem(
                    text="使用Webview2显示",
                    clicked=_tomainsafe(self.parent().menuswitchengine),
                    checkable=True,
                    # 本菜单只在 webview 引擎激活时出现，恒为开
                    checked=True,
                )
            )
            items.append(
                MenuItem(
                    text="附加浏览器插件",
                    clicked=_tomainsafe(self.parent().menutogglewebext),
                    checkable=True,
                    checked=globalconfig.get("webviewLoadExt", True),
                )
            )
            if globalconfig.get("webviewLoadExt", True):
                items.append(
                    MenuItem(
                        text="浏览器插件",
                        clicked=_tomainsafe(functools.partial(Exteditor, self)),
                    )
                )
            return items

    def event(self, a0: QEvent) -> bool:
        if isinstance(a0, TransparentChangedEvent):
            self.__starttrans0checker(a0.transparent_value())
        return super().event(a0)

    def __starttrans0checker(self, transparent_value):
        if transparent_value == 0:
            self.trans0checker.start(50)
        else:
            self.trans0checker.stop()

    def __checkmousestate(self):
        if not self.geometry().contains(self.mapFromGlobal(QCursor.pos())):
            return
        self.eval("report_clickword_positions()", self.__callback)

    def getundermouseword(self, result):

        z = self.get_zoom()
        for ww in json.loads(result):
            __ = ww["x"], ww["y"], ww["w"], ww["h"]
            x, y, w, h = (_ * z for _ in __)
            pos = self.mapToGlobal(QPointF(x, y).toPoint())
            rect = QRectF()
            rect.setTopLeft(pos)
            rect.setWidth(w)
            rect.setHeight(h)
            if not rect.contains(QCursor.pos()):
                continue
            return ww["word"]

    @threader
    def __callback(self, result):
        word = self.getundermouseword(result)
        if not word:
            self.__tooltipshelper.emit(tooltipswidget.hidetooltipwindow)
            return
        self.__tooltipshelper.emit(
            functools.partial(
                tooltipswidget.tracetooltipwindow,
                WordSegResult.from_dict(word),
                QCursor.pos(),
            )
        )
        lb1 = windows.GetKeyState(windows.VK_LBUTTON) < 0
        rb1 = windows.GetKeyState(windows.VK_RBUTTON) < 0
        mb1 = windows.GetKeyState(windows.VK_MBUTTON) < 0
        if not lb1 and not rb1 and not mb1:
            return
        uid = uuid.uuid4()
        self.trans0checkercheck = uid
        time.sleep(0.05)
        if uid != self.trans0checkercheck:
            return
        lb = windows.GetKeyState(windows.VK_LBUTTON) < 0
        rb = windows.GetKeyState(windows.VK_RBUTTON) < 0
        mb = windows.GetKeyState(windows.VK_MBUTTON) < 0
        if lb or rb or mb:
            return
        gobject.base.clickwordcallback(
            word, "left" if lb1 else ("right" if rb1 else "mid")
        )

    @threader
    def menusearchword(self, w: str):
        sentence = gobject.base.currenttext
        if w not in sentence:
            sentence = None
        gobject.base.searchwordW.search_word.emit(
            dict(word=w.replace("\n", "").strip(), sentence=sentence)
        )

    def __init__(self, parent) -> None:
        super().__init__(
            parent, transp=True, loadext=globalconfig.get("webviewLoadExt", True)
        )
        # webview2当会执行alert之类的弹窗js时，若qt窗口不可视，会卡住
        self.setMouseTracking(globalconfig.get("dragable", True))
        self.bind("callwheelEvent", gobject.base.wheelhistory.emit)
        self.bind("calllunaclickedword", gobject.base.clickwordcallback)
        self.bind("calllunaMouseMove", self.calllunaMouseMove)
        self.bind("calllunaMousePress", self.calllunaMousePress)
        self.bind("calllunaMouseRelease", self.calllunaMouseRelease)
        self.bind("calllunaSizeChanged", self.calllunaSizeChanged)
        self.bind("calllunaEnter", self.calllunaEnter)
        self.bind("calllunaLeave", self.calllunaLeave)
        self.bind("calllunaloadready", self.calllunaloadready)
        self.bind("calllunaMouseHoverWord", self.calllunaMouseHoverWord)
        self.set_zoom(globalconfig.get("ZoomFactor2", 1))
        self.on_ZoomFactorChanged.connect(
            functools.partial(globalconfig.__setitem__, "ZoomFactor2")
        )
        self.isfirst = True
        self.window().cursorSet.connect(self._switchcursor)
        self._switchcursor.connect(self.switchcursor)
        self.window().isDragging.connect(self._isDragging)
        self._isDragging.connect(
            lambda b: self.setselectable(
                False if b else globalconfig.get("selectable", True)
            )
        )
        self.loadex()
        self.__tooltipshelper.connect(lambda f: f())
        self.trans0checkercheck = None
        self.trans0checker = QTimer(self)
        self.trans0checker.timeout.connect(self.__checkmousestate)
        self.webview.setfocus()

    def ___cleartext(self):
        self.parent().clear(False)
        gobject.base.currenttext = ""

    def refreshcontent(self):
        gobject.base.translation_ui.translate_text.refreshcontent()

    def refreshcontent_before(self):
        self.debugeval("refreshcontent_before()")

    def refreshcontent_after(self):
        self.debugeval("refreshcontent_after()")

    def switchcursor(self, cursor):
        cursor_map = {
            Qt.CursorShape.ArrowCursor: "default",
            Qt.CursorShape.UpArrowCursor: "n-resize",
            Qt.CursorShape.CrossCursor: "crosshair",
            Qt.CursorShape.WaitCursor: "wait",
            Qt.CursorShape.IBeamCursor: "text",
            Qt.CursorShape.SizeVerCursor: "ns-resize",
            Qt.CursorShape.SizeHorCursor: "ew-resize",
            Qt.CursorShape.SizeBDiagCursor: "nesw-resize",
            Qt.CursorShape.SizeFDiagCursor: "nwse-resize",
            Qt.CursorShape.SizeAllCursor: "move",
            Qt.CursorShape.BlankCursor: "none",
            Qt.CursorShape.SplitVCursor: "row-resize",
            Qt.CursorShape.SplitHCursor: "col-resize",
            Qt.CursorShape.PointingHandCursor: "pointer",
            Qt.CursorShape.ForbiddenCursor: "not-allowed",
            Qt.CursorShape.WhatsThisCursor: "help",
            Qt.CursorShape.BusyCursor: "progress",
            Qt.CursorShape.OpenHandCursor: "grab",
            Qt.CursorShape.ClosedHandCursor: "grabbing",
        }
        self.eval('switchcursor("{}")'.format(cursor_map.get(cursor, "default")))

    def loadex(self, extra=None):
        self.navigate(self.loadex_(extra=extra))

    def debugeval(self, js):
        # print(js)
        self.eval(js)

    def calllunaSizeChanged(self, h, w):
        r = self.get_zoom()
        sz = QSizeF(w, h) * r
        if gobject.runtime_for_xp:
            sz *= NativeUtils.GetDevicePixelRatioF(int(self.winId()))
        self.contentsChanged.emit(sz.toSize())

    def parsemousebutton(self, i):
        btn_map = {
            0: Qt.MouseButton.LeftButton,
            1: Qt.MouseButton.MiddleButton,
            2: Qt.MouseButton.RightButton,
            3: Qt.MouseButton.BackButton,
            4: Qt.MouseButton.ForwardButton,
        }
        return btn_map.get(i, Qt.MouseButton.NoButton)

    def parsexyaspos(self, x, y):
        zoom = self.get_zoom()
        x = zoom * x
        y = zoom * y
        return QPointF(x, y)

    def calllunaMousePress(self, btn, x, y):
        pos = self.parsexyaspos(x, y)
        btn = self.parsemousebutton(btn)
        event = QMouseEvent(
            QEvent.Type.MouseButtonPress,
            pos,
            btn,
            btn,
            Qt.KeyboardModifier.NoModifier,
        )
        QApplication.sendEvent(self, event)

    def calllunaEnter(self):
        QApplication.sendEvent(self.window(), QEvent(QEvent.Type.Enter))

    def calllunaLeave(self):
        QApplication.sendEvent(self.window(), QEvent(QEvent.Type.Leave))

    def calllunaMouseRelease(self, btn, x, y):
        pos = self.parsexyaspos(x, y)
        btn = self.parsemousebutton(btn)
        event = QMouseEvent(
            QEvent.Type.MouseButtonRelease,
            pos,
            btn,
            btn,
            Qt.KeyboardModifier.NoModifier,
        )
        QApplication.sendEvent(self, event)

    def calllunaMouseHoverWord(self, event, x, y, word: str):
        if event in ("mouseenter", "mousemove"):
            tooltipswidget.tracetooltipwindow(
                WordSegResult.from_dict((word)),
                self.mapToGlobal(self.parsexyaspos(x, y).toPoint()),
            )
        elif event == "mouseleave":
            tooltipswidget.hidetooltipwindow()

    def calllunaMouseMove(self, x, y):
        if globalconfig.get("selectable", True) and globalconfig.get(
            "selectableEx", False
        ):
            return
        pos = self.parsexyaspos(x, y)
        event = QMouseEvent(
            QEvent.Type.MouseMove,
            pos,
            Qt.MouseButton.NoButton,
            Qt.MouseButton.NoButton,
            Qt.KeyboardModifier.NoModifier,
        )
        QApplication.sendEvent(self, event)

    def GetSelectedText(self):
        ret = []
        self.eval("getCleanSelectionText()", ret.append)
        if ret:
            return json.loads(ret[0])
