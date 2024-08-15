import time, uuid
import os, threading, re, codecs, winreg
from qtsymbols import *
from traceback import print_exc
from myutils.config import (
    globalconfig,
    _TR,
    savehook_new_list,
    uid2gamepath,
    findgameuidofpath,
    savehook_new_data,
    static_data,
    getlanguse,
    set_font_default,
)
from ctypes import c_int, CFUNCTYPE, c_void_p
from myutils.utils import (
    minmaxmoveobservefunc,
    parsemayberegexreplace,
    kanjitrans,
    find_or_create_uid,
    checkisusingwine,
    checkpostusing,
    stringfyerror,
    targetmod,
    translate_exits,
)
from myutils.wrapper import threader, tryprint
from gui.showword import searchwordW
from myutils.hwnd import getpidexe, ListProcess, getExeIcon, getcurrexe
from textsource.copyboard import copyboard
from textsource.texthook import texthook
from textsource.ocrtext import ocrtext
from gui.selecthook import hookselect
from gui.translatorUI import TranslatorWindow
import zhconv, functools
from gui.transhist import transhist
from gui.edittext import edittext
import importlib, qtawesome
from functools import partial
from gui.setting import Setting
from gui.attachprocessdialog import AttachProcessDialog
import windows
import gobject
import winsharedutils
from winsharedutils import collect_running_pids
from myutils.post import POSTSOLVE
from myutils.utils import nowisdark, getfilemd5
from myutils.traceplaytime import playtimemanager
from myutils.audioplayer import series_audioplayer
from gui.dynalang import LAction, LMenu


class commonstylebase(QWidget):
    setstylesheetsignal = pyqtSignal()

    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.setstylesheetsignal.connect(gobject.baseobject.setcommonstylesheet)


