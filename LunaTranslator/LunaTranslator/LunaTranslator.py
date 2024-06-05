import time
import os, threading, sys
from qtsymbols import *
from traceback import print_exc
from myutils.config import (
    globalconfig,
    _TR,
    savehook_new_list,
    savehook_new_data,
    setlanguage,
    static_data,
)
import zipfile
from myutils.utils import (
    minmaxmoveobservefunc,
    parsemayberegexreplace,
    kanjitrans,
    checkifnewgame,
    checkpostusing,
    getpostfile,
    stringfyerror,
)
from myutils.wrapper import threader
from gui.showword import searchwordW
from myutils.hwnd import getpidexe, ListProcess, getExeIcon
from textsource.copyboard import copyboard
from textsource.texthook import texthook
from textsource.ocrtext import ocrtext
from gui.selecthook import hookselect
from gui.translatorUI import QUnFrameWindow
from gui.languageset import languageset
import zhconv, functools
from gui.transhist import transhist
from gui.edittext import edittext
import importlib, qtawesome
from functools import partial
from gui.setting import Setting
from gui.showocrimage import showocrimage
from gui.attachprocessdialog import AttachProcessDialog
import windows
import gobject
import winsharedutils
from winsharedutils import pid_running
from myutils.post import POSTSOLVE
from myutils.utils import nowisdark

class commonstylebase(QWidget):
    setstylesheetsignal = pyqtSignal()

    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.setstylesheetsignal.connect(gobject.baseobject.setcommonstylesheet)


