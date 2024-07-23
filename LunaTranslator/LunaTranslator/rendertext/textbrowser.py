from qtsymbols import *
from myutils.config import globalconfig, static_data
from rendertext.somefunctions import dataget
import gobject, functools, importlib
from traceback import print_exc
from rendertext.textbrowser_imp.base import base


class Qlabel_c(QLabel):

    def mousePressEvent(self, ev):
        self.pr = True
        return super().mousePressEvent(ev)

    def mouseMoveEvent(self, ev):
        pass
        # return super().mouseMoveEvent(ev)

    def mouseReleaseEvent(self, event: QMouseEvent):
        try:
            if self.geometry().contains(self.parent().mapFromGlobal(QCursor.pos())):
                try:
                    if self.pr:
                        if event.button() == Qt.MouseButton.RightButton:
                            self.callback(True)
                        else:
                            self.callback(False)
                except:
                    print_exc()
            self.pr = False
        except:
            print_exc()
        return super().mouseReleaseEvent(event)

    def enterEvent(self, a0) -> None:
        if self.company:
            self.company.setStyleSheet("background-color: rgba(0,0,0,0.5);")
        self.setStyleSheet("background-color: rgba(0,0,0,0.5);")
        return super().enterEvent(a0)

    def leaveEvent(self, a0) -> None:
        if self.company:
            self.company.setStyleSheet("background-color: rgba(0,0,0,0.01);")
        self.setStyleSheet("background-color: rgba(0,0,0,0.01);")
        return super().leaveEvent(a0)


