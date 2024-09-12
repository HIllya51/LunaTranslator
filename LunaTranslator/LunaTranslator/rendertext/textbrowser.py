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
            if self.rect().contains(event.pos()):
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
        visheight = int(sz.height() + self.extra_height)
        self.textbrowser.resize(self.width(), visheight)
        self.contentsChanged.emit(QSize(sz.width(), visheight + self.labeloffset_y))

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

        self.yinyingposline = 0
        self.lastcolor = None
        self.iteryinyinglabelsave = {}
        self.saveiterclasspointer = {}
        self.extra_height = 0
        self.trace = []
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

    def showhideorigin(self, show):
        traces = self.trace.copy()
        self.clear()
        for t, trace in traces:
            if t == 0:
                self.append(*trace)
            elif t == 1:
                self.iter_append(*trace)

    def iter_append(self, iter_context_class, origin, atcenter, text, color):
        self.trace.append((1, (iter_context_class, origin, atcenter, text, color)))
        if iter_context_class not in self.saveiterclasspointer:
            self._textbrowser_append(origin, atcenter, "", [], color)
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

    def append(self, origin, atcenter, text, tag, flags, color):
        self.trace.append((0, (origin, atcenter, text, tag, flags, color)))
        if origin and not globalconfig["isshowrawtext"]:
            return
        isshowhira, isshow_fenci, isfenciclick = flags
        if len(tag):
            font = self._createqfont(origin)
            textlines, linetags = self._splitlinestags(font, tag, text)
            text = "\n".join(textlines)
            tag = self._join_tags(linetags, True)
        self._textbrowser_append(
            origin, atcenter, text, tag if isshowhira else [], color
        )
        if isshow_fenci or isfenciclick:
            self.addsearchwordmask(isshow_fenci, isfenciclick, tag)

    def _getqalignment(self, atcenter):
        return Qt.AlignmentFlag.AlignCenter if atcenter else Qt.AlignmentFlag.AlignLeft

    def _textbrowser_append(self, origin, atcenter, text: str, tag: list, color):
        self.textbrowser.document().blockSignals(True)
        font = self._createqfont(origin)
        cleared = len(self.textbrowser.toPlainText()) == 0
        self._setnextfont(font, cleared)
        self.textbrowser.setAlignment(self._getqalignment(atcenter))

        _space = "" if cleared else "\n"
        blockcount = 0 if cleared else self.textbrowser.document().blockCount()
        hastag = len(tag) > 0
        self.textbrowser.insertPlainText(_space + text)
        blockcount_after = self.textbrowser.document().blockCount()

        if hastag:
            self._setlineheight_x(blockcount, blockcount_after, self._split_tags(tag))
        else:
            self._setlineheight(blockcount, blockcount_after, origin)
        self.textbrowser.document().blockSignals(False)
        self.textbrowser.document().contentsChanged.emit()
        if hastag:
            self._addtag(tag)
        self._showyinyingtext(blockcount, blockcount_after, color, font)

    def _join_tags(self, tag, space):
        tags = []
        for i in range(len(tag)):
            if i != 0 and space:
                tags.append({"orig_X": "\n", "orig": "\n", "hira": "\n"})
            tags += tag[i]
        return tags

    def _split_tags(self, tag):
        taglines = [[]]
        for word in tag:
            if word["orig"] == "\n":
                taglines.append([])
                continue
            else:
                taglines[-1].append(word)
        return taglines

    def _splitlinestags(self, font, tag, text: str):
        lines = text.split("\n")
        textlines = []
        taglines = self._join_tags(self._split_tags(tag), False)
        newtags = []
        for linetext in lines:

            layout = QTextLayout()
            layout.setFont(font)
            layout.setTextOption(QTextOption(Qt.AlignLeft))
            layout.setText(linetext)
            layout.beginLayout()
            newtag = []
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
                    __ += taglines[0]["orig"]
                    taglines[0]["orig_X"] = taglines[0]["orig"]
                    newtag.append(taglines[0])
                    taglines = taglines[1:]
                if len(__) != len(textlines[-1]):
                    orig = newtag[-1]["orig"]
                    l1 = len(orig) - (len(__) - len(textlines[-1]))
                    sub = orig[:l1]
                    end = orig[l1:]
                    __ = end
                    if newtag[-1]["orig"] == newtag[-1]["hira"]:
                        newtag[-1].update({"orig_X": sub, "hira": sub})
                        _tag = newtag[-1].copy()
                        _tag.update({"orig_X": end, "hira": end, "ref": True})
                        newtag.append({"orig_X": "\n", "orig": "\n", "hira": ""})
                        newtag.append(_tag)
                    else:
                        hiras = [newtag[-1]["hira"], ""]
                        if len(end) > len(sub):
                            hiras.reverse()
                        newtag[-1].update({"orig_X": sub, "hira": hiras[0]})
                        _tag = newtag[-1].copy()
                        _tag.update({"orig_X": end, "hira": hiras[1], "ref": True})
                        newtag.append({"orig_X": "\n", "orig": "\n", "hira": ""})
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
                    newtag.append({"orig_X": "\n", "orig": "\n", "hira": "\n"})
            newtag += newtags[i]
            hasbreak = False
            for _ in newtags[i]:
                if _["orig_X"] == "\n":
                    hasbreak = True
                    break
        return textlines, self._split_tags(newtag)

    def _checkwordhastag(self, word):
        if word["hira"] == word["orig_X"]:
            return False
        if word["orig_X"].strip() == "":
            return False
        if word["hira"].strip() == "":
            return False
        return True

    def _setlineheight_x(self, b1, b2, linetags):
        fh = globalconfig["extra_space"]
        fha, _ = self._getfh(True)

        self.extra_height = fha
        if fh < 0:
            self.extra_height = -fh + self.extra_height
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
            tf.setTopMargin(_fha)
            tf.setLineHeight(fh, LineHeightTypes.LineDistanceHeight)
            self.textcursor.setPosition(b.position())
            self.textcursor.setBlockFormat(tf)
            self.textbrowser.setTextCursor(self.textcursor)

    def _setlineheight(self, b1, b2, origin):
        if origin:
            fh = globalconfig["extra_space"]
        else:
            fh = globalconfig["extra_space_trans"]
        if fh < 0:
            self.extra_height = -fh
        else:
            self.extra_height = 0
        for i in range(b1, b2):
            b = self.textbrowser.document().findBlockByNumber(i)
            tf = b.blockFormat()
            tf.setTopMargin(0)
            tf.setLineHeight(fh, LineHeightTypes.LineDistanceHeight)
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
                collects[collecti].move(tl1.x(), tl1.y() + self.labeloffset_y)
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
                _.move(tl1.x(), tl1.y() + self.labeloffset_y)
                _.show()
                linei += 1
        self.yinyingposline = linei

    def _add_searchlabel(self, isfenciclick, isshow_fenci, labeli, pos1, word, color):
        if labeli >= len(self.searchmasklabels_clicked):
            ql = QLabel(self.atback_color)
            ql.setMouseTracking(True)
            self.searchmasklabels.append(ql)

            ql = Qlabel_c(self.textbrowser)
            ql.setMouseTracking(True)
            ql.setStyleSheet("background-color: rgba(0,0,0,0.01);")
            self.searchmasklabels_clicked.append(ql)
        if isfenciclick:
            self.searchmasklabels_clicked[labeli].setGeometry(*pos1)
            self.searchmasklabels_clicked[labeli].show()
            clickfunction = word.get("clickfunction", None)
            if clickfunction:
                self.searchmasklabels_clicked[labeli].callback = clickfunction
            else:
                self.searchmasklabels_clicked[labeli].callback = functools.partial(
                    gobject.baseobject.clickwordcallback, word
                )
        if isshow_fenci and color:
            self.searchmasklabels[labeli].setGeometry(*pos1)
            self.searchmasklabels[labeli].setStyleSheet(
                "background-color: {};".format(color)
            )
            self.searchmasklabels[labeli].show()

    def addsearchwordmask(self, isshow_fenci, isfenciclick, x):
        if len(x) == 0:
            return
        pos = 0
        labeli = 0
        self.textcursor.setPosition(0)
        self.textbrowser.setTextCursor(self.textcursor)

        heigth, _ = self._getfh(False)
        for word in x:
            l = len(word["orig_X"])

            tl1 = self.textbrowser.cursorRect(self.textcursor).topLeft()

            pos += l
            self.textcursor.setPosition(pos)
            self.textbrowser.setTextCursor(self.textcursor)

            if len(word["hira"].strip()) == 0:
                continue
            tl2 = self.textbrowser.cursorRect(self.textcursor).bottomRight()
            color = self._randomcolor(word)
            dyna_h = int((heigth + tl2.y() - tl1.y()) / 2)
            pos1 = tl1.x() + 1, tl1.y(), tl2.x() - tl1.x() - 2, dyna_h
            self._add_searchlabel(isfenciclick, isshow_fenci, labeli, pos1, word, color)
            if word.get("ref", False):
                self.searchmasklabels_clicked[labeli - 1].company = (
                    self.searchmasklabels_clicked[labeli]
                )
                self.searchmasklabels_clicked[labeli].company = (
                    self.searchmasklabels_clicked[labeli - 1]
                )
            else:
                self.searchmasklabels_clicked[labeli].company = None
            labeli += 1

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

    @property
    def labeloffset_y(self):
        return self.textbrowser.y()

    def _addtag(self, x):
        pos = 0

        fha, fonthira = self._getfh(True)
        fontori_m = self._getfh(False, getfm=True)

        self.settextposcursor(pos)
        savetaglabels_idx = 0
        lines = [[]]
        for word in x:
            l = len(word["orig_X"])
            tl1 = self.textbrowser.cursorRect(self.textcursor).topLeft()
            self.settextposcursor(pos + l)
            pos += l

            if not self._checkwordhastag(word):
                continue
            tl2 = self.textbrowser.cursorRect(self.textcursor).topLeft()
            _ = self.solvejiaminglabel(
                savetaglabels_idx, word, fonthira, fontori_m, tl1, fha
            )
            lines[-1].append(_)
            if tl1.y() != tl2.y():
                lines.append([])
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

    def _dyna_merge_label(self, line):
        if len(line) <= 1:
            return
        rects = [(label.x(), label.x() + label.width()) for label in line]

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

    def solvejiaminglabel(self, idx, word, font, fontori_m: QFontMetricsF, tl1, fha):
        if idx >= len(self.savetaglabels):
            self.savetaglabels.append(self.currentclass(self.atback2))
        _: base = self.savetaglabels[idx]
        color = self._getkanacolor()
        _.setColor(color)
        _.setText(word["hira"])
        origin = word["orig_X"]
        w_origin = fontori_m.size(0, origin).width()
        y = tl1.y() - fha
        center = tl1.x() + w_origin / 2
        _.setFont(font)
        _.adjustSize()
        w = _.width()
        _.move(int(center - w / 2), y + self.labeloffset_y)
        _.show()
        return _

    def clear(self):
        self.resets()
        self.yinyingposline = 0
        self.textbrowser.clear()
        self.saveiterclasspointer.clear()
        self.textbrowser.move(0, 0)
        self.atback_color.move(0, 0)
        self.trace = []