class MAINUI:
    def __init__(self) -> None:
        super().__init__()
        self.lasttranslatorindex = 0
        self.translators = {}
        self.cishus = {}
        self.reader = None
        self.textsource_p = None
        self.currentmd5 = "0"
        self.currenttext = ""
        self.currenttranslate = ""
        self.currentread = ""
        self.refresh_on_get_trans_signature = 0
        self.currentsignature = None
        self.isrunning = True
        self.solvegottextlock = threading.Lock()
        self.outputers = {}
        self.processmethods = []
        self.zhanweifu = 0
        self.showocrimage = None
        self.showocrimage_cached = None
        self.AttachProcessDialog = None
        self.edittextui = None
        self.edittextui_cached = None
        self.edittextui_sync = True

    @property
    def textsource(self):
        return self.textsource_p

    @textsource.setter
    def textsource(self, _):
        if _ is None and self.textsource_p:
            try:
                self.textsource_p.end()
            except:
                print_exc()
        self.textsource_p = _

        self.currentmd5 = "0" if _ is None else _.md5

    @threader
    def safeloadprocessmodels(self):
        for item in static_data["transoptimi"]:
            name = item["name"]
            try:
                mm = getpostfile(name)
                if not mm:
                    continue
                Process = importlib.import_module(mm).Process

                def __(kls, _name):
                    class klass(kls):
                        @property
                        def using(self):
                            return checkpostusing(_name)

                    return klass()

                object = __(Process, name)
                self.processmethods.append({"name": name, "object": object})
            except:
                print_exc()

    def solvebeforetrans(self, content):
        contexts = []
        self.zhanweifu = 0
        for method in self.processmethods:
            context = None
            try:
                if method["object"].using:
                    if "process_before" in dir(method["object"]):
                        content, context = method["object"].process_before(content)
            except:
                print_exc()
            contexts.append(context)
        return content, contexts

    def solveaftertrans(self, res, mp):
        for i, method in enumerate(self.processmethods):

            context = mp[i]
            try:
                if method["object"].using:
                    if "process_after" in dir(method["object"]):
                        res = method["object"].process_after(res, context)
            except:
                print_exc()
        return res

    def _POSTSOLVE(self, s):
        ss = POSTSOLVE(s)
        self.settin_ui.showandsolvesig.emit(s)
        return ss

    def textgetmethod(
        self, text, is_auto_run=True, embedcallback=None, onlytrans=False
    ):
        with self.solvegottextlock:
            return self.textgetmethod_1(text, is_auto_run, embedcallback, onlytrans)

    def textgetmethod_1(
        self, text, is_auto_run=True, embedcallback=None, onlytrans=False
    ):

        returnandembedcallback = lambda: embedcallback("") if embedcallback else ""

        if type(text) == str:
            if text.startswith("<notrans>"):
                self.translation_ui.displayres.emit(
                    dict(
                        color=globalconfig["rawtextcolor"],
                        res=text[len("<notrans>") :],
                        onlytrans=onlytrans,
                        clear=True,
                    )
                )
                self.currenttext = text
                self.currentread = text
                return
            else:
                msgs = [
                    ("<msg_info_not_refresh>", globalconfig["rawtextcolor"], False),
                    ("<msg_info_refresh>", globalconfig["rawtextcolor"], True),
                    ("<msg_error_not_refresh>", "red", False),
                    ("<msg_error_refresh>", "red", True),
                ]
                for msg, color, refresh in msgs:
                    if text.startswith(msg):
                        self.translation_ui.displaystatus.emit(
                            text[len(msg) :], color, refresh, False
                        )
                        return
            if text == "" or len(text) > 100000:
                return returnandembedcallback()
        if onlytrans == False:
            self.currentsignature = time.time()
        try:
            if type(text) == list:
                origin = "\n".join(text)
                text = "\n".join([self._POSTSOLVE(_) for _ in text])
            else:
                origin = text
                text = self._POSTSOLVE(text)
        except Exception as e:
            msg = str(type(e))[8:-2] + " " + str(e).replace("\n", "").replace("\r", "")
            self.translation_ui.displaystatus.emit(msg, "red", True, True)
            return

        if text == "" or (
            is_auto_run
            and (
                text == self.currenttext
                or len(text)
                > (max(globalconfig["maxoriginlength"], globalconfig["maxlength"]))
            )
        ):
            return returnandembedcallback()

        try:
            self.textsource.sqlqueueput(
                (
                    text,
                    origin,
                )
            )
        except:
            pass
        if onlytrans == False:
            self.dispatchoutputer(text)
            self.currenttext = text
            if globalconfig["read_raw"]:
                self.currentread = text
                self.autoreadcheckname()

        if globalconfig["refresh_on_get_trans"] == False:
            self.translation_ui.displayraw1.emit(
                dict(text=text, color=globalconfig["rawtextcolor"], onlytrans=onlytrans)
            )
            _showrawfunction = None
            _showrawfunction_sig = 0
        else:
            _showrawfunction = functools.partial(
                self.translation_ui.displayraw1.emit,
                dict(
                    text=text, color=globalconfig["rawtextcolor"], onlytrans=onlytrans
                ),
            )
            _showrawfunction_sig = time.time()

        text_solved, optimization_params = self.solvebeforetrans(text)

        if is_auto_run and (
            len(text_solved) < globalconfig["minlength"]
            or len(text_solved) > globalconfig["maxlength"]
        ):
            return returnandembedcallback()

        self.premtalready = ["premt"]
        self.usefultranslators = list(self.translators.keys())
        if "premt" in self.translators:
            try:
                res = self.translators["premt"].translate(text_solved)
                for k in res:
                    self.premtalready.append(k)
                    if k in globalconfig["fanyi"]:
                        _colork = k
                    else:
                        _colork = "premt"
                    self.GetTranslationCallback(
                        onlytrans,
                        _colork,
                        self.currentsignature,
                        optimization_params,
                        _showrawfunction,
                        _showrawfunction_sig,
                        text,
                        res[k],
                        embedcallback,
                        0,
                    )

            except:
                print_exc()
        if globalconfig["loadbalance"]:
            usenum = min(globalconfig["loadbalance_oncenum"], len(self.translators))
        else:
            usenum = len(self.translators)
        if usenum:
            thistimeusednum = 0
            self.lasttranslatorindex = self.lasttranslatorindex % len(self.translators)
            _len = len(self.translators)
            keys = list(self.translators.keys()) + list(self.translators.keys())
            keys = keys[self.lasttranslatorindex : self.lasttranslatorindex + _len]
            # print(keys,usenum,self.lasttranslatorindex)
            for engine in keys:
                if engine not in self.premtalready:
                    self.translators[engine].gettask(
                        (
                            partial(
                                self.GetTranslationCallback,
                                onlytrans,
                                engine,
                                self.currentsignature,
                                optimization_params,
                                _showrawfunction,
                                _showrawfunction_sig,
                                text,
                            ),
                            text,
                            text_solved,
                            embedcallback,
                            is_auto_run,
                        )
                    )
                thistimeusednum += 1
                self.lasttranslatorindex += 1
                if thistimeusednum >= usenum:
                    break

    def GetTranslationCallback(
        self,
        onlytrans,
        classname,
        currentsignature,
        optimization_params,
        _showrawfunction,
        _showrawfunction_sig,
        contentraw,
        res,
        embedcallback,
        iter_res_status,
    ):
        if classname in self.usefultranslators:
            self.usefultranslators.remove(classname)
        if embedcallback is None and currentsignature != self.currentsignature:
            return

        returnandembedcallback = lambda x: embedcallback(x) if embedcallback else ""

        if type(res) == str:
            if res.startswith("<msg_translator>"):
                if currentsignature == self.currentsignature:
                    self.translation_ui.displaystatus.emit(
                        globalconfig["fanyi"][classname]["name"]
                        + " "
                        + res[len("<msg_translator>") :],
                        "red",
                        onlytrans,
                        False,
                    )
                if len(self.usefultranslators) == 0:
                    returnandembedcallback("")
                return

        res = self.solveaftertrans(res, optimization_params)

        if onlytrans == False:
            if globalconfig["read_trans"] and (
                list(globalconfig["fanyi"].keys())[globalconfig["read_translator"]]
                == classname
            ):
                self.currentread = res
                self.readcurrent()

        needshowraw = (
            _showrawfunction
            and self.refresh_on_get_trans_signature != _showrawfunction_sig
        )
        if needshowraw:
            self.refresh_on_get_trans_signature = _showrawfunction_sig
            _showrawfunction()

        if currentsignature == self.currentsignature and globalconfig["showfanyi"]:
            displayreskwargs = dict(
                name=globalconfig["fanyi"][classname]["name"],
                color=globalconfig["fanyi"][classname]["color"],
                res=res,
                onlytrans=onlytrans,
            )
            if iter_res_status:
                displayreskwargs.update(iter_context=(iter_res_status, classname))
            self.translation_ui.displayres.emit(displayreskwargs)

        if iter_res_status in (0, 2):  # 0为普通，1为iter，2为iter终止
            try:
                self.textsource.sqlqueueput((contentraw, classname, res))
            except:
                pass
            self.currenttranslate = res
            if (
                globalconfig["embedded"]["as_fast_as_posible"]
                or classname == globalconfig["embedded"]["translator_2"]
            ):
                return returnandembedcallback(
                    kanjitrans(zhconv.convert(res, "zh-tw"))
                    if globalconfig["embedded"]["trans_kanji"]
                    else res
                )

    @threader
    def autoreadcheckname(self):
        try:
            time.sleep(globalconfig["textthreaddelay"] / 1000)
            name = self.textsource.currentname
            names = savehook_new_data[self.textsource.pname]["allow_tts_auto_names_v4"]
            needpass = False
            if name in names:
                needpass = True

            # name文本是类似“美香「おはよう」”的形式
            text = name
            for _name in names:
                if text.startswith(_name) or text.endswith(_name):
                    if len(text) >= len(_name) + 3:  # 2个引号+至少1个文本内容。
                        needpass = True
                        break

            if needpass == False:  # name not in names:
                self.readcurrent()
            gobject.baseobject.textsource.currentname = None
        except:
            # print_exc()
            self.readcurrent()

    def ttsrepair(self, text, usedict):
        if usedict["tts_repair"]:
            text = parsemayberegexreplace(usedict["tts_repair_regex"], text)
        return text

    def readcurrent(self, force=False):
        try:
            if force or globalconfig["autoread"]:
                text = self.ttsrepair(self.currentread, globalconfig["ttscommon"])
                try:
                    text = self.ttsrepair(
                        text, savehook_new_data[self.textsource.pname]
                    )
                except:
                    pass
                self.reader.read(text, force)
        except:
            print_exc()

    @threader
    def startreader(self, use=None, checked=True):
        try:
            self.reader.end()
        except:
            pass
        self.reader = None
        self.settin_ui.voicelistsignal.emit([], -1)
        if checked:
            if use is None:

                for key in globalconfig["reader"]:
                    if globalconfig["reader"][key]["use"] and os.path.exists(
                        ("./LunaTranslator/tts/" + key + ".py")
                    ):
                        use = key
                        break
            if use:
                aclass = importlib.import_module("tts." + use).TTS

                self.reader_usevoice = use
                self.reader = aclass(
                    use, self.settin_ui.voicelistsignal, self.settin_ui.mp3playsignal
                )

    def selectprocess(self, selectedp):
        self.textsource = None
        pids, pexe, hwnd = selectedp
        checkifnewgame(savehook_new_list, pexe, windows.GetWindowText(hwnd))
        if globalconfig["sourcestatus2"]["texthook"]["use"]:
            self.textsource = texthook(pids, hwnd, pexe)

    def starttextsource(self, use=None, checked=True):
        self.translation_ui.showhidestate = False
        self.translation_ui.refreshtooliconsignal.emit()
        try:
            self.settin_ui.selectbutton.setEnabled(
                globalconfig["sourcestatus2"]["texthook"]["use"]
            )
            self.settin_ui.selecthookbutton.setEnabled(
                globalconfig["sourcestatus2"]["texthook"]["use"]
            )
        except:
            pass
        self.textsource = None
        if checked:
            classes = {"ocr": ocrtext, "copy": copyboard, "texthook": None}
            if use is None:
                use = list(
                    filter(
                        lambda _: globalconfig["sourcestatus2"][_]["use"],
                        classes.keys(),
                    )
                )
                use = None if len(use) == 0 else use[0]
            if use is None:
                return
            elif classes[use] is None:
                pass
            else:
                self.textsource = classes[use]()

    @threader
    def starthira(self, use=None, checked=True):
        if checked:
            hirasettingbase = globalconfig["hirasetting"]
            _hira = None
            for name in hirasettingbase:
                if hirasettingbase[name]["use"]:
                    if (
                        os.path.exists("./LunaTranslator/hiraparse/" + name + ".py")
                        == False
                    ):
                        continue
                    _hira = importlib.import_module("hiraparse." + name)
                    _hira = getattr(_hira, name)
                    break

            try:
                if _hira:
                    self.hira_ = _hira(name)
                else:
                    self.hira_ = None
            except:
                print_exc()
                self.hira_ = None
        else:
            self.hira_ = None

    @threader
    def startoutputer_re(self, klass):
        self.outputers[klass].init()

    @threader
    def startoutputer(self):
        for classname in globalconfig["textoutputer"]:
            if not os.path.exists("./LunaTranslator/textoutput/" + classname + ".py"):
                continue
            aclass = importlib.import_module("textoutput." + classname).Outputer
            self.outputers[classname] = aclass(classname)

    def dispatchoutputer(self, text):
        for _, kls in self.outputers.items():
            if kls.config["use"]:
                kls.puttask(text)

    def fanyiinitmethod(self, classname):
        try:
            if classname == "selfbuild":
                if not os.path.exists("./userconfig/selfbuild.py"):
                    return None
                aclass = importlib.import_module("selfbuild").TS
            else:
                if not os.path.exists(
                    "./LunaTranslator/translator/" + classname + ".py"
                ):
                    return None
                aclass = importlib.import_module("translator." + classname).TS
        except Exception as e:
            print_exc()
            self.textgetmethod(
                "<msg_error_not_refresh>"
                + globalconfig["fanyi"][classname]["name"]
                + " import failed : "
                + str(stringfyerror(e))
            )
            return None
        return aclass(classname)

    @threader
    def prepare(self, now=None, _=None):
        self.commonloader("fanyi", self.translators, self.fanyiinitmethod, now)

    def commonloader(self, fanyiorcishu, dictobject, initmethod, _type=None):
        if _type:
            self.commonloader_warp(fanyiorcishu, dictobject, initmethod, _type)
        else:
            for key in globalconfig[fanyiorcishu]:
                self.commonloader_warp(fanyiorcishu, dictobject, initmethod, key)

    @threader
    def commonloader_warp(self, fanyiorcishu, dictobject, initmethod, _type):
        try:
            if _type in dictobject:
                try:
                    dictobject[_type].notifyqueuforend()
                except:
                    pass
                dictobject.pop(_type)
            if globalconfig[fanyiorcishu][_type]["use"] == False:
                return
            item = initmethod(_type)
            if item:
                dictobject[_type] = item
        except:
            print_exc()

    @threader
    def startxiaoxueguan(self, type_=None, _=None):
        self.commonloader("cishu", self.cishus, self.cishuinitmethod, type_)

    def cishuinitmethod(self, type_):
        try:
            aclass = importlib.import_module("cishu." + type_)
            aclass = getattr(aclass, type_)
        except:
            print_exc()
            return

        return aclass(type_)

    def maybesetimage(self, pair):
        if self.showocrimage:
            try:
                self.showocrimage.setimage.emit(pair)
            except:
                print_exc()
        self.showocrimage_cached = pair

    def createshowocrimage(self):
        try:
            self.showocrimage = showocrimage(self.settin_ui, self.showocrimage_cached)
            if self.showocrimage:
                self.showocrimage.show()
        except:
            print_exc()

    def maybesetedittext(self, text):
        if self.edittextui:
            try:
                self.edittextui.getnewsentencesignal.emit(text)
            except:
                print_exc()
        self.edittextui_cached = text

    def createedittextui(self):
        try:
            self.edittextui = edittext(self.settin_ui, self.edittextui_cached)
            if self.edittextui:
                self.edittextui.show()
        except:
            print_exc()

    def safecloseattachprocess(self):

        if self.AttachProcessDialog:
            try:
                self.AttachProcessDialog.close()
            except:
                pass

    def createattachprocess(self):
        try:
            self.AttachProcessDialog = AttachProcessDialog(
                self.settin_ui, self.selectprocess, self.hookselectdialog
            )
            if self.AttachProcessDialog:
                self.AttachProcessDialog.show()
        except:
            print_exc()

    def onwindowloadautohook(self):
        textsourceusing = globalconfig["sourcestatus2"]["texthook"]["use"]
        if not (globalconfig["autostarthook"] and textsourceusing):
            return
        elif self.AttachProcessDialog and self.AttachProcessDialog.isVisible():
            return
        else:
            try:
                if self.textsource is None:
                    hwnd = windows.GetForegroundWindow()
                    pid = windows.GetWindowThreadProcessId(hwnd)
                    name_ = getpidexe(pid)
                    if name_ and name_ in savehook_new_list:
                        lps = ListProcess(False)
                        for pids, _exe in lps:
                            if _exe == name_:

                                # if any(map(testprivilege,pids)):
                                self.textsource = None
                                if globalconfig["sourcestatus2"]["texthook"]["use"]:
                                    if globalconfig["startgamenototop"] == False:
                                        idx = savehook_new_list.index(name_)
                                        savehook_new_list.insert(
                                            0, savehook_new_list.pop(idx)
                                        )
                                    needinserthookcode = savehook_new_data[name_][
                                        "needinserthookcode"
                                    ]
                                    self.textsource = texthook(
                                        pids,
                                        hwnd,
                                        name_,
                                        autostarthookcode=savehook_new_data[name_][
                                            "hook"
                                        ],
                                        needinserthookcode=needinserthookcode,
                                    )

                                onloadautoswitchsrclang = savehook_new_data[name_][
                                    "onloadautoswitchsrclang"
                                ]
                                if onloadautoswitchsrclang > 0:
                                    try:
                                        self.settin_ui.srclangswitcher.setCurrentIndex(
                                            onloadautoswitchsrclang - 1
                                        )
                                    except:
                                        globalconfig["srclang3"] = (
                                            onloadautoswitchsrclang - 1
                                        )
                                break

                else:
                    pids = self.textsource.pids
                    if sum([int(pid_running(pid)) for pid in pids]) == 0:
                        self.safebackupsavedata(
                            self.textsource.pname,
                            self.textsource.basename + "_" + self.textsource.md5,
                        )
                        self.textsource = None

            except:

                print_exc()

    @threader
    def safebackupsavedata(self, exe, signame):
        path = savehook_new_data[exe]["autosavesavedata"]
        if not os.path.exists(path):
            return
        data_head = time.strftime("%Y-%m-%d-%H-%M-%S.zip", time.localtime())
        savedirbase = globalconfig["backupsavedatato"]
        if os.path.exists(savedirbase) == False:
            savedirbase = "./cache/backup"
        savedir = os.path.join(savedirbase, signame)
        os.makedirs(savedir, exist_ok=True)

        def zip_directory(directory_path, output_path):
            with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                for root, _, files in os.walk(directory_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        relative_path = os.path.relpath(file_path, directory_path)
                        zipf.write(file_path, relative_path)

        zip_directory(path, savedir + "/" + data_head)

    def autohookmonitorthread(self):
        while self.isrunning:
            self.onwindowloadautohook()
            time.sleep(
                0.5
            )  # 太短了的话，中间存在一瞬间，后台进程比前台窗口内存占用要大。。。

    def autocheckhwndexists(self):
        def setandrefresh(bool):
            if self.translation_ui.isbindedwindow != bool:
                self.translation_ui.isbindedwindow = bool
                self.translation_ui.refreshtooliconsignal.emit()

        while self.isrunning:
            if self.textsource:

                hwnd = self.textsource.hwnd

                if hwnd == 0:
                    if globalconfig["sourcestatus2"]["texthook"]["use"]:
                        fhwnd = windows.GetForegroundWindow()
                        pids = self.textsource.pids
                        if (
                            hwnd == 0
                            and windows.GetWindowThreadProcessId(fhwnd) in pids
                        ):
                            if "once" not in dir(self.textsource):
                                self.textsource.once = True
                                self.textsource.hwnd = fhwnd
                                setandrefresh(True)
                    else:
                        setandrefresh(False)
                else:
                    if windows.GetWindowThreadProcessId(hwnd) == 0:
                        self.textsource.hwnd = 0
                        setandrefresh(False)
                    elif "once" not in dir(self.textsource):
                        self.textsource.once = True
                        setandrefresh(True)
                if len(self.textsource.pids):
                    _mute = winsharedutils.GetProcessMute(self.textsource.pids[0])
                    if self.translation_ui.processismuteed != _mute:
                        self.translation_ui.processismuteed = _mute
                        self.translation_ui.refreshtooliconsignal.emit()
            else:
                setandrefresh(False)

            time.sleep(0.5)

    def setdarktheme(self, widget, dark):
        if widget.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground):
            return
        winsharedutils.SetTheme(
            int(widget.winId()), dark, globalconfig["WindowBackdrop"]
        )

    def checkgameplayingthread(self):
        self.tracestarted = False
        while True:
            statistictime = time.time()
            time.sleep(1)

            def isok(name_):
                now = time.time()
                if self.tracestarted == False:
                    self.tracestarted = True
                    savehook_new_data[name_]["traceplaytime_v2"].append(
                        [statistictime, statistictime]
                    )
                savehook_new_data[name_]["statistic_playtime"] += now - statistictime
                savehook_new_data[name_]["traceplaytime_v2"][-1][1] = now

            def isbad():
                self.tracestarted = False

            try:
                _hwnd = windows.GetForegroundWindow()
                _pid = windows.GetWindowThreadProcessId(_hwnd)

                try:
                    if len(self.textsource.pids) == 0:
                        raise Exception()
                    if _pid in self.textsource.pids or _pid == os.getpid():
                        isok(self.textsource.pname)
                    else:
                        isbad()
                except:
                    name_ = getpidexe(_pid)
                    if name_ and name_ in savehook_new_list:
                        isok(name_)
                    else:
                        isbad()
            except:
                print_exc()

    def setshowintab_checked(self, widget):
        if widget == self.translation_ui:
            winsharedutils.showintab(int(widget.winId()), globalconfig["showintab"])
            return
        window_flags = widget.windowFlags()
        if (
            Qt.WindowType.FramelessWindowHint & window_flags
            == Qt.WindowType.FramelessWindowHint
        ):
            return
        if isinstance(widget, QMenu):
            return
        if isinstance(widget, QFrame):
            return
        if (
            isinstance(widget, QWidget)
            and widget.parent() is None
            and len(widget.children()) == 0
        ):
            # combobox的下拉框，然后这个widget会迅速销毁，会导致任务栏闪一下。没别的办法了姑且这样过滤一下
            return
        winsharedutils.showintab(int(widget.winId()), globalconfig["showintab_sub"])

    def inittray(self):

        trayMenu = QMenu(self.settin_ui)
        showAction = QAction(
            _TR("&显示"),
            trayMenu,
            triggered=self.translation_ui.show_,
        )
        settingAction = QAction(
            qtawesome.icon("fa.gear"),
            _TR("&设置"),
            trayMenu,
            triggered=lambda: self.settin_ui.showsignal.emit(),
        )
        quitAction = QAction(
            qtawesome.icon("fa.times"),
            _TR("&退出"),
            trayMenu,
            triggered=self.translation_ui.close,
        )
        trayMenu.addAction(showAction)
        trayMenu.addAction(settingAction)
        trayMenu.addSeparator()
        trayMenu.addAction(quitAction)
        self.tray = QSystemTrayIcon()

        icon = getExeIcon(sys.argv[0])  #'./LunaTranslator.exe')# QIcon()
        self.tray.setIcon(icon)

        self.tray.activated.connect(self.translation_ui.leftclicktray)
        self.tray.show()
        self.tray.setContextMenu(trayMenu)

    def destroytray(self):
        self.tray.hide()
        self.tray = None

    def setshowintab(self):
        for widget in QApplication.topLevelWidgets():
            self.setshowintab_checked(widget)

    def setcommonstylesheet(self):

        dark = nowisdark()
        darklight = ["light", "dark"][dark]

        self.currentisdark = dark

        for widget in QApplication.topLevelWidgets():
            self.setdarktheme(widget, dark)
        style = ""
        for _ in (0,):
            try:
                idx = globalconfig[darklight + "theme"] - int(not dark)
                if idx == -1:
                    break
                _fn = static_data["themes"][darklight][idx]["file"]

                if _fn.endswith(".py"):
                    style = importlib.import_module(
                        "files.themes." + _fn[:-3].replace("/", ".")
                    ).stylesheet()
                elif _fn.endswith(".qss"):
                    with open(
                        "./files/themes/{}".format(_fn),
                        "r",
                    ) as ff:
                        style = ff.read()
            except:
                print_exc()
        style += (
            "*{font: %spt '" % (globalconfig["settingfontsize"])
            + (globalconfig["settingfonttype"])
            + "' ;  }"
        )
        self.__commonstylebase.setStyleSheet(style)

    def loadui(self):
        self.installeventfillter()
        self.translation_ui = QUnFrameWindow()
        self.translation_ui.show()
        self.translation_ui.aftershowdosomething()
        self.mainuiloadafter()

    def mainuiloadafter(self):
        self.safeloadprocessmodels()
        self.prepare()
        self.startxiaoxueguan()
        self.starthira()
        self.startoutputer()
        self.__commonstylebase = commonstylebase(self.translation_ui)
        self.setcommonstylesheet()
        self.settin_ui = Setting(self.__commonstylebase)
        self.transhis = transhist(self.settin_ui)
        self.startreader()
        self.searchwordW = searchwordW(self.settin_ui)
        self.hookselectdialog = hookselect(self.settin_ui)
        self.starttextsource()
        threading.Thread(target=self.autocheckhwndexists).start()
        threading.Thread(target=self.autohookmonitorthread).start()
        threading.Thread(
            target=minmaxmoveobservefunc, args=(self.translation_ui,)
        ).start()
        threading.Thread(target=self.checkgameplayingthread).start()
        threading.Thread(target=self.darklistener).start()
        self.inittray()

    def darklistener(self):
        sema = winsharedutils.startdarklistener()
        while True:
            # 会触发两次
            windows.WaitForSingleObject(sema, windows.INFINITE)
            if globalconfig["darklight"] == 2:
                self.__commonstylebase.setstylesheetsignal.emit()
            windows.WaitForSingleObject(sema, windows.INFINITE)

    def installeventfillter(self):
        class WindowEventFilter(QObject):
            def eventFilter(_, obj, event):
                if event.type() == QEvent.Type.WinIdChange:

                    hwnd = obj.winId()
                    if hwnd:  # window create/destroy,when destroy winId is None
                        if self.currentisdark is not None:
                            self.setdarktheme(obj, self.currentisdark)
                        windows.SetProp(
                            int(obj.winId()),
                            "Magpie.ToolWindow",
                            windows.HANDLE(1),
                        )
                        self.setshowintab_checked(obj)
                return False

        self.currentisdark = None
        self.__filter = WindowEventFilter()  # keep ref
        QApplication.instance().installEventFilter(self.__filter)

    def checklang(self):
        if globalconfig["language_setted_2.4.5"] == False:

            x = languageset(static_data["language_list_show"])
            x.exec()
            globalconfig["language_setted_2.4.5"] = True
            globalconfig["languageuse"] = x.current
            globalconfig["tgtlang3"] = x.current
            setlanguage()
