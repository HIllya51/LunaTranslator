from qtsymbols import *
import functools
import gobject, NativeUtils
from myutils.config import globalconfig
from gui.usefulwidget import (
    getcolorbutton,
    getspinbox,
    getsimpleswitch,
    getsmalllabel,
    getIconButton,
    resizableframeless,
    SplitLine,
    getsimplecombobox,
    getboxlayout,
    limitpos,
)
from gui.showword import WordViewer
from gui.dynalang import LDialog, LFormLayout


class DraggableQWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.setMouseTracking(True)
        self.mouse_press_pos = None
        self.window_pos_at_press = None

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.mouse_press_pos = event.globalPos()
            self.window_pos_at_press = self.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.mouse_press_pos:
            move_pos = event.globalPos() - self.mouse_press_pos
            new_window_pos = self.window_pos_at_press + move_pos
            self.move(new_window_pos)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.mouse_press_pos = None
        super().mouseReleaseEvent(event)


def createsomecontrols(
    callbackR, callbackDWM, kR, kRsys, kRsysDf, kDWM, kshadow, needcheck=True
):
    def ___(callbackX, _):
        callbackX()

    spin1 = getspinbox(
        0, 50, globalconfig, kR, callback=functools.partial(___, callbackR)
    )
    sw = None
    effectlayout = None
    if needcheck:

        def __vRsys(kRsys, kRsysDf):
            return gobject.sys_ge_win_11 and globalconfig.get(kRsys, kRsysDf)

        vRsys = functools.partial(__vRsys, kRsys, kRsysDf)

        def __vR(kDWM, vRsys):
            return globalconfig[kDWM] == 0 and not vRsys()

        def __yinyinguse(kDWM, vRsys):
            return globalconfig[kDWM] != 0 and not vRsys()

        vR = functools.partial(__vR, kDWM, vRsys)
        if not vR():
            spin1.hide()
        yinyinguse = functools.partial(__yinyinguse, kDWM, vRsys)
        __shadowxx = getsmalllabel("阴影")()
        __shadowxx2 = getsimpleswitch(
            globalconfig, kshadow, callback=functools.partial(___, callbackDWM)
        )

        def __cb2(
            spin1: QSpinBox,
            vR,
            __shadowxx: QLabel,
            yinyinguse,
            __shadowxx2: QLabel,
            callbackR,
            _,
        ):
            spin1.setVisible(vR()),
            __shadowxx.setVisible(yinyinguse()),
            __shadowxx2.setVisible(yinyinguse()),
            callbackR()

        if gobject.sys_ge_win_11:
            sw = getsimpleswitch(
                globalconfig,
                kRsys,
                default=kRsysDf,
                callback=functools.partial(
                    __cb2, spin1, vR, __shadowxx, yinyinguse, __shadowxx2, callbackR
                ),
            )

        if not yinyinguse():
            __shadowxx.hide()
            __shadowxx2.hide()
        __shadowxx = __shadowxx
        __shadowxx2 = __shadowxx2

        def __cb(
            yinyinguse,
            __shadowxx: QLabel,
            __shadowxx2: QLabel,
            spin1: QSpinBox,
            callbackR,
            callbackDWM,
            _,
        ):
            __shadowxx.setVisible(yinyinguse())
            __shadowxx2.setVisible(yinyinguse())
            spin1.setVisible(vR())
            callbackR()
            callbackDWM()

        effectlayout = getboxlayout(
            [
                getsimplecombobox(
                    ["Disable", "Acrylic", "Aero"],
                    globalconfig,
                    kDWM,
                    callback=functools.partial(
                        __cb,
                        yinyinguse,
                        __shadowxx,
                        __shadowxx2,
                        spin1,
                        callbackR,
                        callbackDWM,
                    ),
                ),
                __shadowxx,
                __shadowxx2,
            ],
        )
    return getboxlayout([spin1, "", "使用系统圆角", sw]) if sw else spin1, effectlayout


