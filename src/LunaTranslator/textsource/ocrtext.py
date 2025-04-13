import time, copy, threading
from myutils.config import globalconfig
import winsharedutils, windows
from gui.rangeselect import rangeadjust
from myutils.wrapper import threader
from myutils.ocrutil import imageCut, ocr_run, ocr_init
from myutils.utils import qimage2binary
import time, gobject
from qtsymbols import *
from myutils.keycode import vkcode_map
from textsource.textsourcebase import basetext
from ocrengines.baseocrclass import OCRResultParsed


def normqimage(img: QImage):
    img = img.scaled(128, 8 * 3)
    return img


def compareImage(img1, img2, h=24, w=128):
    cnt = 0
    for i in range(w):
        for j in range(h):
            cnt += img1.pixel(i, j) == img2.pixel(i, j)
    return cnt / (w * h)


class ocrtext(basetext):

    def init(self):
        self.startsql(gobject.gettranslationrecorddir("0_ocr.sqlite"))
        threading.Thread(target=ocr_init).start()
        self.savelastimg = []
        self.savelastrecimg = []
        self.savelasttext = []
        self.lastocrtime = []
        self.range_ui = []
        self.gettextthread()

    def clearrange(self):
        for _ in self.range_ui:
            _.close()
        self.range_ui.clear()
        self.savelastimg.clear()
        self.savelastrecimg.clear()
        self.lastocrtime.clear()
        self.savelasttext.clear()
        globalconfig["ocrregions"].clear()

    def leaveone(self):
        for _ in self.range_ui[:-1]:
            _.close()
        self.range_ui = self.range_ui[-1:]
        self.savelastimg = self.savelastimg[-1:]
        self.savelastrecimg = self.savelastrecimg[-1:]
        self.lastocrtime = self.lastocrtime[-1:]
        self.savelasttext = self.savelasttext[-1:]

    def newrangeadjustor(self):
        if len(self.range_ui) == 0 or globalconfig["multiregion"]:
            self.range_ui.append(rangeadjust(gobject.baseobject.settin_ui))
            self.savelastimg.append(None)
            self.savelastrecimg.append(None)
            self.lastocrtime.append(0)
            self.savelasttext.append(None)

    def starttrace(self, pos):
        for _r in self.range_ui:
            _r.starttrace(pos)

    def traceoffset(self, curr):
        for _r in self.range_ui:
            _r.traceoffsetsignal.emit(curr)

    def setrect(self, rect):
        self.range_ui[-1].setrect(rect)

    def setstyle(self):
        [_.setstyle() for _ in self.range_ui]

    def showhiderangeui(self, b):
        if b and len(self.range_ui) == 0:
            for region in globalconfig["ocrregions"]:
                if region:
                    self.newrangeadjustor()
                    self.setrect(region)
            return
        for _ in self.range_ui:
            if b:
                _r = _.getrect()
                if _r:
                    _.setrect(_r)
            else:
                _.hide()

    @threader
    def gettextthread(self):
        laststate = tuple((0 for _ in range(len(globalconfig["ocr_trigger_events"]))))
        lastevents = copy.deepcopy(globalconfig["ocr_trigger_events"])
        while not self.ending:
            if not self.isautorunning:
                time.sleep(0.1)
                continue

            if globalconfig["ocr_auto_method"] == 3:
                triggered = False
                this = tuple(
                    (
                        windows.GetAsyncKeyState(vkcode_map[line["vkey"]])
                        for line in globalconfig["ocr_trigger_events"]
                    )
                )
                if lastevents != globalconfig["ocr_trigger_events"]:
                    laststate = this
                    lastevents = copy.deepcopy(globalconfig["ocr_trigger_events"])
                    continue
                for _, line in enumerate(globalconfig["ocr_trigger_events"]):
                    event = line["event"]
                    press = this[_]
                    if ((event == 0) and (laststate[_] == 0) and press) or (
                        (event == 1) and laststate[_] and (press == 0)
                    ):
                        triggered = True
                        break
                laststate = this
                if triggered:
                    if gobject.baseobject.hwnd:
                        for _ in range(2):
                            # 切换前台窗口
                            p1 = windows.GetWindowThreadProcessId(
                                gobject.baseobject.hwnd
                            )
                            p2 = windows.GetWindowThreadProcessId(
                                windows.GetForegroundWindow()
                            )
                            triggered = p1 == p2
                            if triggered:
                                break
                            time.sleep(0.1)

                    else:
                        triggered = self.waitforstablex(strict=True)
                if triggered:
                    time.sleep(globalconfig["ocr_trigger_delay"])

                    while (not self.ending) and (globalconfig["ocr_auto_method"] == 3):
                        if self.waitforstablex():
                            break
                        time.sleep(0.1)
                    t = self.getallres(False)
                    if t:
                        self.dispatchtext(t)
                time.sleep(0.01)
            else:
                laststate = tuple(
                    (0 for _ in range(len(globalconfig["ocr_trigger_events"])))
                )
                t = self.getallres(True)
                if t:
                    self.dispatchtext(t)
                time.sleep(0.1)

    def waitforstable(self, i, imgr, strict):
        if strict:
            imgr1 = imgr
            if self.savelastimg[i] is not None:
                a = qimage2binary(imgr1)
                b = qimage2binary(self.savelastimg[i])
                image_score = a != b
            else:
                image_score = 0
        else:
            imgr1 = normqimage(imgr)
            if (self.savelastimg[i] is not None) and (
                imgr1.size() == self.savelastimg[i].size()
            ):
                image_score = compareImage(imgr1, self.savelastimg[i])
            else:
                image_score = 0

        if i == 0:
            try:
                gobject.baseobject.settin_ui.thresholdsett1.emit(
                    str(float(image_score))
                )
            except:
                pass
        self.savelastimg[i] = imgr1
        if strict:
            return image_score != 0
        else:
            return image_score > globalconfig["ocr_stable_sim2"]

    def waitforstablex(self, strict=False):
        for i, range_ui in enumerate(self.range_ui):
            rect = range_ui.getrect()
            if rect is None:
                continue
            img = imageCut(
                gobject.baseobject.hwnd, rect[0][0], rect[0][1], rect[1][0], rect[1][1]
            )
            if not self.waitforstable(i, img, strict):
                return False
        return True

    def getresauto(self, i, imgr):
        ok = True
        if globalconfig["ocr_auto_method"] in [0, 2]:
            imgr1 = normqimage(imgr)

            if self.savelastimg[i] is not None and (
                imgr1.size() == self.savelastimg[i].size()
            ):

                image_score = compareImage(imgr1, self.savelastimg[i])

            else:
                image_score = 0
            if i == 0:
                try:
                    gobject.baseobject.settin_ui.thresholdsett1.emit(
                        str(image_score)
                    )
                except:
                    pass
            self.savelastimg[i] = imgr1

            if image_score > globalconfig["ocr_stable_sim"]:
                if self.savelastrecimg[i] is not None and (
                    imgr1.size() == self.savelastrecimg[i].size()
                ):
                    image_score2 = compareImage(imgr1, self.savelastrecimg[i])
                else:
                    image_score2 = 0
                if i == 0:
                    try:
                        gobject.baseobject.settin_ui.thresholdsett2.emit(
                            str(image_score2)
                        )
                    except:
                        pass
                if image_score2 > globalconfig["ocr_diff_sim"]:
                    ok = False
                else:
                    self.savelastrecimg[i] = imgr1
            else:
                ok = False
        if globalconfig["ocr_auto_method"] in [1, 2]:
            if time.time() - self.lastocrtime[i] > globalconfig["ocr_interval"]:
                ok = True
            else:
                ok = False
        if ok == False:
            return
        result = ocr_run(imgr)
        t = result.textonly
        self.lastocrtime[i] = time.time()
        if self.savelasttext[i] is not None:
            sim = winsharedutils.distance(self.savelasttext[i], t)
            self.savelasttext[i] = t
            if sim < globalconfig["ocr_text_diff"]:
                return
        self.savelasttext[i] = t
        return result

    def getresmanual(self, i, imgr):
        result = ocr_run(imgr)
        imgr1 = normqimage(imgr)
        self.savelastimg[i] = imgr1
        self.savelastrecimg[i] = imgr1
        self.lastocrtime[i] = time.time()
        self.savelasttext[i] = result.textonly
        return result

    def getallres(self, auto):
        __text: "list[OCRResultParsed]" = []
        for i, range_ui in enumerate(self.range_ui):
            rect = range_ui.getrect()
            if rect is None:
                continue
            img = imageCut(
                gobject.baseobject.hwnd, rect[0][0], rect[0][1], rect[1][0], rect[1][1]
            )
            if auto:
                _ = self.getresauto(i, img)
            else:
                _ = self.getresmanual(i, img)
            if _ is None:
                continue
            if _.error:
                _.displayerror()
                return
            __text.append(_)
        if not __text:
            return
        text = "\n".join(_.textonly for _ in __text)
        if __text[0].result.isocrtranslate:
            gobject.baseobject.displayinfomessage(text, "<notrans>")
        else:
            return text

    def gettextonce(self):
        return self.getallres(False)

    def end(self):
        globalconfig["ocrregions"] = [_.getrect() for _ in self.range_ui]
        [_.closesignal.emit() for _ in self.range_ui]
