from qtsymbols import *
from myutils.config import globalconfig, static_data
from gui.rendertext.texttype import (
    dataget,
    TextType,
    ColorControl,
    SpecialColor,
    FenciColor,
)
import gobject, functools, importlib, NativeUtils
from traceback import print_exc
from gui.rendertext.textbrowser_imp.base import base
from gui.dynalang import LAction
from sometypes import WordSegResult
from gui.rendertext.tooltipswidget import tooltipswidget

reference: "list[QLabel]" = []


class WordSegResultX(WordSegResult):
    def __init__(self, *a, **w):
        super().__init__(*a, **w)
        self.word_X: str = w.get("word_X")
        self.ref: bool = w.get("ref", False)

    @staticmethod
    def fromW(w: WordSegResult):
        return WordSegResultX(
            w.word,
            w.kana,
            w.isdeli,
            w.wordclass,
            w._prototype,
            hidekana=w.hidekana,
            info=w.info,
            isshit=w.isshit,
        )

    def copy(self):
        _ = WordSegResultX.fromW(self)
        _.word = self.word
        _.ref = self.ref
        return _

    def __repr__(self):
        return super().__repr__() + str(dict(word_X=self.word_X, ref=self.ref))


class QLabel_w(QLabel):
    def __init__(self, *argc):
        super().__init__(*argc)
        self.word: str = None
        self.refmask: QLabel_w = None
        self.ref: QLabel_w = None
        self.company: QLabel_w = None


class Qlabel_c(QLabel_w):
    def mousePressEvent(self, ev):
        self.pr = True
        return super().mousePressEvent(ev)

    def mouseMoveEvent(self, ev):
        tooltipswidget.tracetooltipwindow(self.word, self.mapToGlobal(ev.pos()))
        # return super().mouseMoveEvent(ev)

    def mouseReleaseEvent(self, event: QMouseEvent):
        try:
            if self.rect().contains(event.pos()):
                try:
                    if self.pr:
                        if event.button() == Qt.MouseButton.LeftButton:
                            gobject.baseobject.clickwordcallback(self.word, False)
                        elif event.button() == Qt.MouseButton.RightButton:
                            gobject.baseobject.clickwordcallback(self.word, True)
                except:
                    print_exc()
            self.pr = False
        except:
            print_exc()
        return super().mouseReleaseEvent(event)

    def enterEvent(self, a0) -> None:
        try:
            if self.company:
                self.company.ref.setStyleSheet(
                    "background-color: " + globalconfig["hovercolor"]
                )
                reference.append(self.company.ref)
        except:
            pass
        self.ref.setStyleSheet("background-color: " + globalconfig["hovercolor"])
        reference.append(self.ref)
        return super().enterEvent(a0)

    def leaveEvent(self, a0) -> None:
        try:
            if self.company:
                self.company.ref.setStyleSheet("background-color: rgba(0,0,0,0.01);")
                reference.remove(self.company.ref)
        except:
            pass
        self.ref.setStyleSheet("background-color: rgba(0,0,0,0.01);")
        try:
            reference.remove(self.ref)
        except:
            pass
        tooltipswidget.hidetooltipwindow()
        return super().leaveEvent(a0)


class FenciQLabel(QLabel_w):
    def __init__(self, *argc, **kw):
        self.last = None
        self.color = None
        super().__init__(*argc, **kw)

    def setColor(self, color: ColorControl):
        style = "background-color: {};".format(color.get())
        self.last = color.get()
        self.color = color
        self.setStyleSheet(style)

    def maybestylechanged(self):
        if not self.isVisible():
            return
        if self.last == self.color.get():
            return
        self.setColor(self.color)