class MAINUI:
    def __init__(self) -> None:
        super().__init__()
        self.update_avalable = False
        self.lasttranslatorindex = 0
        self.translators = {}
        self.cishus = {}
        self.specialreaders = {}
        self.textsource_p = None
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
        self.AttachProcessDialog = None
        self.edittextui = None
        self.edittextui_cached = None
        self.edittextui_sync = True
        self.notifyonce = set()
        self.audioplayer = series_audioplayer()
        self._internal_reader = None
        self.reader_uid = None
        self.__hwnd = None

    @property
    def reader(self):
        return self._internal_reader

    @reader.setter
    def reader(self, _):
        if _ is None:
            self._internal_reader = None
            self.reader_uid = None
            self.settin_ui.voicelistsignal.emit(None)
        else:
            if self.reader_uid != _.uid:
                return
            self._internal_reader = _
            self.settin_ui.voicelistsignal.emit(_)

    @property
    def textsource(self):
        return self.textsource_p

    @property
    def hwnd(self):
        return self.__hwnd

    @hwnd.setter
    def hwnd(self, __hwnd):
        self.__hwnd = __hwnd
        if not __hwnd:
            self.translation_ui.processismuteed = False
            self.translation_ui.isbindedwindow = False
            self.translation_ui.refreshtooliconsignal.emit()
            self.translation_ui.thistimenotsetop = False
        else:
            _mute = winsharedutils.GetProcessMute(
                windows.GetWindowThreadProcessId(__hwnd)
            )
            self.translation_ui.processismuteed = _mute
            self.translation_ui.isbindedwindow = True
            self.translation_ui.refreshtooliconsignal.emit()
            try:
                if not self.textsource:
                    return
                if not self.textsource.autofindpids:
                    return
                self.textsource.pids = [windows.GetWindowThreadProcessId(__hwnd)]
                gameuid = findgameuidofpath(getpidexe(self.textsource.pids[0]))
                if gameuid:
                    self.textsource.gameuid = gameuid[0]
                    self.textsource.md5 = getfilemd5(uid2gamepath[gameuid[0]])
            except:
                print_exc()

        if globalconfig["keepontop"]:
            self.translation_ui.settop()

    @textsource.setter
    def textsource(self, _):
        if _ is None and self.textsource_p:
            try:
                self.textsource_p.endX()
            except:
                print_exc()
            self.hwnd = None
        self.textsource_p = _

    @property
    def currentmd5(self):
        _ = self.textsource
        return "0" if _ is None else _.md5

    @threader
    def safeloadprocessmodels(self):
        for item in static_data["transoptimi"]:
            name = item["name"]
            try:
                checkpath = "./LunaTranslator/transoptimi/" + name + ".py"
                if os.path.exists(checkpath) == False:
                    continue
                mm = "transoptimi." + name

                Process = importlib.import_module(mm).Process

                def __(kls, _name):
                    class klass(kls):
                        @property
                        def using(self):
                            if "using_X" in dir(self):
                                try:
                                    return self.using_X
                                except:
                                    return False
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
            self.textgetmethod_1(text, is_auto_run, embedcallback, onlytrans)

    def parsehira(self, text):
        try:
            if self.hira_:
                return self.hira_.safeparse(text)
            else:
                return []
        except:
            return []

    def textgetmethod_1(
        self, text, is_auto_run=True, embedcallback=None, onlytrans=False
    ):

        safe_embedcallback = embedcallback if embedcallback else lambda _: 1
        safe_embedcallback_none = functools.partial(safe_embedcallback, "")
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
            self.currenttranslate = text
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
            return safe_embedcallback_none()
        if onlytrans == False:
            self.currentsignature = uuid.uuid4()
        try:
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
            return safe_embedcallback_none()

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
            self.currenttext = text
            self.currenttranslate = ""
            if globalconfig["read_raw"]:
                self.currentread = text
                which = self.__usewhich()
                if which.get(
                    "tts_repair_use_at_translate",
                    globalconfig["ttscommon"]["tts_repair_use_at_translate"],
                ):
                    text = self.readcurrent(needresult=True)
                else:
                    self.readcurrent()
            self.dispatchoutputer(text)

        self.transhis.getnewsentencesignal.emit(text)
        self.maybesetedittext(text)
        _showrawfunction = functools.partial(
            self.translation_ui.displayraw1.emit,
            dict(text=text, color=globalconfig["rawtextcolor"], onlytrans=onlytrans),
        )
        if globalconfig["refresh_on_get_trans"] == False:
            _showrawfunction()
            _showrawfunction = None
            _showrawfunction_sig = 0
        else:
            _showrawfunction_sig = uuid.uuid4()

        text_solved, optimization_params = self.solvebeforetrans(text)

        if is_auto_run and (
            len(text_solved) < globalconfig["minlength"]
            or len(text_solved) > globalconfig["maxlength"]
        ):
            return safe_embedcallback_none()

        self.premtalready = ["premt"]
        self.usefultranslators = list(self.translators.keys())
        no_available_translator = True
        if "premt" in self.translators:
            try:
                res = self.translators["premt"].translate(text_solved)
                for engine in res:
                    self.premtalready.append(engine)
                    if engine in globalconfig["fanyi"]:
                        _colork = engine
                    else:
                        _colork = "premt"
                    no_available_translator = False
                    self.create_translate_task(
                        onlytrans,
                        _colork,
                        optimization_params,
                        _showrawfunction,
                        _showrawfunction_sig,
                        text,
                        text_solved,
                        embedcallback,
                        is_auto_run,
                        res[engine],
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
            collect_this_time_use_engines = []
            for engine in keys:
                if engine not in self.premtalready:
                    no_available_translator = False
                    collect_this_time_use_engines.append(engine)

                thistimeusednum += 1
                self.lasttranslatorindex += 1
                if thistimeusednum >= usenum:
                    break
            for engine in globalconfig["fix_translate_rank_rank"]:
                if engine not in collect_this_time_use_engines:
                    continue

                if globalconfig["fix_translate_rank"]:
                    self.ifuse_fix_translate_rank_preprare(
                        engine, onlytrans, embedcallback
                    )

                self.create_translate_task(
                    onlytrans,
                    engine,
                    optimization_params,
                    _showrawfunction,
                    _showrawfunction_sig,
                    text,
                    text_solved,
                    embedcallback,
                    is_auto_run,
                )
        if no_available_translator:
            safe_embedcallback_none()
            if _showrawfunction:
                _showrawfunction()

    def ifuse_fix_translate_rank_preprare(self, engine, onlytrans, embedcallback):
        if onlytrans:
            return
        if embedcallback:
            return
        displayreskwargs = dict(
            name="",
            color=globalconfig["fanyi"][engine]["color"],
            res="",
            onlytrans=onlytrans,
            iter_context=(1, engine),
        )
        self.translation_ui.displayres.emit(displayreskwargs)

    def create_translate_task(
        self,
        onlytrans,
        engine,
        optimization_params,
        _showrawfunction,
        _showrawfunction_sig,
        text,
        text_solved,
        embedcallback,
        is_auto_run,
        result=None,
    ):
        callback = partial(
            self.GetTranslationCallback,
            embedcallback,
            onlytrans,
            engine,
            self.currentsignature,
            optimization_params,
            _showrawfunction,
            _showrawfunction_sig,
            text,
        )
        task = (
            callback,
            text,
            text_solved,
            embedcallback,
            is_auto_run,
            optimization_params,
        )
        if result:
            # 预翻译
            callback(result, 0)
        else:

            self.translators[engine].gettask(task)

    def GetTranslationCallback(
        self,
        embedcallback,
        onlytrans,
        classname,
        currentsignature,
        optimization_params,
        _showrawfunction,
        _showrawfunction_sig,
        contentraw,
        res,
        iter_res_status,
    ):
        if classname in self.usefultranslators:
            self.usefultranslators.remove(classname)
        if embedcallback is None and currentsignature != self.currentsignature:
            return

        safe_embedcallback = embedcallback if embedcallback else lambda _: 1
        safe_embedcallback_none = functools.partial(safe_embedcallback, "")
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
                safe_embedcallback_none()
            return

        res = self.solveaftertrans(res, optimization_params)
        if len(res) == 0:
            return
        if onlytrans == False:
            if (
                globalconfig["read_trans"]
                and globalconfig["read_translator2"] == classname
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
                iter_context=(iter_res_status, classname),
            )
            self.translation_ui.displayres.emit(displayreskwargs)

        if iter_res_status in (0, 2):  # 0为普通，1为iter，2为iter终止
            try:
                self.textsource.sqlqueueput((contentraw, classname, res))
            except:
                pass
            if len(self.currenttranslate):
                self.currenttranslate += "\n"
            self.currenttranslate += res
            if (
                globalconfig["embedded"]["as_fast_as_posible"]
                or classname == globalconfig["embedded"]["translator_2"]
            ):
                return safe_embedcallback(
                    kanjitrans(zhconv.convert(res, "zh-tw"))
                    if globalconfig["embedded"]["trans_kanji"]
                    else res
                )

    def __usewhich(self):

        try:
            for _ in (0,):

                if not self.textsource:
                    break

                gameuid = self.textsource.gameuid
                if not gameuid:
                    break
                if savehook_new_data[gameuid]["tts_follow_default"]:
                    break
                return savehook_new_data[gameuid]
        except:
            pass
        return globalconfig["ttscommon"]

    def ttsrepair(self, text, usedict):
        if usedict["tts_repair"]:
            text = parsemayberegexreplace(usedict["tts_repair_regex"], text)
        return text

    def matchwhich(self, dic: dict, res: str):

        for item in dic:
            if item["regex"]:
                retext = codecs.escape_decode(bytes(item["key"], "utf-8"))[0].decode(
                    "utf-8"
                )
                if item["condition"] == 1:
                    if re.search(retext, res):
                        return item
                elif item["condition"] == 0:
                    if re.match(retext, res) or re.search(retext + "$", res):
                        # 用^xxx|xxx$有可能有点危险
                        return item
            else:
                if item["condition"] == 1:
                    if (
                        res.isascii()
                        and item["key"].isascii()
                        and (" " not in item["key"])
                    ):  # 目标可能有空格
                        resx = res.split(" ")
                        for i in range(len(resx)):
                            if resx[i] == item["key"]:
                                return item
                    else:
                        if item["key"] in res:
                            return item
                elif item["condition"] == 0:
                    if res.startswith(item["key"]) or res.endswith(item["key"]):
                        return item
        return None

    def ttsskip(self, text, usedict) -> dict:
        if usedict["tts_skip"]:
            return self.matchwhich(usedict["tts_skip_regex"], text)
        return None

    @threader
    def __readcurrent(self, text1, text2, force=False):
        if (not force) and (not globalconfig["autoread"]):
            return
        matchitme = self.ttsskip(text1, self.__usewhich())
        reader = None
        if matchitme is None:
            reader = self.reader
        else:
            target = matchitme.get("target", "default")
            if target == "default":
                reader = self.reader
            elif target == "skip":
                if not force:
                    return
                reader = self.reader
            else:
                engine, voice, _ = target
                key = str((engine, voice))  # voice可能是list，无法hash
                reader = self.specialreaders.get(key, None)
                if reader == -1:
                    reader = self.reader
                elif reader is None:
                    try:
                        reader = self.loadreader(engine, privateconfig={"voice": voice})
                        self.specialreaders[key] = reader
                    except:
                        reader = self.reader
                        self.specialreaders[key] = -1
        if reader is None:
            return
        if text2 is None:
            text2 = self.ttsrepair(text1, self.__usewhich())
        reader.read(text2, force)

    def readcurrent(self, force=False, needresult=False):
        if needresult:
            text = self.ttsrepair(self.currentread, self.__usewhich())
            self.__readcurrent(self.currentread, text, force)
            return text
        else:
            self.__readcurrent(self.currentread, None, force)

    def loadreader(self, use, privateconfig=None, init=True, uid=None):
        aclass = importlib.import_module("tts." + use).TTS
        if uid is None:
            uid = uuid.uuid4()
        obj = aclass(use, self.audioplayer.play, privateconfig, init, uid)
        return obj

    def __reader_usewhich(self):

        for key in globalconfig["reader"]:
            if globalconfig["reader"][key]["use"] and os.path.exists(
                ("./LunaTranslator/tts/" + key + ".py")
            ):
                return key
        return None

    @threader
    def startreader(self, use=None, checked=True, setting=False):
        if setting:
            if use != self.__reader_usewhich():
                return
            self.reader = None
            self.reader_uid = uuid.uuid4()
            self.reader = self.loadreader(use, uid=self.reader_uid)
            return
        if not checked:
            self.reader = None
            return
        if use is None:
            use = self.__reader_usewhich()
        if not use:
            self.reader = None
            return
        self.reader = None
        self.reader_uid = uuid.uuid4()
        self.reader = self.loadreader(use, uid=self.reader_uid)

    def selectprocess(self, selectedp, title):
        self.textsource = None
        pids, pexe, hwnd = selectedp
        if len(collect_running_pids(pids)) == 0:
            return
        if not title:
            title = windows.GetWindowText(hwnd)

        if not globalconfig["sourcestatus2"]["texthook"]["use"]:
            return
        found = findgameuidofpath(pexe)
        if found:
            gameuid, reflist = found
            if globalconfig["startgamenototop"] == False:
                idx = reflist.index(gameuid)
                reflist.insert(0, reflist.pop(idx))
        else:
            gameuid = find_or_create_uid(savehook_new_list, pexe, title)
            savehook_new_list.insert(0, gameuid)

        self.textsource = texthook(pids, pexe, gameuid, autostart=False)
        self.hwnd = hwnd
        self.textsource.start()

    def starttextsource(self, use=None, checked=True):
        self.translation_ui.showhidestate = False
        self.translation_ui.refreshtooliconsignal.emit()

        self.translation_ui.set_color_transparency()
        self.translation_ui.adjustbuttons()
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
            which = translate_exits(classname, which=True)
            if which is None:
                return None
            if which == 0:
                aclass = importlib.import_module("translator." + classname).TS
            elif which == 1:
                aclass = importlib.import_module("userconfig.copyed." + classname).TS
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
            use = globalconfig[fanyiorcishu][_type]["use"]
            rankkeys = {"cishu": "cishuvisrank", "fanyi": "fix_translate_rank_rank"}
            rankkey = rankkeys.get(fanyiorcishu)
            if use:
                if _type not in globalconfig[rankkey]:
                    globalconfig[rankkey].append(_type)
            else:

                if _type in globalconfig[rankkey]:
                    globalconfig[rankkey].remove(_type)

            if not use:

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

    def maybesetedittext(self, text):
        if self.edittextui:
            try:
                self.edittextui.getnewsentencesignal.emit(text)
            except:
                print_exc()
        self.edittextui_cached = text

    def createedittextui(self):
        try:
            self.edittextui = edittext(self.commonstylebase, self.edittextui_cached)
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
                self.commonstylebase, self.selectprocess, self.hookselectdialog
            )
            if self.AttachProcessDialog:
                self.AttachProcessDialog.show()
        except:
            print_exc()

    def autohookmonitorthread(self):
        def onwindowloadautohook():
            textsourceusing = globalconfig["sourcestatus2"]["texthook"]["use"]
            if not (globalconfig["autostarthook"] and textsourceusing):
                return
            elif self.AttachProcessDialog and self.AttachProcessDialog.isVisible():
                return
            if self.textsource is not None:
                return
            hwnd = windows.GetForegroundWindow()
            pid = windows.GetWindowThreadProcessId(hwnd)
            name_ = getpidexe(pid)
            if not name_:
                return
            found = findgameuidofpath(name_)
            if not found:
                return
            uid, reflist = found
            pids = ListProcess(name_)
            if self.textsource is not None:
                return
            if not globalconfig["sourcestatus2"]["texthook"]["use"]:
                return
            if globalconfig["startgamenototop"] == False:
                idx = reflist.index(uid)
                reflist.insert(0, reflist.pop(idx))
            self.textsource = texthook(pids, name_, uid, autostart=True)
            self.hwnd = hwnd
            self.textsource.start()

        while self.isrunning:
            try:
                onwindowloadautohook()
            except:
                print_exc()
            time.sleep(0.5)
            # 太短了的话，中间存在一瞬间，后台进程比前台窗口内存占用要大。。。

    def setdarkandbackdrop(self, widget, dark):
        if self.__dontshowintaborsetbackdrop(widget):
            return
        winsharedutils.SetTheme(
            int(widget.winId()), dark, globalconfig["WindowBackdrop"]
        )

    @threader
    def clickwordcallback(self, word, append):
        if globalconfig["usewordorigin"] == False:
            word = word["orig"]
        else:
            word = word.get("origorig", word["orig"])

        if globalconfig["usecopyword"]:
            if append:
                winsharedutils.clipboard_set(winsharedutils.clipboard_get() + word)
            else:
                winsharedutils.clipboard_set(word)
        if globalconfig["usesearchword"]:
            self.searchwordW.search_word.emit(word, append)

    def __dontshowintaborsetbackdrop(self, widget):
        window_flags = widget.windowFlags()
        if (
            Qt.WindowType.FramelessWindowHint & window_flags
            == Qt.WindowType.FramelessWindowHint
        ):
            return True
        return False

    def setshowintab_checked(self, widget):
        try:
            self.translation_ui
        except:
            return
        if widget == self.translation_ui:
            winsharedutils.showintab(
                int(widget.winId()), globalconfig["showintab"], True
            )
            return
        if self.__dontshowintaborsetbackdrop(widget):
            return
        if isinstance(widget, (QMenu, QFrame)):
            return
        if (
            isinstance(widget, QWidget)
            and widget.parent() is None
            and len(widget.children()) == 0
        ):
            # combobox的下拉框，然后这个widget会迅速销毁，会导致任务栏闪一下。没别的办法了姑且这样过滤一下
            return
        winsharedutils.showintab(
            int(widget.winId()), globalconfig["showintab_sub"], False
        )

    def inittray(self):
        self.tray = QSystemTrayIcon()
        self.tray.setIcon(getExeIcon(getcurrexe()))
        trayMenu = LMenu(self.commonstylebase)
        showAction = LAction("显示", trayMenu)
        showAction.triggered.connect(self.translation_ui.show_)
        settingAction = LAction(qtawesome.icon("fa.gear"), "设置", trayMenu)
        settingAction.triggered.connect(self.settin_ui.showsignal)
        quitAction = LAction(qtawesome.icon("fa.times"), "退出", trayMenu)
        quitAction.triggered.connect(self.translation_ui.close)
        trayMenu.addAction(showAction)
        trayMenu.addAction(settingAction)
        trayMenu.addSeparator()
        trayMenu.addAction(quitAction)
        trayMenu.addAction(showAction)
        trayMenu.addAction(settingAction)
        trayMenu.addSeparator()
        trayMenu.addAction(quitAction)
        self.tray.setContextMenu(trayMenu)
        self.tray.activated.connect(self.leftclicktray)
        self.tray.messageClicked.connect(winsharedutils.dispatchcloseevent)
        self.tray.show()

    def leftclicktray(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.translation_ui.showhideui()

    def showtraymessage(self, title, message):
        self.tray.showMessage(_TR(title), _TR(message), getExeIcon(getcurrexe()))

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
            self.setdarkandbackdrop(widget, dark)
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
        style += f"""
        QListWidget {{
                font:{globalconfig["settingfontsize"] + 4}pt  {globalconfig["settingfonttype"]};  }}
            """
        self.commonstylebase.setStyleSheet(style)
        font = QFont()
        font.setFamily(globalconfig["settingfonttype"])
        font.setPointSizeF(globalconfig["settingfontsize"])
        QApplication.instance().setFont(font)

    def parsedefaultfont(self):
        for k in ["fonttype", "fonttype2", "settingfonttype"]:
            if globalconfig[k] == "":
                l = "ja" if k == "fonttype" else getlanguse()
                set_font_default(l, k)
                # globalconfig[k] = QFontDatabase.systemFont(
                #     QFontDatabase.SystemFont.GeneralFont
                # ).family()

    def loadui(self):
        self.installeventfillter()
        self.parsedefaultfont()
        self.loadmetadatas()
        self.translation_ui = TranslatorWindow()
        winsharedutils.showintab(
            int(self.translation_ui.winId()), globalconfig["showintab"], True
        )
        self.translation_ui.show()
        self.translation_ui.aftershowdosomething()
        self.mainuiloadafter()

    def mainuiloadafter(self):
        self.__checkmutethread()
        self.safeloadprocessmodels()
        self.prepare()
        self.startxiaoxueguan()
        self.starthira()
        self.startoutputer()
        self.commonstylebase = commonstylebase(self.translation_ui)
        self.setcommonstylesheet()
        self.settin_ui = Setting(self.commonstylebase)
        self.transhis = transhist(self.commonstylebase)
        self.startreader()
        self.searchwordW = searchwordW(self.commonstylebase)
        self.hookselectdialog = hookselect(self.commonstylebase)
        self.starttextsource()
        threading.Thread(target=self.autohookmonitorthread).start()
        threading.Thread(
            target=minmaxmoveobservefunc, args=(self.translation_ui,)
        ).start()
        self.messagecallback__ = CFUNCTYPE(None, c_int, c_void_p)(self.messagecallback)
        winsharedutils.globalmessagelistener(self.messagecallback__)
        self.inittray()
        self.playtimemanager = playtimemanager()
        self.__count = 0

    @threader
    def __checkmutethread(self):
        while True:
            time.sleep(0.5)
            if not self.hwnd:
                continue
            pid = windows.GetWindowThreadProcessId(self.hwnd)
            if not pid:
                continue
            _mute = winsharedutils.GetProcessMute(pid)
            if self.translation_ui.processismuteed != _mute:
                self.translation_ui.processismuteed = _mute
                self.translation_ui.refreshtooliconsignal.emit()

    def openlink(self, file):
        if file.startswith("http") and checkisusingwine():
            self.translation_ui.displaylink.emit(file)
            return
        return os.startfile(file)

    def messagecallback(self, msg, param):
        if msg == 0:
            if globalconfig["darklight2"] == 0:
                if self.__count % 2:
                    self.commonstylebase.setstylesheetsignal.emit()
                self.__count += 1
        elif msg == 1:
            if bool(param):
                self.translation_ui.settop()
            else:
                if not globalconfig["keepontop"]:
                    self.translation_ui.canceltop()
        elif msg == 2:
            self.translation_ui.closesignal.emit()

    def _dowhenwndcreate(self, obj):
        hwnd = obj.winId()
        if not hwnd:  # window create/destroy,when destroy winId is None
            return
        windows.SetProp(
            int(obj.winId()),
            "Magpie.ToolWindow",
            windows.HANDLE(1),
        )
        winsharedutils.setdwmextendframe(int(hwnd))
        if self.currentisdark is not None:
            self.setdarkandbackdrop(obj, self.currentisdark)
        self.setshowintab_checked(obj)

    def installeventfillter(self):
        class WindowEventFilter(QObject):
            def eventFilter(_, obj: QObject, event: QEvent):
                if event.type() == QEvent.Type.LanguageChange:
                    if "updatelangtext" in dir(obj):
                        obj.updatelangtext()
                elif event.type() == QEvent.Type.WinIdChange:
                    self._dowhenwndcreate(obj)

                return False

        self.currentisdark = None
        self.__filter = WindowEventFilter()  # keep ref
        QApplication.instance().installEventFilter(self.__filter)

    def loadmetadatas(self):

        for k in globalconfig["metadata"]:
            try:
                targetmod[k] = importlib.import_module(f"metadata.{k}").searcher(k)
            except:
                print_exc()

    @tryprint
    def urlprotocol(self):

        key = winreg.CreateKey(
            winreg.HKEY_CURRENT_USER, r"Software\Classes\lunatranslator"
        )
        winreg.SetValue(key, None, winreg.REG_SZ, "URL:lunatranslator")
        winreg.SetValueEx(key, r"URL Protocol", 0, winreg.REG_SZ, "")
        keysub = winreg.CreateKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Classes\lunatranslator\shell\open\command",
        )
        command = f'"{getcurrexe()}" --URLProtocol "%1"'
        winreg.SetValue(keysub, r"", winreg.REG_SZ, command)
