import time, copy, threading
from myutils.config import globalconfig
import NativeUtils, windows
from gui.rangeselect import rangeadjust
from myutils.wrapper import threader
from myutils.ocrutil import imageCut, ocr_run, ocr_init
import time, gobject
from qtsymbols import *
from myutils.keycode import vkcode_map
from textsource.textsourcebase import basetext
from ocrengines.baseocrclass import OCRResultParsed
from CVUtils import cvMat


class rangemanger:
    def __init__(self):
        self.range_ui = rangeadjust(gobject.baseobject.settin_ui)
        self.savelastimg: cvMat = None
        self.savelastrecimg: cvMat = None
        self.lastocrtime: float = 0
        self.savelasttext: str = None

    def __del__(self):
        self.range_ui.closesignal.emit()

    def getresmanual(self):
        rect = self.range_ui.getrect()
        if rect is None:
            return
        imgr = imageCut(
            gobject.baseobject.hwnd, rect[0][0], rect[0][1], rect[1][0], rect[1][1]
        )
        result = ocr_run(imgr)
        self.savelastimg = cvMat.fromQImage(imgr)
        self.savelastrecimg = self.savelastimg
        self.lastocrtime = time.time()
        self.savelasttext = result.textonly
        return result

    def getresauto(self):
        rect = self.range_ui.getrect()
        if rect is None:
            return
        imgr = imageCut(
            gobject.baseobject.hwnd, rect[0][0], rect[0][1], rect[1][0], rect[1][1]
        )
        ok = True
        if globalconfig["ocr_auto_method_v2"] == "analysis":
            imgr1 = cvMat.fromQImage(imgr)

            image_score = imgr1.MSSIM(self.savelastimg)

            try:
                gobject.baseobject.settin_ui.thresholdsett1.emit(str(image_score))
            except:
                pass
            self.savelastimg = imgr1

            if image_score > globalconfig["ocr_stable_sim_v2"]:

                image_score2 = imgr1.MSSIM(self.savelastrecimg)

                try:
                    gobject.baseobject.settin_ui.thresholdsett2.emit(str(image_score2))
                except:
                    pass
                if image_score2 > globalconfig["ocr_diff_sim_v2"]:
                    ok = False
                else:
                    self.savelastrecimg = imgr1
            else:
                ok = False
        elif globalconfig["ocr_auto_method_v2"] == "period":
            if time.time() - self.lastocrtime > globalconfig["ocr_interval"]:
                ok = True
            else:
                ok = False
        if ok == False:
            return
        result = ocr_run(imgr)
        t = result.textonly
        self.lastocrtime = time.time()
        sim = NativeUtils.distance(self.savelasttext, t)
        self.savelasttext = t
        if sim < globalconfig["ocr_text_diff"]:
            return
        self.savelasttext = t
        return result

    def waitforstable(self):
        rect = self.range_ui.getrect()
        if rect is None:
            return False
        imgr = imageCut(
            gobject.baseobject.hwnd, rect[0][0], rect[0][1], rect[1][0], rect[1][1]
        )
        imgr1 = cvMat.fromQImage(imgr)
        image_score = imgr1.MSSIM(self.savelastimg)

        try:
            gobject.baseobject.settin_ui.thresholdsett1.emit(str(float(image_score)))
        except:
            pass
        self.savelastimg = imgr1
        return image_score > globalconfig["ocr_stable_sim2_v2"]


class ocrtext(basetext):

    def init(self):
        self.startsql(gobject.gettranslationrecorddir("0_ocr.sqlite"))
        threading.Thread(target=ocr_init).start()
        self.ranges: "list[rangemanger]" = []
        self.gettextthread()

    def clearrange(self):
        self.ranges.clear()
        globalconfig["ocrregions"].clear()

    def leaveone(self):
        self.ranges = self.ranges[-1:]

    def newrangeadjustor(self):
        if len(self.ranges) == 0 or globalconfig["multiregion"]:
            self.ranges.append(rangemanger())

    def starttrace(self, pos):
        for _r in self.ranges:
            _r.range_ui.starttrace(pos)

    def traceoffset(self, curr):
        for _r in self.ranges:
            _r.range_ui.traceoffsetsignal.emit(curr)

    def setrect(self, rect):
        self.ranges[-1].range_ui.setrect(rect)

    def setstyle(self):
        [_.range_ui.setstyle() for _ in self.ranges]

    def showhiderangeui(self, b):
        if b and len(self.ranges) == 0:
            for region in globalconfig["ocrregions"]:
                if region:
                    self.newrangeadjustor()
                    self.setrect(region)
            return
        for _ in self.ranges:
            if b:
                _r = _.range_ui.getrect()
                if _r:
                    _.range_ui.setrect(_r)
            else:
                _.range_ui.hide()

    @threader
    def gettextthread(self):
        laststate = tuple((0 for _ in range(len(globalconfig["ocr_trigger_events"]))))
        lastevents = copy.deepcopy(globalconfig["ocr_trigger_events"])
        while not self.ending:
            if not self.isautorunning:
                time.sleep(0.1)
                continue

            if globalconfig["ocr_auto_method_v2"] == "trigger":
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

                if triggered:

                    t1 = time.time()
                    while (not self.ending) and (
                        globalconfig["ocr_auto_method_v2"] == "trigger"
                    ):
                        time.sleep(0.1)
                        if time.time() - t1 >= globalconfig["ocr_trigger_delay"]:
                            break
                    while (not self.ending) and (
                        globalconfig["ocr_auto_method_v2"] == "trigger"
                    ):
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

    def waitforstablex(self):
        for range_ui in self.ranges:
            if not range_ui.waitforstable():
                return False
        return True

    def getallres(self, auto):
        __text: "list[OCRResultParsed]" = []
        for r in self.ranges:

            if auto:
                _ = r.getresauto()
            else:
                _ = r.getresmanual()
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
        globalconfig["ocrregions"] = [_.range_ui.getrect() for _ in self.ranges]
