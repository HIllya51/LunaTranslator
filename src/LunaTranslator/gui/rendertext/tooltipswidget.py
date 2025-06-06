from qtsymbols import *
from myutils.config import globalconfig
from gui.rendertext.texttype import dataget, TextType
import gobject
from traceback import print_exc
from sometypes import WordSegResult
import windows
from myutils.config import globalconfig
from gui.usefulwidget import getcolorbutton, getspinbox, limitpos
from myutils.wrapper import Singleton, threader
from gui.dynalang import LDialog, LFormLayout
from gui.flowsearchword import createsomecontrols
import NativeUtils


@Singleton
class tooltipssetting(LDialog):
    def __cb(self, *_):
        tooltipswidget.resetstyle()
        gobject.baseobject.translation_ui.translate_text.settooltipsstyle(
            globalconfig["word_hover_bg_color"],
            globalconfig["word_hover_text_color"],
            globalconfig["word_hover_border"],
            globalconfig["word_hover_border_R"],
        )

    def __init__(self, parent) -> None:
        super().__init__(parent, Qt.WindowType.WindowCloseButtonHint)
        self.setWindowTitle("设置")
        formLayout = LFormLayout(self)

        spin = getspinbox(0, 50, globalconfig, "word_hover_border", callback=self.__cb)
        formLayout.addRow("边距", spin)

        spin1, lay = createsomecontrols(
            self.__cb,
            tooltipswidget.seteffect,
            "word_hover_border_R",
            "word_hover_border_R_SYS",
            False,
            "word_hover_DWM",
            "word_hover_DWM_1",
            (globalconfig["rendertext_using"] != "webview")
            or (not globalconfig["word_hover_action_usewb2"]),
        )
        formLayout.addRow("圆角", spin1)
        if lay:
            formLayout.addRow("窗口特效", lay)
        color = getcolorbutton(
            self,
            globalconfig,
            "word_hover_bg_color",
            alpha=True,
            tips="背景颜色",
            callback=self.__cb,
        )
        formLayout.addRow("背景颜色", color)
        color = getcolorbutton(
            self,
            globalconfig,
            "word_hover_text_color",
            tips="文字颜色",
            callback=self.__cb,
        )
        formLayout.addRow("文字颜色", color)
        self.show()


class TextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

        # 使其看起来和感觉像一个普通标签
        self.setReadOnly(True)
        self.setFrameStyle(0)  # QFrame.NoFrame

        pal = self.palette()
        pal.setColor(QPalette.ColorRole.Base, Qt.GlobalColor.transparent)
        self.setPalette(pal)

        # 自动换行，动态调整最小高度
        self.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        self.setWordWrapMode(QTextOption.WrapMode.WrapAnywhere)

        # 连接文档大小变化信号
        self.document().documentLayout().documentSizeChanged.connect(
            self.adjustMinimumSize
        )

    def adjustMinimumSize(self, size: QSizeF):
        """根据文档大小调整最小高度"""
        self.setMinimumHeight(int(size.height()) + 2 * self.frameWidth())


class tooltipswidget(QMainWindow, dataget):
    @staticmethod
    def resetstyle():
        if tooltipswidget.tooltipwindow:
            tooltipswidget.tooltipwindow._setstyle()

    @staticmethod
    def seteffect():
        if tooltipswidget.tooltipwindow:
            tooltipswidget.tooltipwindow._seteffect()

    def _seteffect(self):
        if globalconfig["word_hover_DWM"] == 0:
            NativeUtils.clearEffect(int(self.winId()))
        elif globalconfig["word_hover_DWM"] == 1:
            NativeUtils.setAcrylicEffect(
                int(self.winId()), globalconfig["word_hover_DWM_1"], 0x00FFFFFF
            )
        elif globalconfig["word_hover_DWM"] == 2:
            NativeUtils.setAeroEffect(
                int(self.winId()), globalconfig["word_hover_DWM_1"]
            )

    tooltipwindow: "tooltipswidget" = None

    @staticmethod
    def createtipstext(word: WordSegResult):
        tooltipcontent = ""
        if word.prototype and word.word != word.prototype:
            tooltipcontent += " / " + word.prototype
        if word.kana and word.kana != word.word:
            tooltipcontent += " / " + word.kana
        if word.info:
            tooltipcontent += "\n" + ",".join(word.info)
        if tooltipcontent:
            return word.word + tooltipcontent

    def _setstyle(self):
        NativeUtils.SetCornerNotRound(
            int(self.winId()), False, globalconfig.get("word_hover_border_R_SYS", False)
        )

        radiu_valid = globalconfig["word_hover_DWM"] == 0 and not (
            gobject.sys_ge_win_11 and globalconfig.get("word_hover_border_R_SYS", False)
        )
        self.qlabel.setStyleSheet(
            r""" 
        background: {};  
        color: {};    
        padding: {}px;   
        border-radius: {}px; 
 """.format(
                globalconfig["word_hover_bg_color"],
                globalconfig["word_hover_text_color"],
                globalconfig["word_hover_border"],
                globalconfig["word_hover_border_R"] * radiu_valid,
            )
        )

    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        windows.SetWindowLong(
            int(self.winId()),
            windows.GWL_EXSTYLE,
            windows.GetWindowLong(int(self.winId()), windows.GWL_EXSTYLE)
            | windows.WS_EX_TRANSPARENT,
        )
        qlabel = TextEdit(self)
        self.qlabel = qlabel
        self._setstyle()
        self._seteffect()
        self.setCentralWidget(qlabel)

    def showtext(self, text, pos: QPoint, mw):
        font = self._createqfont(TextType.Origin)
        self.qlabel.resize(QSize(mw, 1))
        self.qlabel.setPlainText(text)
        self.qlabel.setFont(font)

        self.resize(
            int(self.qlabel.document().idealWidth() + 2 * self.qlabel.frameWidth()),
            self.qlabel.minimumHeight(),
        )
        pos = limitpos(pos, self, QPoint(0, 10))
        self.move(pos)
        self.show()

    @staticmethod
    def hidetooltipwindow():
        if tooltipswidget.tooltipwindow:
            tooltipswidget.tooltipwindow.hide()
        gobject.baseobject.WordViewTooltip.Leave()

    @staticmethod
    def tracetooltipwindow(word: WordSegResult, pos):
        skip = False
        if globalconfig["usesearchword_S_hover"]:
            result = gobject.baseobject.checkkeypresssatisfy(
                "searchword_S_hover", False
            )
            result = result == -1 or result == True
            skip = result
            wordwhich = lambda k: (word.word, word.prototype)[
                globalconfig["usewordoriginfor"].get(k, False)
            ]
            threader(gobject.signals.hover_search_word.emit)(
                wordwhich("searchword_S_hover"),
                gobject.baseobject.currenttext,
                False,
                True,
                result,
            )
        if skip:
            return
        if gobject.baseobject.WordViewTooltip.isVisible():
            return
        if globalconfig["word_hover_show_word_info"]:

            try:
                if not tooltipswidget.tooltipwindow:
                    tooltipswidget.tooltipwindow = tooltipswidget(
                        gobject.baseobject.translation_ui.translate_text
                    )
                tips = tooltipswidget.createtipstext(word)
                if tips:
                    tooltipswidget.tooltipwindow.showtext(
                        tips,
                        pos,
                        gobject.baseobject.translation_ui.translate_text.width(),
                    )
                else:
                    tooltipswidget.tooltipwindow.hide()
            except:
                print_exc()