class dialog_syssetting(LDialog):
    def __init__(self, parent: "WordViewTooltip") -> None:
        super().__init__(parent, Qt.WindowType.WindowCloseButtonHint)
        self.setWindowTitle("其他设置")
        formLayout = LFormLayout(self)

        formLayout.addRow(
            "自动朗读",
            getsimpleswitch(globalconfig, "is_search_word_auto_tts_2"),
        )
        formLayout.addRow(
            "失去焦点时关闭",
            getsimpleswitch(
                globalconfig,
                "WordViewTooltipHideFocus",
                callback=lambda x: parent.closebutton.setVisible(not x),
            ),
        )
        formLayout.addRow(SplitLine())
        spin = getspinbox(
            0,
            50,
            globalconfig,
            "WordViewTooltipBorder",
            callback=lambda _: parent.doResize(),
        )
        formLayout.addRow("边距", spin)

        spin1, lay = createsomecontrols(
            lambda: parent.setbgcolor(),
            lambda: parent.seteffect(),
            "WordViewTooltipRadius",
            "WordViewTooltipRadiusSys",
            gobject.sys_ge_win_11,
            "WordViewTooltipDWM",
            "WordViewTooltipDWM_1",
        )
        formLayout.addRow("圆角", spin1)

        formLayout.addRow("窗口特效", lay)
        color11 = getcolorbutton(
            self,
            globalconfig,
            "WordViewTooltipColor",
            callback=lambda _: parent.setbgcolor(),
            alpha=True,
            tips="背景颜色",
            cantzeroalpha=True,
        )
        formLayout.addRow("背景颜色", color11)
        color1 = getcolorbutton(
            self,
            globalconfig,
            "WordViewTooltipContentColor",
            callback=lambda _: parent.setbgcolor(),
            alpha=True,
            tips="内容背景颜色",
        )
        formLayout.addRow("内容背景颜色", color1)

        self.exec()