class QTextBrowser_1(QTextEdit):
    def __init__(self, parent: "TextBrowser") -> None:
        super().__init__(parent)
        self.p = parent
        self.pr = None
        self.setReadOnly(True)
        self.prpos = QPoint()
        self.selectionChanged.connect(self.selectcg)
        self.ignorecount = 0

    def selectcg(self):
        self.pr = self.textCursor().selectedText()

    def getcurrlabel(self, pos: QPoint):
        for label in self.p.searchmasklabels:
            if not label.isVisible():
                continue
            if not label.geometry().contains(pos):
                continue
            return label

    def mousePressEvent(self, ev: QMouseEvent):
        if ev.button() == Qt.MouseButton.LeftButton:
            c = self.textCursor()
            c.clearSelection()
            self.setTextCursor(c)
        self.prpos = ev.pos()
        if self.ismousehastext(ev):
            return super().mousePressEvent(ev)
        else:
            self.ignorecount += 1
            ev.ignore()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        try:
            label = self.getcurrlabel(event.pos())
            if label and label.refmask.word:
                if event.button() == Qt.MouseButton.LeftButton:
                    if self.prpos == event.pos() or not self.pr:
                        gobject.baseobject.clickwordcallback(label.refmask.word, False)
                elif event.button() == Qt.MouseButton.RightButton:
                    if not self.pr:
                        gobject.baseobject.clickwordcallback(label.refmask.word, True)
                        return event.ignore()
        except:
            pass
        if self.ignorecount:
            self.ignorecount -= 1
            event.ignore()
        else:
            return super().mouseReleaseEvent(event)

    def ismousehastext(self, ev: QMouseEvent):
        cursor = self.cursorForPosition(ev.pos())
        rect1 = self.cursorRect(cursor)
        cursor.movePosition(QTextCursor.MoveOperation.NextCharacter)
        rect2 = self.cursorRect(cursor)
        cursor.movePosition(QTextCursor.MoveOperation.PreviousCharacter)
        cursor.movePosition(QTextCursor.MoveOperation.PreviousCharacter)
        rect3 = self.cursorRect(cursor)
        if rect1.y() == rect2.y():
            rect1 = rect1.united(rect2)
        if rect1.y() == rect3.y():
            rect1 = rect1.united(rect3)
        return rect1.contains(ev.pos())

    def focusOutEvent(self, e):
        tooltipswidget.hidetooltipwindow()
        return super().focusOutEvent(e)

    def mouseMoveEvent(self, ev: QMouseEvent):
        if globalconfig["selectable"] and globalconfig["selectableEx"]:
            tooltipswidget.hidetooltipwindow()
            return super().mouseMoveEvent(ev)
        for label in self.p.searchmasklabels:
            if label.geometry().contains(ev.pos()):
                continue
            try:
                label.refmask.setStyleSheet("background-color: rgba(0,0,0,0.01);")
                label.company.refmask.setStyleSheet(
                    "background-color: rgba(0,0,0,0.01);"
                )
                reference.remove(label.refmask)
                reference.remove(label.company.refmask)
            except:
                pass
        targetlabel = self.getcurrlabel(ev.pos())
        if targetlabel and targetlabel.isVisible():
            try:
                tooltipswidget.tracetooltipwindow(
                    targetlabel.refmask.word, self.mapToGlobal(ev.pos())
                )
                targetlabel.refmask.setStyleSheet(
                    "background-color: " + globalconfig["hovercolor"]
                )
                targetlabel.company.refmask.setStyleSheet(
                    "background-color: " + globalconfig["hovercolor"]
                )
                reference.append(targetlabel.refmask)
                reference.append(targetlabel.company.refmask)
            except:
                pass
        else:
            tooltipswidget.hidetooltipwindow()
        if not self.ismousehastext(ev):
            self.viewport().setCursor(Qt.CursorShape.ArrowCursor)
        else:
            self.viewport().setCursor(Qt.CursorShape.IBeamCursor)
        if self.ignorecount:
            ev.ignore()
        else:
            return super().mouseMoveEvent(ev)


