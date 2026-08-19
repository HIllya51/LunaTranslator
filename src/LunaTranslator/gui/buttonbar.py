from qtsymbols import *
import functools
from traceback import print_exc
import qtawesome, gobject
from myutils.config import (
    globalconfig,
)
from myutils.utils import (
    str2rgba,
)
from myutils.hwnd import getExeIcon, getcurrexe
from gui.usefulwidget import (
    resizableframeless,
    load_specific_icon_size,
)
from gui.dynalang import LLabel


class buttonfunctions:
    def __init__(
        self,
        clicked=None,
        rightclick=None,
        middleclick=None,
        iconstate=None,
        colorstate=None,
    ):
        (
            self.clicked,
            self.rightclick,
            self.middleclick,
            self.iconstate,
            self.colorstate,
        ) = (clicked, rightclick, middleclick, iconstate, colorstate)


class IconLabelX(LLabel):
    clicked = pyqtSignal()
    rightclick = pyqtSignal()
    middleclick = pyqtSignal()

    @staticmethod
    def w():
        return (
            globalconfig.get("buttonsize", 25)
            * gobject.Consts.toolwdivh
            * gobject.Consts.toolscale
        )

    @staticmethod
    def h():
        return globalconfig.get("buttonsize", 25) * gobject.Consts.toolscale

    def setSize(self):
        sz = (QSizeF(IconLabelX.w(), IconLabelX.h())).toSize()
        self.setFixedSize(sz)

    def __init__(self, *argc):
        super().__init__(*argc)
        self.reflayout = None
        self.belong = None
        self._icon = QIcon()
        self._size = QSize()
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self.pixmap_ = None
        self.setScaledContents(True)
        # 开启鼠标跟踪，使鼠标在按钮上移动时事件能向父窗口传播，
        # 从而让 resizableframeless 更新边框 resize 光标（按钮无显式
        # cursor，会继承父窗口光标）。
        self.setMouseTracking(True)

    def update_scaled_pixmap(self):
        if self.pixmap_ is None:
            return
        label_size = self.size()
        if label_size.width() <= 0 or label_size.height() <= 0:
            return

        original_width = self.pixmap_.width()
        original_height = self.pixmap_.height()
        label_ratio = label_size.width() / label_size.height()
        img_ratio = original_width / original_height

        if 0:
            if label_ratio > img_ratio:
                canvas_width = original_width
                canvas_height = original_width / label_ratio
            else:
                canvas_width = original_height * label_ratio
                canvas_height = original_height
        else:
            if label_ratio > img_ratio:
                canvas_width = original_height * label_ratio
                canvas_height = original_height
            else:
                canvas_width = original_width
                canvas_height = original_width / label_ratio

        dpr = self.devicePixelRatioF()
        canvas = QPixmap(int(canvas_width * dpr), int(canvas_height * dpr))
        canvas.setDevicePixelRatio(dpr)
        canvas.fill(Qt.GlobalColor.transparent)

        painter = QPainter(canvas)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        x = int((canvas_width - original_width) / 2)
        y = int((canvas_height - original_height) / 2)
        painter.drawPixmap(x, y, self.pixmap_)
        painter.end()
        self.setPixmap(canvas)

    def resizeEvent(self, event):
        self.update_scaled_pixmap()
        super().resizeEvent(event)

    def showinlayout(self, layout: QBoxLayout):

        layout.addWidget(self)
        self.show()
        self.reflayout = layout

    def hideinlayout(self):
        if self.reflayout is None:
            return
        _ = self.reflayout
        self.reflayout = None
        _.removeWidget(self)
        self.hide()

    def resizeEvent(self, e: QResizeEvent):
        h = int(e.size().height() / gobject.Consts.toolscale)
        self.setIconSize(QSize(int(h * gobject.Consts.IconSizeHW), h))

    def setIconStr(self, icon: str, color: str):
        if len(icon) > 1 and (icon == "luna" or not icon.startswith("fa.")):
            self.pixmap_ = (
                getExeIcon(getcurrexe(), icon=False, large=True)
                if icon == "luna"
                else load_specific_icon_size(icon)
            )
            self.update_scaled_pixmap()
            self._icon = None
        else:
            self.pixmap_ = None
            self._icon = qtawesome.icon(icon, color=color)
        self.update()

    def setIconSize(self, size: QSize):
        self._size = size
        self.update()

    def paintEvent(self, a0: QPaintEvent) -> None:
        if self.pixmap():
            return super().paintEvent(a0)
        if self._icon is None:
            return
        if self._size.isEmpty():
            return
        painter = QPainter(self)
        rect = QRect(
            (self.width() - self._size.width()) // 2,
            (self.height() - self._size.height()) // 2,
            self._size.width(),
            self._size.height(),
        )
        self._icon.paint(
            painter,
            rect,
            Qt.AlignmentFlag.AlignCenter,
            QIcon.Mode.Normal,
            QIcon.State.On,
        )

    def _resize_ancestor(self):
        win = self.window()
        if isinstance(win, resizableframeless):
            return win
        return None

    def mousePressEvent(self, ev: QMouseEvent) -> None:
        win = self._resize_ancestor()
        if win and win.in_resize_zone(self.mapTo(win, ev.pos())):
            return super().mousePressEvent(ev)
        if QObject.receivers(self, self.clicked) == 0:
            return super().mousePressEvent(ev)

    def mouseReleaseEvent(self, ev: QMouseEvent) -> None:
        # 父窗口正在拖动缩放时，把释放事件传播回去以结束拖动，
        # 并避免在缩放结束后误触发按钮 click。
        win = self._resize_ancestor()
        if win and win.isdoingsomething():
            return super().mouseReleaseEvent(ev)
        if self.rect().contains(ev.pos()):
            if ev.button() == Qt.MouseButton.RightButton:
                self.rightclick.emit()
            elif ev.button() == Qt.MouseButton.LeftButton:
                self.clicked.emit()
            elif ev.button() == Qt.MouseButton.MiddleButton:
                self.middleclick.emit()
        return super().mouseReleaseEvent(ev)