class WordViewTooltip(resizableframeless, DraggableQWidget):

    @property
    def gripSize(self):
        return globalconfig["WordViewTooltipBorder"]

    def focusOutEvent(self, a0):
        if globalconfig["WordViewTooltipHideFocus"]:
            focused_widget = QApplication.focusWidget()
            if (
                focused_widget
                and focused_widget.window()
                and focused_widget.window().parent() == self
            ):
                pass
            else:
                self.close()
        return super().focusOutEvent(a0)

    def doResize(self):
        self.wbutton.setGeometry(
            self.gripSize,
            self.gripSize,
            self.width() - 2 * self.gripSize,
            self.wbutton.height(),
        )
        self.view.setGeometry(
            self.gripSize,
            self.gripSize + self.wbutton.height(),
            self.width() - 2 * self.gripSize,
            self.height() - 2 * self.gripSize - self.wbutton.height(),
        )

    def resizeEvent(self, a0: QResizeEvent):
        self.doResize()
        globalconfig["WordViewTooltip2"] = a0.size().width(), a0.size().height()
        return super().resizeEvent(a0)

    def setbgcolor(self):

        NativeUtils.SetCornerNotRound(
            int(self.winId()),
            False,
            globalconfig.get("WordViewTooltipRadiusSys", gobject.sys_ge_win_11),
        )
        radiu_valid = globalconfig["WordViewTooltipDWM"] == 0 and not (
            gobject.sys_ge_win_11
            and globalconfig.get("WordViewTooltipRadiusSys", gobject.sys_ge_win_11)
        )
        color = globalconfig["WordViewTooltipColor"]
        r = globalconfig["WordViewTooltipRadius"]
        self.w.setStyleSheet(
            r""" 
        QLabel{background: %s; 
        border-radius: %spx}
 """
            % (color, r * radiu_valid)
        )
        self.w2.setStyleSheet(
            r""" 
        QLabel{background: %s;border-radius: 0px; }
 """
            % (globalconfig["WordViewTooltipContentColor"])
        )

    def seteffect(self):
        if globalconfig["WordViewTooltipDWM"] == 0:
            NativeUtils.clearEffect(int(self.winId()))
        elif globalconfig["WordViewTooltipDWM"] == 1:
            NativeUtils.setAcrylicEffect(
                int(self.winId()), globalconfig["WordViewTooltipDWM_1"], 0x00FFFFFF
            )
        elif globalconfig["WordViewTooltipDWM"] == 2:
            NativeUtils.setAeroEffect(
                int(self.winId()), globalconfig["WordViewTooltipDWM_1"]
            )

    def __init__(self, parent):
        DraggableQWidget.__init__(self)
        resizableframeless.__init__(
            self,
            parent,
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint,
            None,
        )
        self.setMouseTracking(True)

        self.setMinimumHeight(300)
        self.setMinimumWidth(300)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        w = QLabel(self)
        w.setMouseTracking(True)
        self.w = w
        w2 = QLabel(self)
        self.w2 = w2
        self.setbgcolor()
        self.seteffect()
        self.wbutton = QWidget(self)
        self.wbutton.setMouseTracking(True)
        self.wbutton.setObjectName("fuck")
        self.wbutton.setStyleSheet("QWidget#fuck{background:transparent}")
        buttons = QHBoxLayout(self.wbutton)
        buttons.setContentsMargins(0, 0, 0, 0)
        self.closebutton = getIconButton(
            icon="fa.times", callback=self.close, tips="关闭"
        )
        if globalconfig["WordViewTooltipHideFocus"]:
            self.closebutton.hide()
        buttons.addWidget(self.closebutton)
        buttons.addWidget(
            getIconButton(
                icon="fa.music",
                callback=lambda: gobject.baseobject.read_text(self.view.currWord),
                tips="语音合成",
            )
        )
        buttons.addStretch(1)
        searchword = lambda anki: (
            self.close(),
            gobject.baseobject.searchwordW.move(self.pos()),
            gobject.baseobject.searchwordW._click_word_search_function(
                self.view.currWord, self.view.save_sentence, False, self.view.readyData
            ),
            (
                gobject.baseobject.searchwordW.ankiconnect.click()
                if ((anki ^ gobject.baseobject.searchwordW.ankiconnect.isChecked()))
                else ""
            ),
        )
        buttons.addWidget(
            getIconButton(
                icon="fa.search",
                callback=lambda: (searchword(False)),
                tips="查词",
            )
        )
        buttons.addWidget(
            getIconButton(
                icon="fa.adn",
                callback=lambda: (searchword(True)),
                tips="Anki",
            )
        )
        buttons.addWidget(
            getIconButton(
                callback=functools.partial(dialog_syssetting, self), tips="设置"
            )
        )
        self.view = WordViewer(self, tabonehide=True, transp=True)
        self.view.use_bg_color_parser = True
        self.setCentralWidget(w)
        self.view.first_result_shown.connect(self.showresult)
        self.view.search_word.connect(self.view.searchword)
        self.view.search_word_in_new_window.connect(
            lambda w: gobject.baseobject.searchwordW.searchwinnewwindow(w)
        )
        self.view.setStyleSheet("background:transparent")
        self.view.internalsizechanged.connect(self.w2.resize)
        self.view.internalmoved.connect(
            lambda pos: self.w2.move(self.view.mapToParent(pos))
        )

    def searchword(self, word: str, sentence=None, append=False):
        self.savepos = QCursor.pos()
        if globalconfig["is_search_word_auto_tts_2"]:
            gobject.baseobject.read_text(word)
        self.view.searchword(word, sentence, append)

    def showresult(self):
        size = globalconfig.get("WordViewTooltip2")
        if size:
            self.resize(size[0], size[1])
        # 1 系统圆角时会谜之遮挡鼠标
        self.move(limitpos(self.savepos, self, QPoint(1, 10)))
        self.show()
        self.setFocus()