class TextBrowser(QWidget, dataget):
    contentsChanged = pyqtSignal(QSize)
    _padding = 5

    def __makeborder(self, size: QSize):
        # border是用来当可选取时，用来拖动的
        # webview2的绘制和qt的绘制不兼容，qt的半透明对他无效，必须缩放，否则遮挡，所以还是各写一份吧。
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
        self.textbrowser.resize(self.width(), sz.height())
        self.contentsChanged.emit(QSize(sz.width(), self.textbrowser.y() + sz.height()))

    def resizeEvent(self, event: QResizeEvent):
        self.atback2.resize(event.size())
        self.atback_color.resize(event.size())
        self.toplabel2.resize(event.size())
        self.masklabel.resize(event.size())

        self.__makeborder(event.size())

    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.atback_color = QLabel(self)
        self.atback_color.setMouseTracking(True)
        self.atback2 = QLabel(self)
        self.atback2.setMouseTracking(True)

        self.toplabel2 = QLabel(self)
        self.toplabel2.setMouseTracking(True)
        self.textbrowser = QTextBrowser(self)
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
        self.masklabel = QLabel(self.textbrowser)
        self.masklabel.setMouseTracking(True)
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
        self.savetaglabels = []
        self.searchmasklabels_clicked = []
        self.searchmasklabels = []
        self.backcolorlabels = []

        self.yinyinglabels = []
        self.yinyinglabels_idx = 0

        self.yinyingpos = 0
        self.yinyingposline = 0
        self.lastcolor = None
        self.blockcount = 0
        self.iteryinyinglabelsave = {}
        self.saveiterclasspointer = {}
        self.resets1()

    def resets1(self):
        self.currenttype = globalconfig["rendertext_using_internal"]["textbrowser"]
        if self.currenttype not in static_data["textrender"]["textbrowser"]:
            self.currenttype = static_data["textrender"]["textbrowser"][0]
            globalconfig["rendertext_using_internal"]["textbrowser"] = static_data[
                "textrender"
            ]["textbrowser"][0]

        __ = importlib.import_module(f"rendertext.textbrowser_imp.{self.currenttype}")

        self.currentclass = functools.partial(__.TextLine, self.currenttype)

    def resets(self):

        for label in self.searchmasklabels:
            label.hide()
        for label in self.searchmasklabels_clicked:
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
        for label in self.searchmasklabels:
            label.deleteLater()
        self.searchmasklabels.clear()
        for label in self.searchmasklabels_clicked:
            label.deleteLater()
        self.searchmasklabels_clicked.clear()
        for label in self.savetaglabels:
            label.deleteLater()

        self.savetaglabels.clear()
        self.yinyinglabels_idx = 0
        for label in self.yinyinglabels:
            label.deleteLater()
        self.yinyinglabels.clear()
        for labels in self.iteryinyinglabelsave.values():
            for label in labels:
                label.deleteLater()
        self.iteryinyinglabelsave.clear()

    def setselectable(self, b):
        self.masklabel.setHidden(b)

    def _createqfont(self, origin):

        fm, fs, bold = self._getfontinfo(origin)
        font = QFont()
        font.setFamily(fm)
        font.setPointSizeF(fs)
        font.setBold(bold)
        return font

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

    def iter_append(self, iter_context_class, origin, atcenter, text, color, cleared):
        self._textbrowser_iter_append(
            iter_context_class, origin, atcenter, text, color, cleared
        )

    def _textbrowser_iter_append(
        self, iter_context_class, origin, atcenter, text, color, cleared
    ):
        if iter_context_class not in self.saveiterclasspointer:
            self._textbrowser_append(origin, atcenter, "", [], color, cleared)
            self.saveiterclasspointer[iter_context_class] = {
                "currtext": "",
                "curr": self._getcurrpointer(),
                "start": self._getcurrpointer(),
            }

        currbefore = self.saveiterclasspointer[iter_context_class]["curr"]
        currlen = len(self.saveiterclasspointer[iter_context_class]["currtext"])
        if len(text) < currlen:
            self._deletebetween(
                self.saveiterclasspointer[iter_context_class]["start"] + len(text),
                self.saveiterclasspointer[iter_context_class]["curr"],
            )
        else:
            newtext = text[currlen:]
            self._insertatpointer(
                self.saveiterclasspointer[iter_context_class]["start"] + currlen,
                newtext,
            )

        self.saveiterclasspointer[iter_context_class]["currtext"] = text
        currcurrent = self._getcurrpointer()
        self.saveiterclasspointer[iter_context_class]["curr"] = currcurrent
        currchange = currcurrent - currbefore
        for klass in self.saveiterclasspointer:
            if klass == iter_context_class:
                continue
            if self.saveiterclasspointer[klass]["curr"] > currbefore:
                self.saveiterclasspointer[klass]["curr"] += currchange
                self.saveiterclasspointer[klass]["start"] += currchange

        self._showyinyingtext2(
            color,
            iter_context_class,
            self.saveiterclasspointer[iter_context_class]["start"],
            text,
            self._createqfont(origin),
        )

    def append(self, origin, atcenter, text, tag, flags, color, cleared):
        isshowhira, isshow_fenci, isfenciclick = flags
        self._textbrowser_append(
            origin, atcenter, text, tag if isshowhira else [], color, cleared
        )
        if isshow_fenci or isfenciclick:
            self.addsearchwordmask(
                isshow_fenci,
                isfenciclick,
                tag,
                text,
                gobject.baseobject.clickwordcallback,
            )

    def _getqalignment(self, atcenter):
        return Qt.AlignmentFlag.AlignCenter if atcenter else Qt.AlignmentFlag.AlignLeft

    def _textbrowser_append(self, origin, atcenter, text, tag, color, cleared):
        font = self._createqfont(origin)
        self._setnextfont(font, cleared)
        self.textbrowser.setAlignment(self._getqalignment(atcenter))

        if cleared:
            _space = ""
            self.blockcount = 0
            b1 = 0
        else:
            _space = "\n"
            b1 = self.textbrowser.document().blockCount()
        self.textbrowser.insertPlainText(_space + text)

        b2 = self.textbrowser.document().blockCount()
        if origin:
            fh = globalconfig["extra_space"]
        else:
            fh = globalconfig["extra_space_trans"]
        for i in range(self.blockcount, self.textbrowser.document().blockCount()):
            b = self.textbrowser.document().findBlockByNumber(i)
            tf = b.blockFormat()
            tf.setLineHeight(fh, LineHeightTypes.LineDistanceHeight)
            self.textcursor.setPosition(b.position())
            self.textcursor.setBlockFormat(tf)
            self.textbrowser.setTextCursor(self.textcursor)
        self.blockcount = self.textbrowser.document().blockCount()

        if len(tag) > 0:
            self._addtag(tag)
        self._showyinyingtext(b1, b2, color, font)

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

    def _showyinyingtext2(self, color, iter_context_class, pos, text, font):
        if iter_context_class not in self.iteryinyinglabelsave:
            self.iteryinyinglabelsave[iter_context_class] = []

        for label in self.iteryinyinglabelsave[iter_context_class]:
            label.hide()

        subtext = []
        subpos = []
        lastpos = None
        posx = pos
        for i in range(len(text)):
            self.textcursor.setPosition(posx)
            posx += 1
            tl1 = self.textbrowser.cursorRect(self.textcursor).topLeft()
            if lastpos is None or tl1.y() != lastpos.y() or text[i] == "\n":
                lastpos = tl1
                subpos.append(lastpos)
                subtext.append("")
            subtext[-1] += text[i]

        collects = []
        for i in range(len(subtext)):
            if i >= len(self.iteryinyinglabelsave[iter_context_class]):
                self.iteryinyinglabelsave[iter_context_class].append(
                    self.currentclass(self.toplabel2)
                )
            _ = self.iteryinyinglabelsave[iter_context_class][i]
            _.setColor(color)
            _.setText(subtext[i])
            _.setFont(font)
            _.adjustSize()
            _.move(
                subpos[i].x(), subpos[i].y() + self.textbrowser.y() - self.toplabel2.y()
            )
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
                collects[collecti].move(tl1)
                collecti += 1

    def _showyinyingtext(self, b1, b2, color, font):
        linei = self.yinyingposline

        doc = self.textbrowser.document()
        block = doc.findBlockByNumber(0)

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

                if self.yinyinglabels_idx >= len(self.yinyinglabels):
                    self.yinyinglabels.append(self.currentclass(self.toplabel2))
                _ = self.yinyinglabels[self.yinyinglabels_idx]
                self.yinyinglabels_idx += 1

                _.setColor(color)
                _.setText(block.text()[s : s + l])
                _.setFont(font)
                _.adjustSize()
                _.move(tl1.x(), tl1.y() + self.textbrowser.y() - self.toplabel2.y())
                _.show()
                linei += 1
        self.yinyingposline = linei

    def addsearchwordmask(self, isshow_fenci, isfenciclick, x, raw, callback=None):
        if len(x) == 0:
            return
        # print(x)
        pos = 0
        labeli = 0
        self.textcursor.setPosition(0)
        self.textbrowser.setTextCursor(self.textcursor)

        idx = 0
        heigth, _ = self._getfh(False)
        for word in x:
            idx += 1
            l = len(word["orig"])
            tl1 = self.textbrowser.cursorRect(self.textcursor).topLeft()

            tl4 = self.textbrowser.cursorRect(self.textcursor).bottomRight()

            if True:
                self.textcursor.setPosition(pos + l)
                self.textbrowser.setTextCursor(self.textcursor)

                tl2 = self.textbrowser.cursorRect(self.textcursor).bottomRight()
                tl3 = self.textbrowser.cursorRect(self.textcursor).topLeft()
                color = self._randomcolor(word)
                if len(word["orig"].strip()):
                    if labeli >= len(self.searchmasklabels) - 1:
                        ql = QLabel(self.atback_color)
                        ql.setMouseTracking(True)
                        self.searchmasklabels.append(ql)

                        ql = Qlabel_c(self.textbrowser)
                        ql.setMouseTracking(True)
                        ql.setStyleSheet("background-color: rgba(0,0,0,0.01);")
                        self.searchmasklabels_clicked.append(ql)

                        ql = QLabel(self.atback_color)
                        ql.setMouseTracking(True)
                        self.searchmasklabels.append(ql)

                        ql = Qlabel_c(self.textbrowser)
                        ql.setMouseTracking(True)
                        ql.setStyleSheet("background-color: rgba(0,0,0,0.01);")
                        self.searchmasklabels_clicked.append(ql)
                    if tl1.y() != tl3.y():
                        for __i in range(len(word["orig"])):
                            self.textcursor.setPosition(pos + __i)
                            self.textbrowser.setTextCursor(self.textcursor)
                            _tl = self.textbrowser.cursorRect(self.textcursor).topLeft()
                            if _tl.y() != tl1.y():
                                break
                        self.textcursor.setPosition(pos + l)
                        self.textbrowser.setTextCursor(self.textcursor)
                        __fm = self._getfh(False, getfm=True)
                        w1 = int(__fm.size(0, word["orig"][:__i]).width())
                        w2 = int(__fm.size(0, word["orig"][__i:]).width())

                        pos1 = (
                            tl1.x() + 1,
                            tl1.y(),
                            w1 - 2,
                            int(heigth),
                        )
                        pos2 = tl3.x() + 1 - w2, tl3.y(), w2 - 2, int(heigth)

                        if isfenciclick:
                            self.searchmasklabels_clicked[labeli].setGeometry(*pos1)
                            self.searchmasklabels_clicked[labeli].show()
                            self.searchmasklabels_clicked[labeli].company = (
                                self.searchmasklabels_clicked[labeli + 1]
                            )
                            if callback:
                                self.searchmasklabels_clicked[labeli].callback = (
                                    functools.partial(callback, (word))
                                )

                            self.searchmasklabels_clicked[labeli + 1].setGeometry(*pos2)
                            self.searchmasklabels_clicked[labeli + 1].show()
                            self.searchmasklabels_clicked[labeli + 1].company = (
                                self.searchmasklabels_clicked[labeli]
                            )
                            if callback:
                                self.searchmasklabels_clicked[labeli + 1].callback = (
                                    functools.partial(callback, (word))
                                )

                        if isshow_fenci and color:
                            self.searchmasklabels[labeli].setGeometry(*pos1)
                            self.searchmasklabels[labeli].setStyleSheet(
                                "background-color: {};".format(color)
                            )
                            self.searchmasklabels[labeli].show()

                            self.searchmasklabels[labeli + 1].setGeometry(*pos2)
                            self.searchmasklabels[labeli + 1].setStyleSheet(
                                "background-color: {};".format(color)
                            )
                            self.searchmasklabels[labeli + 1].show()
                        labeli += 2
                    else:

                        pos1 = (
                            tl1.x() + 1,
                            tl1.y(),
                            tl2.x() - tl1.x() - 2,
                            int(heigth),
                        )
                        if isfenciclick:
                            self.searchmasklabels_clicked[labeli].setGeometry(*pos1)
                            self.searchmasklabels_clicked[labeli].company = None
                            self.searchmasklabels_clicked[labeli].show()
                            if callback:
                                self.searchmasklabels_clicked[labeli].callback = (
                                    functools.partial(callback, word)
                                )
                        if isshow_fenci and color:
                            self.searchmasklabels[labeli].setGeometry(*pos1)
                            self.searchmasklabels[labeli].setStyleSheet(
                                "background-color: {};".format(color)
                            )
                            self.searchmasklabels[labeli].show()
                        labeli += 1

                tl1 = tl3
                tl4 = tl2

                pos += l

    def _getfh(self, half, origin=True, getfm=False):

        font = QFont()
        fm, fs, bold = self._getfontinfo(origin)
        font.setBold(bold)
        font.setFamily(fm)
        if half:
            fs *= globalconfig["kanarate"]
        font.setPointSizeF(fs)
        fm = QFontMetricsF(font)
        if getfm:
            return fm
        return fm.height(), font

    def _addtag(self, x):
        pos = 0

        _, fontorig = self._getfh(False)
        fha, fonthira = self._getfh(True)
        self.textbrowser.move(0, int(fha))
        self.atback_color.move(0, int(fha))
        ldh = max(globalconfig["extra_space"], int(fha / 2))
        for i in range(0, self.textbrowser.document().blockCount()):
            b = self.textbrowser.document().findBlockByNumber(i)

            tf = b.blockFormat()
            tf.setLineHeight(ldh, LineHeightTypes.LineDistanceHeight)
            self.textcursor.setPosition(b.position())
            self.textcursor.setBlockFormat(tf)
            self.textbrowser.setTextCursor(self.textcursor)
        x = self.nearmerge(x, pos, fonthira, fontorig)
        self.settextposcursor(pos)
        savetaglabels_idx = 0
        for word in x:
            l = len(word["orig"])

            tl1 = self.textbrowser.cursorRect(self.textcursor).topLeft()

            self.settextposcursor(pos + l)
            pos += l

            tl2 = self.textbrowser.cursorRect(self.textcursor).topLeft()
            if word["hira"] == word["orig"]:
                continue
            # print(tl1,tl2,word['hira'],self.textbrowser.textCursor().position())
            if word["orig"] == " ":
                continue
            if savetaglabels_idx >= len(self.savetaglabels):
                self.savetaglabels.append(self.currentclass(self.atback2))
            self.solvejiaminglabel(
                self.savetaglabels[savetaglabels_idx], word, fonthira, tl1, tl2, fha
            )
            savetaglabels_idx += 1

    def settextposcursor(self, pos):
        self.textcursor.setPosition(pos)
        self.textbrowser.setTextCursor(self.textcursor)

    def nearmerge(self, x, startpos, fonthira, fontorig):
        pos = startpos
        linex = []
        newline = []
        self.settextposcursor(pos)
        _metrichira = QFontMetricsF(fonthira)
        _metricorig = QFontMetricsF(fontorig)
        for i, word in enumerate(x):
            word["orig_w"] = _metricorig.size(0, word["orig"]).width()
            word["hira_w"] = _metrichira.size(0, word["hira"]).width()
            # print(word['hira'],word['hira_w'])
            newline.append(word)

            l = len(word["orig"])
            tl1 = self.textbrowser.cursorRect(self.textcursor).topLeft()
            self.settextposcursor(pos + l)
            pos += l

            tl2 = self.textbrowser.cursorRect(self.textcursor).topLeft()

            # print(tl1,tl2,word['hira'],self.textbrowser.textCursor().position())

            if tl1.y() != tl2.y() or i == len(x) - 1:
                linex.append(newline)
                newline = []
        res = []
        for line in linex:

            while True:
                allnotbig = True
                newline = []
                canmerge = False
                for word in line:
                    if (
                        word["hira"] == word["orig"]
                        or word["hira"] == ""
                        or word["orig"] == ""
                    ):
                        newline.append(word.copy())
                        canmerge = False
                    else:
                        if (
                            len(newline) > 0
                            and canmerge
                            and (
                                word["hira_w"] + newline[-1]["hira_w"]
                                > word["orig_w"] + newline[-1]["orig_w"]
                            )
                        ):
                            # print(word['hira'],word['hira_w'],newline[-1]['hira_w'],word['orig_w'],newline[-1]['orig_w'])
                            newline[-1]["hira"] += word["hira"]
                            newline[-1]["orig"] += word["orig"]
                            newline[-1]["hira_w"] += word["hira_w"]
                            newline[-1]["orig_w"] += word["orig_w"]
                            allnotbig = False
                        else:
                            newline.append(word.copy())
                        canmerge = True
                line = newline
                if allnotbig:
                    break
            res += newline
            newline = []
        self.settextposcursor(startpos)
        return res

    def solvejiaminglabel(self, _: base, word, font, tl1, tl2, fh):
        color = self._getkanacolor()
        _.setColor(color)
        _.setText(word["hira"])
        _.setFont(font)
        _.adjustSize()
        w = _.width()

        if tl1.y() != tl2.y():
            # print(label,word)
            x = tl1.x()
            if x + w / 2 < self.textbrowser.width():
                x = tl1.x()
                y = tl1.y() - fh
            else:
                x = tl2.x() - w
                y = tl2.y() - fh
        else:
            x = tl1.x() / 2 + tl2.x() / 2 - w / 2
            y = tl2.y() - fh

        _.move(x, y + self.textbrowser.y() - self.toplabel2.y())

        _.show()
        return _

    def clear(self):
        self.resets()
        self.yinyingpos = 0
        self.yinyingposline = 0
        self.textbrowser.clear()

        self.saveiterclasspointer.clear()

        self.textbrowser.move(0, 0)
        self.atback_color.move(0, 0)