class TextBrowser(QWidget, dataget):
    contentsChanged = pyqtSignal(QSize)
    dropfilecallback = pyqtSignal(str)
    _padding = 5

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        if not files:
            return
        file = files[0]
        self.dropfilecallback.emit(file)

    def __makeborder(self, size: QSize):
        _padding = self._padding
        self.masklabel_top.setGeometry(0, 0, size.width(), _padding)

        self.masklabel_left.setGeometry(0, 0, _padding, size.height())
        self.masklabel_right.setGeometry(
            self.width() - _padding, 0, _padding, size.height()
        )
        self.masklabel_bottom.setGeometry(
            0, size.height() - _padding, size.width(), _padding
        )

    def contentchangedfunction(self):
        sz = self.textbrowser.document().size().toSize()
        visheight = sz.height()
        self.textbrowser.resize(self.width(), visheight)
        self.contentsChanged.emit(QSize(sz.width(), visheight + self.labeloffset_y))

    def resizeEvent(self, event: QResizeEvent):
        self.atback2.resize(event.size())
        self.atback_color.resize(event.size())
        self.toplabel2.resize(event.size())
        self.masklabel.resize(event.size())

        self.__makeborder(event.size())

    def menunoselect(self, p):
        currlabel = self.textbrowser.getcurrlabel(p)
        if currlabel and currlabel.isVisible():
            return
        menu = QMenu(gobject.baseobject.commonstylebase)
        search = LAction("清空", menu)
        menu.addAction(search)
        action = menu.exec(QCursor.pos())
        if action == search:
            self.parent().clear()
            gobject.baseobject.currenttext = ""

    def showmenu(self, p):
        curr = self.textbrowser.textCursor().selectedText()
        if not curr:
            return self.menunoselect(p)
        menu = QMenu(gobject.baseobject.commonstylebase)

        search = LAction("查词", menu)
        translate = LAction("翻译", menu)
        tts = LAction("朗读", menu)
        copy = LAction("复制", menu)
        menu.addAction(search)
        menu.addAction(translate)
        menu.addAction(tts)
        menu.addSeparator()
        menu.addAction(copy)
        action = menu.exec(QCursor.pos())
        if action == search:
            gobject.baseobject.searchwordW.search_word.emit(curr, None, False)
        elif action == copy:
            NativeUtils.ClipBoard.text = curr
        elif action == tts:
            gobject.baseobject.read_text(curr)
        elif action == translate:
            gobject.baseobject.textgetmethod(curr, False)

    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.savetaglabels: "list[FenciQLabel]" = []
        self.searchmasklabels_clicked: "list[QLabel_w]" = []
        self.searchmasklabels_clicked2: "list[Qlabel_c]" = []
        self.searchmasklabels_clicked_num = 0
        self.searchmasklabels: "list[FenciQLabel]" = []
        self.showatcenterflag = globalconfig["showatcenter"]
        self.yinyinglabels: "list[base]" = []
        self.yinyinglabels_idx = 0

        self.yinyingposline = 0
        self.lastcolor = None
        self.iteryinyinglabelsave: "dict[str, list[FenciQLabel]]" = {}
        self.saveiterclasspointer = {}
        self.cleared = True

        self.setAcceptDrops(True)
        self.atback_color = QLabel(self)
        self.atback_color.setMouseTracking(True)
        self.atback2 = QLabel(self)
        self.atback2.setMouseTracking(True)

        self.toplabel2 = QLabel(self)
        self.toplabel2.setMouseTracking(True)
        self.textbrowser = QTextBrowser_1(self)
        self.textbrowser.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.textbrowser.customContextMenuRequested.connect(self.showmenu)

        self.textbrowser.document().contentsChanged.connect(self.contentchangedfunction)
        self.tranparentcolor = QColor()
        self.tranparentcolor.setAlpha(0)
        self.textbrowser.setTextColor(self.tranparentcolor)

        self.textbrowser.setStyleSheet(
            "border-width: 0;\
            border-style: outset;\
            background-color: rgba(0, 0, 0, 0)"
        )

        self.textcursor = self.textbrowser.textCursor()
        self.textbrowser.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.textbrowser.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.customContextMenuRequested.connect(self.menunoselect)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.masklabel = QLabel(self.textbrowser)
        self.masklabel.setMouseTracking(True)
        self.masklabel.customContextMenuRequested.connect(self.menunoselect)
        self.masklabel.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.masklabel_left = QLabel(self)
        self.masklabel_left.setMouseTracking(True)
        # self.masklabel_left.setStyleSheet('background-color:red')
        self.masklabel_right = QLabel(self)
        # self.masklabel_right.setStyleSheet('background-color:red')
        self.masklabel_right.setMouseTracking(True)
        self.masklabel_bottom = QLabel(self)
        self.masklabel_bottom.setMouseTracking(True)
        self.masklabel_top = QLabel(self)
        self.masklabel_top.setMouseTracking(True)
        # self.masklabel_bottom.setStyleSheet('background-color:red')
        self.resets1()
        self.setselectable(globalconfig["selectable"])

    def resets1(self):
        self.currenttype = globalconfig["rendertext_using_internal"]["textbrowser"]
        if self.currenttype not in static_data["textrender"]["textbrowser"]:
            self.currenttype = static_data["textrender"]["textbrowser"][0]
            globalconfig["rendertext_using_internal"]["textbrowser"] = static_data[
                "textrender"
            ]["textbrowser"][0]

        __ = importlib.import_module(
            "gui.rendertext.textbrowser_imp." + self.currenttype
        )

        self.currentclass = functools.partial(__.TextLine, self.currenttype)

    def resets(self):
        self.searchmasklabels_clicked_num = 0
        for label in self.searchmasklabels:
            label.hide()
        for label in self.searchmasklabels_clicked:
            label.hide()
        for label in self.searchmasklabels_clicked2:
            label.hide()
        for label in self.savetaglabels:
            label.hide()

        self.yinyinglabels_idx = 0
        for label in self.yinyinglabels:
            label.hide()
        for labels in self.iteryinyinglabelsave.values():
            for label in labels:
                label.hide()
        if self.currenttype == globalconfig["rendertext_using_internal"]["textbrowser"]:
            return
        self.resets1()
        for label in self.savetaglabels:
            label.deleteLater()
        self.savetaglabels.clear()
        for label in self.yinyinglabels:
            label.deleteLater()
        self.yinyinglabels.clear()
        for labels in self.iteryinyinglabelsave.values():
            for label in labels:
                label.deleteLater()
        self.iteryinyinglabelsave.clear()

    def setselectable(self, b):
        self.masklabel.setHidden(b)

    def seteditable(self, _):
        pass

    def _setnextfont(self, font, cleared):
        if cleared:
            self.textbrowser.setFont(font)

        self.textbrowser.moveCursor(QTextCursor.MoveOperation.End)
        f = QTextCharFormat()
        f.setFont(font)
        f.setForeground(self.tranparentcolor)
        c = self.textbrowser.textCursor()
        c.setCharFormat(f)
        self.textbrowser.setTextCursor(c)

    def refreshcontent_before(self):
        pass

    def refreshcontent_after(self):
        pass

    def showatcenter(self, center):
        self.showatcenterflag = center
        self.parent().refreshcontent()

    def showhidetranslate(self, show):
        self.parent().refreshcontent()

    def showhidert(self, _):
        self.parent().refreshcontent()

    def showhidename(self, _):
        self.parent().refreshcontent()

    def showhideorigin(self, show):
        self.parent().refreshcontent()

    def settooltipsstyle(self, *_):
        pass

    def showhideerror(self, show):
        self.parent().refreshcontent()

    def setwordhoveruse(self, _):
        pass

    def verticalhorizontal(self, v):
        pass

    def set_word_hover_show_word_info(self, _):
        pass

    def setfontstyle(self):
        self.parent().refreshcontent()

    def resetstyle(self):
        self.parent().refreshcontent()

    def setfontextra(self, klass: str):
        self.parent().refreshcontent()

    def setcolorstyle(self, _=None):
        for label in self.searchmasklabels:
            label.maybestylechanged()
        for label in self.savetaglabels:
            label.maybestylechanged()
        for label in self.yinyinglabels:
            label.maybestylechanged()
        for labels in self.iteryinyinglabelsave.values():
            for label in labels:
                label.maybestylechanged()

    def checkskip(self, texttype: TextType):
        if (texttype in (TextType.Origin,)) and (not globalconfig["isshowrawtext"]):
            return True
        if (texttype in (TextType.Translate, TextType.Error_translator)) and (
            not globalconfig["showfanyi"]
        ):
            return True
        if (texttype in (TextType.Error_translator, TextType.Error_origin)) and (
            not globalconfig["showtranexception"]
        ):
            return True
        return False

    def __findsame(self, s1, s2):
        i = 0
        while i < len(s1) and i < len(s2):
            if s1[i] != s2[i]:
                break
            i += 1
        return i

    def checkaddname(self, name, text):
        if name and globalconfig["showfanyisource"]:
            text = name + " " + text
        return text

    def iter_append(
        self,
        iter_context_class,
        texttype: TextType,
        name,
        text,
        color: ColorControl,
        klass,
    ):
        if self.checkskip(texttype):
            return
        text = self.checkaddname(name, text)
        if iter_context_class not in self.saveiterclasspointer:
            self._textbrowser_append(texttype, "", [], color, klass)
            self.saveiterclasspointer[iter_context_class] = {
                "currtext": "",
                "curr": self._getcurrpointer(),
                "start": self._getcurrpointer(),
            }

        currbefore = self.saveiterclasspointer[iter_context_class]["curr"]
        currtext = self.saveiterclasspointer[iter_context_class]["currtext"]
        currlen = len(currtext)
        _samenum = self.__findsame(text, currtext)
        if _samenum < currlen:
            self._deletebetween(
                self.saveiterclasspointer[iter_context_class]["start"] + _samenum,
                self.saveiterclasspointer[iter_context_class]["curr"],
            )
        newtext = text[_samenum:]
        self._insertatpointer(
            self.saveiterclasspointer[iter_context_class]["start"] + _samenum,
            newtext,
        )

        self.saveiterclasspointer[iter_context_class]["currtext"] = text
        currcurrent = self._getcurrpointer()
        self.saveiterclasspointer[iter_context_class]["curr"] = currcurrent
        currchange = currcurrent - currbefore
        for _klass in self.saveiterclasspointer:
            if _klass == iter_context_class:
                continue
            if self.saveiterclasspointer[_klass]["curr"] > currbefore:
                self.saveiterclasspointer[_klass]["curr"] += currchange
                self.saveiterclasspointer[_klass]["start"] += currchange

        self._showyinyingtext2(
            color,
            iter_context_class,
            self.saveiterclasspointer[iter_context_class]["start"],
            text,
            self._createqfont(texttype, klass),
        )
        self.cleared = False

    def GetSelectedText(self):
        return self.textbrowser.textCursor().selectedText()

    def setdisplayrank(self, type):
        pass

    def append(
        self,
        texttype: TextType,
        name,
        text,
        tag: "list[WordSegResult]",
        color: ColorControl,
        klass,
    ):
        if self.checkskip(texttype):
            return
        text = self.checkaddname(name, text)
        if len(tag):
            isshowhira = globalconfig["isshowhira"]
            font = self._createqfont(texttype, klass)
            tag = list(WordSegResultX.fromW(word) for word in tag)
            textlines, linetags = self._splitlinestags(font, tag, text)
            text = "\n".join(textlines)
            tag = self._join_tags(linetags, True)
            tagshow = tag if isshowhira else []
        else:
            tagshow = []
        self._textbrowser_append(texttype, text, tagshow, color, klass)
        if len(tag):
            self.addsearchwordmask(tag)
        self.cleared = False

    def _getqalignment(self, atcenter):
        return Qt.AlignmentFlag.AlignCenter if atcenter else Qt.AlignmentFlag.AlignLeft

    def _textbrowser_append(
        self, texttype: TextType, text: str, tag: list, color: ColorControl, klass: str
    ):
        self.textbrowser.document().blockSignals(True)
        font = self._createqfont(texttype, klass)
        self._setnextfont(font, self.cleared)
        self.textbrowser.setAlignment(self._getqalignment(self.showatcenterflag))

        _space = "" if self.cleared else "\n"
        blockcount = 0 if self.cleared else self.textbrowser.document().blockCount()
        hastag = len(tag) > 0
        self.textbrowser.insertPlainText(_space + text)
        blockcount_after = self.textbrowser.document().blockCount()

        if hastag:
            self._setlineheight_x(blockcount, blockcount_after, self._split_tags(tag))
        else:
            self._setlineheight(blockcount, blockcount_after, texttype, klass)
        self.textbrowser.document().blockSignals(False)
        self.textbrowser.document().contentsChanged.emit()
        if hastag:
            self._addtag(tag)
        self._showyinyingtext(blockcount, blockcount_after, color, font)

    def _join_tags(self, tag: "list[list[WordSegResultX]]", space):
        tags: "list[WordSegResultX]" = []
        for i in range(len(tag)):
            if i != 0 and space:
                tags.append(WordSegResultX("\n", word_X="\n"))
            tags += tag[i]
        return tags

    def _split_tags(self, tag: "list[WordSegResultX]"):
        taglines: "list[list[WordSegResultX]]" = [[]]
        for word in tag:
            if word.word == "\n":
                taglines.append([])
                continue
            else:
                taglines[-1].append(word)
        return taglines

    def _splitlinestags(self, font, tag: "list[WordSegResultX]", text: str):
        lines = text.split("\n")
        textlines = []
        taglines = self._join_tags(self._split_tags(tag), False)
        newtags: "list[list[WordSegResultX]]" = []
        for linetext in lines:

            layout = QTextLayout()
            layout.setFont(font)
            layout.setTextOption(QTextOption(Qt.AlignmentFlag.AlignLeft))
            layout.setText(linetext)
            layout.beginLayout()
            newtag: "list[WordSegResultX]" = []
            __ = ""
            while True:
                line = layout.createLine()
                if not line.isValid():
                    break
                line.setLineWidth(self.width())
                textlines.append(
                    linetext[line.textStart() : line.textStart() + line.textLength()]
                )
                while len(taglines) and len(__) < len(textlines[-1]):
                    __ += taglines[0].word
                    taglines[0].word_X = taglines[0].word
                    newtag.append(taglines[0])
                    taglines = taglines[1:]
                if newtag and (len(__) != len(textlines[-1])):
                    orig = newtag[-1].word
                    l1 = len(orig) - (len(__) - len(textlines[-1]))
                    sub = orig[:l1]
                    end = orig[l1:]
                    __ = end
                    if newtag[-1].word == newtag[-1].kana:
                        newtag[-1].word_X = sub
                        newtag[-1].kana = sub
                        _tag = newtag[-1].copy()
                        _tag.word_X = end
                        _tag.kana = end
                        _tag.ref = True
                        newtag.append(WordSegResultX("\n", word_X="\n"))
                        newtag.append(_tag)
                    else:
                        hiras = [newtag[-1].kana, ""]
                        if len(end) > len(sub):
                            hiras.reverse()
                        newtag[-1].word_X = sub
                        newtag[-1].kana = hiras[0]
                        _tag = newtag[-1].copy()
                        _tag.word_X = end
                        _tag.kana = hiras[1]
                        _tag.ref = True
                        newtag.append(WordSegResultX("\n", word_X="\n"))
                        newtag.append(_tag)
                else:
                    __ = ""
                newtags.append(newtag)
                newtag = []
            if len(newtag):
                newtags.append(newtag)
            layout.endLayout()

        newtag = []
        for i in range(len(newtags)):
            if i != 0:
                if not hasbreak:
                    newtag.append(WordSegResultX("\n", word_X="\n"))
            newtag += newtags[i]
            hasbreak = False
            for _ in newtags[i]:
                if _.word_X == "\n":
                    hasbreak = True
                    break
        return textlines, self._split_tags(newtag)

    def _checkwordhastag(self, word: WordSegResultX):
        if word.hidekana:
            return False
        if word.kana == word.word_X:
            return False
        if not (word.word_X.strip()):
            return False
        if not (word.kana and word.kana.strip()):
            return False
        return True

    def getlhfordict(self, dic):
        return 100 * (
            1 if dic.get("lineHeightNormal", True) else dic.get("lineHeight", 1)
        )

    def _setlineheight_x(self, b1, b2, linetags: "list[list[WordSegResultX]]"):
        fha, _ = self._getfh(True)

        for i in range(b1, b2):
            _fha = 0
            for word in linetags[i - b1]:

                if not self._checkwordhastag(word):
                    continue
                _fha = fha
                break
            if i == 0 and _fha:
                self.textbrowser.move(0, int(fha))
                self.atback_color.move(0, int(fha))
            b = self.textbrowser.document().findBlockByNumber(i)
            tf = b.blockFormat()
            tf.setTopMargin(_fha + globalconfig["lineheights"]["marginTop"])
            tf.setLineHeight(
                self.getlhfordict(globalconfig["lineheights"]),
                self.ProportionalHeight,
            )
            tf.setBottomMargin(globalconfig["lineheights"]["marginBottom"])
            self.textcursor.setPosition(b.position())
            self.textcursor.setBlockFormat(tf)
            self.textbrowser.setTextCursor(self.textcursor)
    @property
    def ProportionalHeight(self):
        _= QTextBlockFormat.LineHeightTypes.ProportionalHeight
        if not isqt5:
            _= _.value
        return _
        
    def _setlineheight(self, b1, b2, texttype: TextType, klass: str):
        if texttype == TextType.Origin:
            fh = globalconfig["lineheights"]
        else:
            fh = globalconfig["lineheightstrans"]
            if klass:
                data = globalconfig["fanyi"][klass].get("privatefont", {})
                if not data.get("lineheight_df", True):
                    fh = data
        for i in range(b1, b2):
            b = self.textbrowser.document().findBlockByNumber(i)
            tf = b.blockFormat()
            tf.setTopMargin(fh.get("marginTop", 0))
            tf.setLineHeight(self.getlhfordict(fh), self.ProportionalHeight)
            tf.setBottomMargin(fh.get("marginBottom", 0))
            self.textcursor.setPosition(b.position())
            self.textcursor.setBlockFormat(tf)
            self.textbrowser.setTextCursor(self.textcursor)

    def _getcurrpointer(self):
        return self.textcursor.position()

    def _insertatpointer(self, pointer, text):
        self.textcursor.setPosition(pointer)
        self.textbrowser.setTextCursor(self.textcursor)
        self.textbrowser.setTextColor(self.tranparentcolor)
        self.textbrowser.insertPlainText(text)

    def _deletebetween(self, p1, p2):
        self.textcursor.setPosition(p1, QTextCursor.MoveMode.MoveAnchor)
        self.textcursor.setPosition(p2, QTextCursor.MoveMode.KeepAnchor)
        self.textcursor.removeSelectedText()

    def _showyinyingtext2(
        self, color: ColorControl, iter_context_class, pos, text, font: QFont
    ):
        if iter_context_class not in self.iteryinyinglabelsave:
            self.iteryinyinglabelsave[iter_context_class] = []
        for label in self.iteryinyinglabelsave[iter_context_class]:
            label.hide()

        maxh = self.maxvisheight
        subtext = []
        subpos = []
        lastpos = None
        posx = pos
        for i in range(len(text)):
            self.textcursor.setPosition(posx)
            posx += 1
            tl1 = self.textbrowser.cursorRect(self.textcursor).topLeft()
            if tl1.y() > maxh:
                break
            if lastpos is None or tl1.y() != lastpos.y():
                lastpos = tl1
                subpos.append(lastpos)
                subtext.append("")

            if text[i] != "\n":
                subtext[-1] += text[i]
        collects = []
        for i in range(len(subtext)):

            if i >= len(self.iteryinyinglabelsave[iter_context_class]):
                self.iteryinyinglabelsave[iter_context_class].append(
                    self.currentclass(self.toplabel2)
                )
            _ = self.iteryinyinglabelsave[iter_context_class][i]
            if (_.text() != subtext[i]) or (_.font().toString != font.toString()):
                _.setColor(color)
                _.setText(subtext[i])
                _.setFont(font)
                _.adjustSize()
            _.move(subpos[i].x(), subpos[i].y() + self.labeloffset_y)
            _.show()

        self.textcursor.setPosition(pos)
        self.textbrowser.setTextCursor(self.textcursor)
        tl1 = self.textbrowser.cursorRect(self.textcursor).topLeft()
        thisy0 = tl1.y()
        for label in self.yinyinglabels:
            if label.isVisible() == False:
                continue
            if label.y() >= thisy0:
                collects.append(label)
        for klass in self.iteryinyinglabelsave:
            if klass == iter_context_class:
                continue
            for label in self.iteryinyinglabelsave[klass]:
                if label.isVisible() == False:
                    continue
                if label.y() >= thisy0:
                    collects.append(label)
        collects.sort(key=lambda label: label.y())
        doc = self.textbrowser.document()
        block = doc.findBlockByNumber(0)
        collecti = 0
        for blocki in range(0, self.textbrowser.document().blockCount()):
            block = doc.findBlockByNumber(blocki)
            layout = block.layout()
            blockstart = block.position()
            lc = layout.lineCount()
            if blockstart < posx:
                continue
            for lineii in range(lc):
                line = layout.lineAt(lineii)

                s = line.textStart()
                l = line.textLength()
                if l == 0:
                    continue
                self.textcursor.setPosition(blockstart + s)
                self.textbrowser.setTextCursor(self.textcursor)
                tl1 = self.textbrowser.cursorRect(self.textcursor).topLeft()
                if tl1.y() > maxh:
                    return
                collects[collecti].move(tl1.x(), tl1.y() + self.labeloffset_y)
                collecti += 1

    @property
    def maxvisheight(self):
        return QApplication.primaryScreen().virtualGeometry().height() * 2

    def _showyinyingtext(self, b1, b2, color: ColorControl, font: QFont):
        linei = self.yinyingposline

        doc = self.textbrowser.document()
        block = doc.findBlockByNumber(0)
        maxh = self.maxvisheight
        for blocki in range(b1, b2):
            block = doc.findBlockByNumber(blocki)
            layout = block.layout()
            blockstart = block.position()
            lc = layout.lineCount()
            for lineii in range(lc):
                line = layout.lineAt(lineii)

                s = line.textStart()
                l = line.textLength()
                if l == 0:
                    continue
                self.textcursor.setPosition(blockstart + s)
                self.textbrowser.setTextCursor(self.textcursor)
                tl1 = self.textbrowser.cursorRect(self.textcursor).topLeft()
                if tl1.y() > maxh:
                    self.yinyingposline = linei
                    return
                if self.yinyinglabels_idx >= len(self.yinyinglabels):
                    self.yinyinglabels.append(self.currentclass(self.toplabel2))
                _ = self.yinyinglabels[self.yinyinglabels_idx]
                self.yinyinglabels_idx += 1
                _.setColor(color)
                _.setText(block.text()[s : s + l])
                _.setFont(font)
                _.adjustSize()
                _.move(tl1.x(), tl1.y() + self.labeloffset_y)
                _.show()

                linei += 1
        self.yinyingposline = linei

    def _add_searchlabel(self, labeli: int, pos1, word, color: ColorControl):
        if labeli >= len(self.searchmasklabels_clicked):
            ql = FenciQLabel(self.atback_color)
            ql.setMouseTracking(True)
            self.searchmasklabels.append(ql)
            ql_1 = QLabel_w(ql)
            ql_1.setMouseTracking(True)
            ql.refmask = ql_1
            ql_1.setStyleSheet("background-color: rgba(0,0,0,0.01);")
            self.searchmasklabels_clicked.append(ql_1)
            ql = Qlabel_c(self.masklabel)
            ql.ref = ql_1
            ql.setMouseTracking(True)
            ql.setStyleSheet("background-color: rgba(0,0,0,0.01);")
            self.searchmasklabels_clicked2.append(ql)
        self.searchmasklabels_clicked[labeli].setGeometry(0, 0, pos1[2], pos1[3])
        self.searchmasklabels_clicked[labeli].word = word
        self.searchmasklabels_clicked2[labeli].setGeometry(*pos1)
        self.searchmasklabels_clicked2[labeli].word = word
        self.searchmasklabels[labeli].setGeometry(*pos1)
        self.searchmasklabels[labeli].setColor(color)
        self.showhideclick_i(labeli)

    def showhideclick(self, _=None):
        show = self._clickhovershow
        for i in range(self.searchmasklabels_clicked_num):
            self.searchmasklabels_clicked[i].setVisible(show)
            self.searchmasklabels_clicked2[i].setVisible(show)

    def showhideclick_i(self, i: int):
        show = self._clickhovershow
        self.searchmasklabels_clicked[i].setVisible(show)
        self.searchmasklabels_clicked2[i].setVisible(show)
        self.searchmasklabels[i].setVisible(True)

    def addsearchwordmask(self, x: "list[WordSegResultX]"):
        if len(x) == 0:
            return
        pos = 0
        labeli = 0
        self.textcursor.setPosition(0)
        self.textbrowser.setTextCursor(self.textcursor)

        heigth, _ = self._getfh(False)
        for word in x:
            l = len(word.word_X)

            tl1 = self.textbrowser.cursorRect(self.textcursor).topLeft()

            pos += l
            self.textcursor.setPosition(pos)
            self.textbrowser.setTextCursor(self.textcursor)

            if word.isdeli or word.isshit:
                continue
            tl2 = self.textbrowser.cursorRect(self.textcursor).bottomRight()
            color = FenciColor(word)
            dyna_h = int((heigth + tl2.y() - tl1.y()) / 2)
            pos1 = tl1.x(), tl1.y(), tl2.x() - tl1.x(), dyna_h
            self._add_searchlabel(labeli, pos1, word, color)
            if word.ref:
                self.searchmasklabels_clicked[labeli - 1].company = (
                    self.searchmasklabels_clicked[labeli]
                )
                self.searchmasklabels_clicked[labeli].company = (
                    self.searchmasklabels_clicked[labeli - 1]
                )
                self.searchmasklabels_clicked2[labeli - 1].company = (
                    self.searchmasklabels_clicked2[labeli]
                )
                self.searchmasklabels_clicked2[labeli].company = (
                    self.searchmasklabels_clicked2[labeli - 1]
                )
            else:
                self.searchmasklabels_clicked[labeli].company = None
                self.searchmasklabels_clicked2[labeli].company = None
            labeli += 1
            self.searchmasklabels_clicked_num += 1

    def _getfh(self, half, texttype: TextType = TextType.Origin, getfm=False):

        font = QFont()
        fm, fs, bold = self._getfontinfo(texttype)
        font.setBold(bold)
        font.setFamily(fm)
        if half:
            fs *= globalconfig["kanarate"]
        font.setPointSizeF(fs)
        fm = QFontMetricsF(font)
        if getfm:
            return fm
        return fm.height(), font

    @property
    def labeloffset_y(self):
        return self.textbrowser.y()

    def _addtag(self, x: "list[WordSegResultX]"):
        pos = 0
        fha, fonthira = self._getfh(True)
        fontori_m = self._getfh(False, getfm=True)

        self.settextposcursor(pos)
        savetaglabels_idx = 0
        lines = [[]]
        maxh = self.maxvisheight
        for word in x:
            l = len(word.word_X)
            tl1 = self.textbrowser.cursorRect(self.textcursor).topLeft()
            self.settextposcursor(pos + l)
            pos += l

            if not self._checkwordhastag(word):
                continue
            tl2 = self.textbrowser.cursorRect(self.textcursor).topLeft()
            if tl2.y() > maxh:
                break
            _ = self.solvejiaminglabel(
                savetaglabels_idx, word, fonthira, fontori_m, tl1, fha
            )
            if len(lines[-1]) and (_.y() != lines[-1][-1].y()):
                lines.append([])
            lines[-1].append(_)
            savetaglabels_idx += 1
        for line in lines:
            self._dyna_merge_label(line)

    def has_intersection(self, interval1, interval2):
        start = max(interval1[0], interval2[0])
        end = min(interval1[1], interval2[1])

        if start <= end:
            return True
        else:
            return None

    def _dyna_merge_label(self, line: "list[base]"):
        if len(line) <= 0:
            return
        if line[0].x() < 0:
            line[0].move(0, line[0].y())
        if len(line) <= 1:
            return
        rects = [(label.realx(), label.realx() + label.realw()) for label in line]

        for i in range(len(line) - 1):
            if not self.has_intersection(rects[i], rects[i + 1]):
                continue
            w1 = rects[i][1] - rects[i][0]
            w2 = rects[i + 1][1] - rects[i + 1][0]
            c1 = rects[i][1] + rects[i][0]
            c2 = rects[i + 1][1] + rects[i + 1][0]
            center = (c1 * w1 + c2 * w2) / (w1 + w2)
            center /= 2
            line[i].setText(line[i].text() + line[i + 1].text())
            line[i].adjustSize()
            line[i].move(int(center - line[i].width() / 2), line[i].y())
            line[i + 1].hide()
            return self._dyna_merge_label(line[: i + 1] + line[i + 2 :])

    def settextposcursor(self, pos):
        self.textcursor.setPosition(pos)
        self.textbrowser.setTextCursor(self.textcursor)

    def solvejiaminglabel(
        self, idx, word: WordSegResultX, font, fontori_m: QFontMetricsF, tl1, fha
    ):
        if idx >= len(self.savetaglabels):
            self.savetaglabels.append(self.currentclass(self.atback2))
        _: base = self.savetaglabels[idx]
        _.setColor(SpecialColor.KanaColor)
        _.setText(word.kana)
        origin = word.word_X
        w_origin = fontori_m.size(0, origin).width()
        y = tl1.y() - fha
        center = tl1.x() + w_origin / 2
        _.setFont(font)
        _.adjustSize()
        w = _.realw()
        _.move(int(center - w / 2), y + self.labeloffset_y)
        _.show()
        return _

    def clear(self):
        self.resets()
        self.yinyingposline = 0
        self.textbrowser.clear()
        self.cleared = True
        self.saveiterclasspointer.clear()
        self.textbrowser.move(0, 0)
        self.atback_color.move(0, 0)

    def sethovercolor(self, color):
        for _ in reference:
            try:
                _.setStyleSheet("background-color: " + color)
            except:
                pass