class ButtonBar(QFrame):
    def setDirection(self, v):
        self.v = v
        direct = [QBoxLayout.Direction.LeftToRight, QBoxLayout.Direction.TopToBottom][v]
        self.threelayout.setDirection(direct)
        self._left.setDirection(direct)
        self._center.setDirection(direct)
        self._right.setDirection(direct)

    def __init__(self, *argc):
        super().__init__(*argc)
        self.v = False

        def __(p: QBoxLayout = None, pp=None):
            _ = QBoxLayout(QBoxLayout.Direction.LeftToRight, pp)
            _.setContentsMargins(0, 0, 0, 0)
            _.setSpacing(0)
            if p is not None:
                p.addLayout(_)
            return _

        self.threelayout = __(pp=self)
        self._left = __(self.threelayout)
        self.threelayout.addStretch()
        self._center = __(self.threelayout)
        self.threelayout.addStretch()
        self._right = __(self.threelayout)
        self.cntbtn = 0
        self.buttons: "dict[str, IconLabelX]" = {}
        self.iconstate = {}
        self.colorstate = {}

    def refreshtoolicon(self):
        for name in self.buttons:
            if name in self.colorstate:
                color = (
                    globalconfig.get("buttoncolor_1", "#ff03f2")
                    if self.colorstate[name]()
                    else globalconfig.get("buttoncolor", "#2e2eff")
                )
            else:
                color = globalconfig.get("buttoncolor", "#2e2eff")
            if name in self.iconstate:
                icon = (
                    globalconfig["toolbutton"]["buttons"][name]["icon"]
                    if self.iconstate[name]()
                    else globalconfig["toolbutton"]["buttons"][name]["icon2"]
                )
            else:
                icon = globalconfig["toolbutton"]["buttons"][name]["icon"]
            self.buttons[name].setIconStr(icon, color)

    def setstyle(self, bottomr, bottomr3):

        style = """IconLabelX:focus {{outline: 0px;}}
            IconLabelX{{
                background-color: rgba(255, 255, 255, 0);
                border: 0px;{bottomr3};
            }}
            IconLabelX#IconLabelX2:hover{{
                background-color: {color0};
                border: 0px;{bottomr3};
            }}
            IconLabelX#IconLabelX1:hover{{
                background-color: {color1};
                border: 0px;{bottomr3};
            }}
            #titlebar{{border-width: 0;{bottomr};background-color: {color2}}}
        """.format(
            bottomr3=bottomr3,
            color1=globalconfig.get("button_color_normal", "#FFFFFF"),
            color0="red",
            bottomr=bottomr,
            color2=str2rgba(
                globalconfig.get("backcolor_tool", "#ffaaff"),
                globalconfig.get("transparent_tool", 50),
            ),
        )
        self.setStyleSheet(style)

    def takusanbuttons(
        self,
        clicked,
        rightclick,
        tips,
        name,
        belong=None,
        iconstate=None,
        colorstate=None,
        middleclick=None,
    ):
        button = IconLabelX()

        def callwrap(call):
            try:
                call()
            except:
                print_exc()

        if clicked:
            button.clicked.connect(functools.partial(callwrap, clicked))
        if rightclick:
            button.rightclick.connect(functools.partial(callwrap, rightclick))
        if middleclick:
            button.middleclick.connect(functools.partial(callwrap, middleclick))
        if tips:
            button.setToolTip(tips)
            button.setAccessibleName(tips)
        if clicked:
            button.setObjectName("IconLabelX{}".format(2 if name == "quit" else 1))
        else:
            button.setMouseTracking(True)
        button.reflayout = None
        button.belong = belong
        self.buttons[name] = button
        if iconstate:
            self.iconstate[name] = iconstate
        if colorstate:
            self.colorstate[name] = colorstate

    def adjustbuttons(self):
        __ = [self._left, self._right, self._center]
        cnt = 0
        for name in globalconfig["toolbutton"]["rank2"]:
            button: IconLabelX = self.buttons[name]
            if button.belong:
                hide = True
                for k in button.belong:
                    if (
                        k in globalconfig["sourcestatus2"]
                        and globalconfig["sourcestatus2"][k]["use"]
                    ):
                        hide = False
                        break
                if hide:
                    button.hideinlayout()
                    continue
            if (
                name in globalconfig["toolbutton"]["buttons"]
                and not globalconfig["toolbutton"]["buttons"][name]["use"]
            ):
                button.hideinlayout()
                continue
            layout: QBoxLayout = __[
                globalconfig["toolbutton"]["buttons"][name]["align"]
            ]
            button.showinlayout(layout)
            cnt += 1
        self.cntbtn = cnt
        self.adjustminwidth()

    def adjustminwidth(self):
        p: QWidget = self.parent()
        if self.v:
            w = self.cntbtn * IconLabelX.h()
            p.setMinimumHeight(max(int(w), 200))
            p.setMinimumWidth(self.width() * 1)
        else:
            w = self.cntbtn * IconLabelX.w()
            p.setMinimumWidth(max(int(w), 200))
            p.setMinimumHeight(self.height() * 1)

    def setbuttonsize(self):

        if globalconfig.get("verticalhorizontal", False):
            self.setFixedWidth(int(IconLabelX.w()))
        else:
            self.setFixedHeight(int(IconLabelX.h()))
        for _ in self.buttons:
            btn: IconLabelX = self.buttons[_]
            btn.setSize()
