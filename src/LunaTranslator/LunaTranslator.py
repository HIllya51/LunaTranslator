import time, uuid, json
import os, threading, re, winreg, copy
from qtsymbols import *
from traceback import print_exc
from sometypes import TranslateResult, TranslateError, WordSegResult
from myutils.config import (
    globalconfig,
    savehook_new_list,
    findgameuidofpath,
    magpie_config,
    savehook_new_data,
    static_data,
    translatorsetting,
    getlanguse,
    _TR,
    isascii,
)
from ctypes import cast, c_void_p, c_wchar_p
from myutils.keycode import mod_map_r
from gobject import sys_le_xp
from myutils.mecab import mecab, latin
from myutils.utils import (
    parsemayberegexreplace,
    dynamiclink,
    find_or_create_uid,
    parsekeystringtomodvkcode,
    checkisusingwine,
    checkpostusing,
    checkmd5reloadmodule,
    stringfyerror,
    targetmod,
    translate_exits,
    safe_escape,
)
from language import Languages
from myutils.wrapper import threader, tryprint
from gui.showword import searchwordW
from myutils.hwnd import getExeIcon, getcurrexe
from textio.textsource.copyboard import copyboard
from textio.textsource.texthook import texthook
from textio.textsource.ocrtext import ocrtext
from textio.textsource.textsourcebase import basetext
from textio.textsource.filetrans import filetrans
from textio.textsource.mssr import mssr
from gui.selecthook import hookselect
from gui.translatorUI import TranslatorWindow
import functools, gobject
from gui.transhist import transhist
from gui.edittext import edittext
from gui.flowsearchword import WordViewTooltip
import importlib, qtawesome
from functools import partial
from gui.attachprocessdialog import AttachProcessDialog
import windows
import NativeUtils
from gui.gamemanager.common import startgame
from myutils.post import POSTSOLVE
from myutils.utils import nowisdark, dynamicapiname
from myutils.traceplaytime import playtimemanager
from myutils.audioplayer import series_audioplayer
from gui.dynalang import LAction, LDialog
from gui.usefulwidget import pixmapviewer
from gui.setting.setting import Setting
from gui.usefulwidget import PopupWidget
from gui.rendertext.texttype import TextType, SpecialColor, TranslateColor
from network.server.servicecollection import registerall
from network.server.tcpservice import TCPService
from tts.basettsclass import TTSbase
from cishu.cishubase import cishubase
from translator.basetranslator import basetrans
from textio.textoutput.outputerbase import Base as outputerbase
from myutils.updater import versioncheckthread


class BASEOBJECT(QObject):
    setstylesheetsignal = pyqtSignal()
    safeinvokefunction = pyqtSignal(object)
    setimage = pyqtSignal(QImage)
    setresult = pyqtSignal(object)
    voicelistsignal = pyqtSignal(object)
    portconflict = pyqtSignal(str)
    thresholdsett2 = pyqtSignal(str)
    thresholdsett1 = pyqtSignal(str)
    progresssignal2 = pyqtSignal(str, int)
    progresssignal3 = pyqtSignal(int)
    progresssignal4 = pyqtSignal(str, int)
    versiontextsignal = pyqtSignal(str)
    clipboardcallback = pyqtSignal(bool, str)
    hover_search_word = pyqtSignal(str, str, bool, bool, bool)
    settin_ui_showsignal = pyqtSignal()
    showandsolvesig = pyqtSignal(str, str)
    selecthookbuttonstatus = pyqtSignal(bool)
    backtransparentstatus = pyqtSignal(bool)
    show_fany_switch = pyqtSignal(bool)
    show_original_switch = pyqtSignal(bool)
    sourceswitchs = pyqtSignal(str, bool)
    fenyinsettings = pyqtSignal(bool)
    dispatch_translate = pyqtSignal(str, str)
    showupdatebtn = pyqtSignal()
    createimageviewsig = pyqtSignal(QWidget)

    def connectsignal(self, signal: pyqtBoundSignal, callback):
        if signal in self.__cachesignal:
            signal.disconnect()
            callback(*self.__cachesignal[signal])
        signal.connect(callback)

    def __connect_internal(self, signal: pyqtBoundSignal):
        signal.connect(functools.partial(self.__connect_internal_1, signal))

    def __connect_internal_1(self, signal, *arg):
        self.__cachesignal[signal] = arg

    def __safeinvoke(self, fobj):
        try:
            fobj()
        except:
            print_exc()

    def initsignals(self):
        self.__cachesignal: "dict[pyqtBoundSignal, tuple]" = {}
        self.__connect_internal(self.dispatch_translate)
        self.__connect_internal(self.portconflict)
        self.__connect_internal(self.thresholdsett1)
        self.__connect_internal(self.thresholdsett2)
        self.__connect_internal(self.voicelistsignal)
        self.__connect_internal(self.setresult)
        self.__connect_internal(self.setimage)
        self.safeinvokefunction.connect(self.__safeinvoke)
        self.setstylesheetsignal.connect(self.setcommonstylesheet)
        self.__connect_internal(self.progresssignal2)
        self.__connect_internal(self.progresssignal3)
        self.__connect_internal(self.progresssignal4)
        self.__connect_internal(self.versiontextsignal)
        self.__connect_internal(self.showandsolvesig)
        self.__connect_internal(self.showupdatebtn)
        self.createimageviewsig.connect(self.createimageview)

    def __init__(self) -> None:
        super().__init__()
        self.initsignals()
        self.currentisdark = None
        self.update_avalable = False
        self.translators: "dict[str, basetrans]" = {}
        self.cishus: "dict[str, cishubase]" = {}
        self.specialreaders: "dict[object, TTSbase]" = {}
        self.textsource_p: basetext = None
        self.currenttext = ""
        self.currenttranslate = ""
        self.currentread = ""
        self.currentread_from_origin = None
        self.refresh_on_get_trans_signature = 0
        self.currentsignature = None
        self.isrunning = True
        self.solvegottextlock = threading.Lock()
        self.gettranslatelock = threading.Lock()
        self.outputers: "dict[str, outputerbase]" = {}
        self.processmethods = []
        self.AttachProcessDialog = None
        self.edittextui = None
        self.edittextui_cached = None
        self.notifyonce = set()
        self.audioplayer = series_audioplayer(playovercallback=self.ttsautoforward)
        self._internal_reader = None
        self.reader_uid = None
        self.__hwnd = None
        self.gameuid = 0
        self.autoswitchgameuid = True
        self.istriggertoupdate = False
        self.thishastranslated = True
        self.service = TCPService()
        registerall(self.service)

    def createimageview(self, parent):
        m = LDialog(parent, Qt.WindowType.WindowCloseButtonHint)
        m.setWindowTitle("微信赞赏码")
        lb = pixmapviewer()
        l = QHBoxLayout(m)
        l.addWidget(lb)
        img = QPixmap.fromImage(QImage("files/static/zan.jpg"))
        lb.showpixmap(img)
        m.resize(500, 500)
        m.exec()

    @threader
    def serviceinit(self):
        gobject.base.portconflict.emit("")
        self.service.stop()
        if globalconfig["networktcpenable"]:
            try:
                self.service.init(globalconfig["networktcpport"])
            except OSError:
                gobject.base.portconflict.emit("端口冲突")

    @threader
    def ttsautoforward(self):
        if not globalconfig["ttsautoforward"]:
            return
        if not globalconfig["autorun"]:
            return
        windows.SetForegroundWindow(self.hwnd)
        time.sleep(0.001)
        windows.keybd_event(windows.VK_RETURN, 0, 0, 0)
        time.sleep(0.001)
        windows.keybd_event(windows.VK_RETURN, 0, windows.KEYEVENTF_KEYUP, 0)

    @property
    def reader(self) -> TTSbase:
        return self._internal_reader

    @reader.setter
    def reader(self, _):
        if _ is None:
            self._internal_reader = None
            self.reader_uid = None
            gobject.base.voicelistsignal.emit(None)
        else:
            if self.reader_uid != _.uid:
                return
            self._internal_reader = _
            gobject.base.voicelistsignal.emit(_)

    @property
    def textsource(self) -> basetext:
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
            if self.autoswitchgameuid:
                self.gameuid = 0
        else:
            _pid = windows.GetWindowThreadProcessId(__hwnd)
            if _pid:
                NativeUtils.MonitorPidVolume(_pid)
                self.translation_ui.isbindedwindow = True
                self.translation_ui.refreshtooliconsignal.emit()
                try:
                    if self.autoswitchgameuid:
                        gameuid, _ = findgameuidofpath(windows.GetProcessFileName(_pid))
                        if gameuid:
                            self.gameuid = gameuid
                except:
                    print_exc()
            else:
                if self.autoswitchgameuid:
                    self.gameuid = 0
        if globalconfig["keepontop"]:
            self.translation_ui.settop()

    @textsource.setter
    def textsource(self, _):
        if _ is None:
            if self.textsource_p:
                try:
                    self.textsource_p.endX()
                except:
                    print_exc()
            self.autoswitchgameuid = True
            self.hwnd = None
            self.gameuid = 0
        self.textsource_p = _

    @threader
    def safeloadprocessmodels(self):
        for item in static_data["transoptimi"]:
            name = item["name"]
            try:
                checkpath = "LunaTranslator/transoptimi/" + name + ".py"
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

    def parsehira(self, text):
        need = (
            globalconfig["isshowhira"]
            or globalconfig["show_fenci"]
            or self.translation_ui.translate_text.textbrowser._clickhovershow
        )
        if not need:
            return []
        try:
            if self.mecab_:
                return self.mecab_.safeparse(text)
            else:
                raise Exception()
        except:
            return latin().safeparse(text)

    def displayinfomessage(self, text, infotype):
        if infotype == "<notrans>":
            self.translation_ui.displayres.emit(
                dict(
                    color=SpecialColor.RawTextColor,
                    res=text,
                    clear=True,
                    klass=str(uuid.uuid4()),
                )
            )
            self.currenttext = text
            self.currenttranslate = text
            self.currentread = text
            self.currentread_from_origin = False
            return
        elif infotype == "<msg_info_append>":
            self.translation_ui.displayres.emit(
                dict(color=SpecialColor.RawTextColor, res=text, klass=str(uuid.uuid4()))
            )
        else:
            msgs = [
                ("<msg_info_refresh>", TextType.Info),
                ("<msg_error_Translator>", TextType.Error_translator),
                ("<msg_error_Origin>", TextType.Error_origin),
            ]
            for msg, t in msgs:
                if infotype == msg:
                    self.translation_ui.displaystatus.emit(text, t)
                    return

    def maybeneedtranslateshowhidetranslate(self):
        if globalconfig["showfanyi"]:
            if not self.thishastranslated:
                self.textgetmethod(self.currenttext, is_auto_run=False)
            self.translation_ui.translate_text.showhidetranslate(True)
        else:
            self.translation_ui.translate_text.showhidetranslate(False)

    def updaterawtext(self, text):
        self.currentread = text
        self.translation_ui.displayraw2.emit(text)

    def textgetmethod(
        self,
        text,
        is_auto_run=True,
        waitforresultcallback=None,
        waitforresultcallbackengine=None,
        waitforresultcallbackengine_force=False,
        erroroutput=None,
        donttrans=False,
        updateTranslate=False,
    ):
        with self.solvegottextlock:
            succ = self.textgetmethod_1(
                text,
                is_auto_run=is_auto_run,
                waitforresultcallback=waitforresultcallback,
                waitforresultcallbackengine=waitforresultcallbackengine,
                waitforresultcallbackengine_force=waitforresultcallbackengine_force,
                erroroutput=erroroutput,
                donttrans=donttrans,
                updateTranslate=updateTranslate,
            )
            if waitforresultcallback and not succ:
                waitforresultcallback(TranslateResult())

    def __erroroutput(self, klass, erroroutput, _showrawfunction, e, t):

        if erroroutput:
            return erroroutput(TranslateError(klass, e))
        if klass:
            e = _TR(dynamicapiname(klass)) + " " + e
        self._delayshowraw(_showrawfunction)
        self.translation_ui.displaystatus.emit(e, t)

    def textgetmethod_1(
        self,
        text: str,
        is_auto_run=True,
        waitforresultcallback=None,
        waitforresultcallbackengine=None,
        waitforresultcallbackengine_force=False,
        erroroutput=None,
        donttrans=False,
        updateTranslate=False,
    ):
        if not text:
            return
        if not text.strip():
            return
        if is_auto_run and text == self.currenttext:
            return
        origin = text
        __erroroutput = functools.partial(self.__erroroutput, None, erroroutput, None)
        currentsignature = uuid.uuid4()
        try:
            text = POSTSOLVE(text, isEx=waitforresultcallback)
            gobject.base.showandsolvesig.emit(origin, text)
            if not text:
                return
            if not text.strip():
                return
        except Exception as e:
            __erroroutput(stringfyerror(e), TextType.Error_origin)
            return

        if is_auto_run and text == self.currenttext:
            return
        self.currentsignature = currentsignature
        if is_auto_run and (
            len(text) < globalconfig["minlength"]
            or len(text) > globalconfig["maxlength"]
        ):

            if len(text) > globalconfig["maxlength"]:
                text = text[: globalconfig["maxlength"]] + "……"

            self.translation_ui.displayraw1.emit(text, updateTranslate)
            self.transhis.getnewsentencesignal.emit(text)
            self.maybesetedittext(text)
            return

        try:
            self.textsource.sqlqueueput((text, origin))
        except:
            pass
        if donttrans:
            return
        _showrawfunction_unsafe = None
        if not waitforresultcallback:
            self.currenttext = text
            self.currenttranslate = ""
            if globalconfig["read_raw"]:
                self.currentread = text
                self.currentread_from_origin = True
                self.readcurrent()
            self.dispatchoutputer(text, True)

            _showrawfunction_unsafe = functools.partial(
                self.translation_ui.displayraw1.emit, text, updateTranslate
            )
            self.thishastranslated = globalconfig["showfanyi"]
        _showrawfunction = lambda: (
            _showrawfunction_unsafe() if _showrawfunction_unsafe else None
        )
        self.transhis.getnewsentencesignal.emit(text)
        self.maybesetedittext(text)

        if not waitforresultcallback and not globalconfig["showfanyi"]:
            return _showrawfunction()

        text_solved, optimization_params = self.solvebeforetrans(text)

        maybehaspremt = {}
        skip_other_on_success = False
        fix_rank = globalconfig["fix_translate_rank_rank"].copy()
        if ("rengong" in self.translators) and (
            not (is_auto_run and globalconfig["fanyi"]["rengong"].get("manual", False))
        ):
            contentraw = self.analyzecontent(text_solved, optimization_params)
            try:
                res = self.translators["rengong"].translate(contentraw)
            except:
                print_exc()
                res = None
            maybehaspremt["rengong"] = res
            skip_other_on_success = (
                res and self.translators["rengong"].config["skip_other_on_success"]
            )

        if (
            (not skip_other_on_success)
            and ("premt" in self.translators)
            and (
                not (
                    is_auto_run and globalconfig["fanyi"]["premt"].get("manual", False)
                )
            )
        ):
            contentraw = self.analyzecontent(text_solved, optimization_params)
            try:
                maybehaspremt = self.translators["premt"].translate(contentraw)
            except:
                print_exc()
            other = list(set(maybehaspremt.keys()) - set(fix_rank))
            idx = fix_rank.index("premt")
            fix_rank = fix_rank[:idx] + other + fix_rank[idx + 1 :]

        real_fix_rank = []
        if skip_other_on_success:
            real_fix_rank.append("rengong")
        else:
            for engine in fix_rank:
                if (engine not in self.translators) and (engine not in maybehaspremt):
                    continue
                real_fix_rank.append(engine)

        if len(real_fix_rank) == 0:
            return _showrawfunction()

        if waitforresultcallbackengine:
            if waitforresultcallbackengine in real_fix_rank:
                real_fix_rank = [waitforresultcallbackengine]
            elif waitforresultcallbackengine_force:
                return

        usefultranslators = real_fix_rank.copy()
        if globalconfig["fix_translate_rank"] and (not waitforresultcallback):
            _showrawfunction = functools.partial(
                self._delaypreparefixrank, _showrawfunction, real_fix_rank
            )
        if not (updateTranslate or globalconfig["refresh_on_get_trans"]):
            _showrawfunction()
            _showrawfunction = None
        read_trans_once_check = []
        for engine in real_fix_rank:
            if engine in globalconfig["fanyi"]:
                _colork = engine
            else:
                _colork = "premt"
            self.create_translate_task(
                currentsignature,
                usefultranslators,
                _colork,
                optimization_params,
                _showrawfunction,
                text,
                text_solved,
                waitforresultcallback,
                is_auto_run,
                result=maybehaspremt.get(engine),
                read_trans_once_check=read_trans_once_check,
                erroroutput=erroroutput,
            )
        return True

    def analyzecontent(self, text_solved, optimization_params):
        for _ in optimization_params:
            if isinstance(_, dict):
                _gpt_dict = _.get("gpt_dict", None)
                if _gpt_dict is None:
                    continue
                return _.get("gpt_dict_origin")
        return text_solved

    def _delaypreparefixrank(self, _showrawfunction, real_fix_rank):
        _showrawfunction()
        for engine in real_fix_rank:
            if engine not in globalconfig["fanyi"]:
                engine = "premt"
            displayreskwargs = dict(
                name="",
                color=TranslateColor(engine),
                res="",
                iter_context=(1, engine),
                klass=engine,
            )
            self.translation_ui.displayres.emit(displayreskwargs)

    def create_translate_task(
        self,
        currentsignature,
        usefultranslators,
        engine,
        optimization_params,
        _showrawfunction,
        text,
        text_solved,
        waitforresultcallback,
        is_auto_run,
        result,
        read_trans_once_check: list,
        erroroutput,
    ):
        callback = partial(
            self.GetTranslationCallback,
            usefultranslators,
            waitforresultcallback,
            engine,
            currentsignature,
            optimization_params,
            _showrawfunction,
            text,
            read_trans_once_check,
            erroroutput,
        )
        task = (
            callback,
            text_solved,
            waitforresultcallback,
            is_auto_run,
            optimization_params,
        )
        if result:
            # 预翻译
            callback(result, 1)
            callback(result, 2)
        else:

            self.translators[engine].gettask(task)

    def __safecallback(self, waitforresultcallback, klass, result=None):
        if not waitforresultcallback:
            return
        waitforresultcallback(TranslateResult(klass, result))

    def _delayshowraw(self, _showrawfunction):
        needshowraw = (
            _showrawfunction and self.refresh_on_get_trans_signature != _showrawfunction
        )
        if needshowraw:
            self.refresh_on_get_trans_signature = _showrawfunction
            _showrawfunction()

    def GetTranslationCallback(
        self,
        usefultranslators: list,
        waitforresultcallback,
        classname,
        currentsignature,
        optimization_params,
        _showrawfunction,
        contentraw,
        read_trans_once_check: list,
        erroroutput,
        res: str,
        iter_res_status,
        iserror=False,
    ):
        with self.gettranslatelock:
            if classname in usefultranslators:
                usefultranslators.remove(classname)
            if (
                waitforresultcallback is None
                and currentsignature != self.currentsignature
            ):
                return

            safe_callback = functools.partial(
                self.__safecallback, waitforresultcallback, classname
            )
            __erroroutput = functools.partial(
                self.__erroroutput, classname, erroroutput, _showrawfunction
            )
            if iserror:
                if erroroutput or (currentsignature == self.currentsignature):
                    __erroroutput(res, TextType.Error_translator)
                if len(usefultranslators) == 0:
                    safe_callback()
                return

            res = self.solveaftertrans(res, optimization_params)
            if not res:
                if len(usefultranslators) == 0:
                    safe_callback()
                return
            self._delayshowraw(_showrawfunction)
            if (
                (currentsignature == self.currentsignature)
                and (iter_res_status in (0, 1))
                and (not waitforresultcallback)
            ):
                displayreskwargs = dict(
                    name=_TR(dynamicapiname(classname)),
                    color=TranslateColor(classname),
                    res=res,
                    iter_context=(iter_res_status, classname),
                    klass=classname,
                )
                self.translation_ui.displayres.emit(displayreskwargs)
            if iter_res_status in (0, 2):  # 0为普通，1为iter，2为iter终止

                self.transhis.getnewtranssignal.emit(
                    _TR(dynamicapiname(classname)), res
                )
                if not waitforresultcallback:
                    if (
                        globalconfig["read_trans"]
                        and (not read_trans_once_check)
                        and (
                            (globalconfig["toppest_translator"] == classname)
                            or ((not globalconfig["toppest_translator"]))
                        )
                    ):
                        self.currentread = res
                        self.currentread_from_origin = False
                        self.readcurrent()
                        read_trans_once_check.append(classname)

                    self.dispatchoutputer(res, False)
                try:
                    self.textsource.sqlqueueput((contentraw, classname, res))
                except:
                    pass
                gobject.base.dispatch_translate.emit(classname, res)
                if len(self.currenttranslate):
                    self.currenttranslate += "\n"
                self.currenttranslate += res
                safe_callback(res)

    def __usewhich(self):

        try:
            for _ in (0,):
                gameuid = self.gameuid
                if not gameuid:
                    break
                if savehook_new_data[gameuid].get("tts_follow_default", True):
                    break
                tts_repair_merge = savehook_new_data[gameuid].get(
                    "tts_repair_merge", False
                )
                tts_skip_merge = savehook_new_data[gameuid].get("tts_skip_merge", False)
                if tts_skip_merge or tts_repair_merge:
                    _this = {"tts_repair_regex": [], "tts_skip_regex": []}
                    _this.update(copy.deepcopy(savehook_new_data[gameuid]))
                    if tts_repair_merge:
                        _ = copy.deepcopy(globalconfig["ttscommon"]["tts_repair_regex"])
                        _this["tts_repair_regex"] += _
                    if tts_skip_merge:
                        _ = copy.deepcopy(globalconfig["ttscommon"]["tts_skip_regex"])
                        _this["tts_skip_regex"] += _
                    return _this
                return savehook_new_data[gameuid]
        except:
            pass
        return globalconfig["ttscommon"]

    def ttsprocess(self, path, text):
        path1 = "userconfig/posts/{}.py".format(path)
        if not os.path.exists(path1):
            return text
        return checkmd5reloadmodule(path1, "posts." + path)[1].POSTSOLVE(text)

    def ttsrepair(self, text, usedict: dict):
        if usedict.get("tts_repair", False):
            if usedict.get("ttsprocess_use", False):
                try:
                    text = self.ttsprocess(usedict.get("ttsprocess_path"), text)
                except:
                    print_exc()
            text = parsemayberegexreplace(usedict.get("tts_repair_regex", []), text)
        return text

    def matchwhich(self, dic: dict, res: str, isorigin: bool):

        for item in dic:
            range_ = item.get("range", 0)
            if range_ and ((range_ == 1) ^ isorigin):
                continue
            if item["regex"]:
                retext = safe_escape(item["key"])
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
                        isascii(res)
                        and isascii(item["key"])
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

    def ttsskip(self, text, usedict, isorigin) -> dict:
        if usedict.get("tts_skip", False):
            return self.matchwhich(usedict.get("tts_skip_regex", []), text, isorigin)
        return None

    @threader
    def readcurrent(self, force=False):
        if (not force) and (not globalconfig["autoread"]):
            return
        text1 = self.currentread
        matchitme = self.ttsskip(text1, self.__usewhich(), self.currentread_from_origin)
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
        text2 = self.ttsrepair(text1, self.__usewhich())
        self.audioplayer.timestamp = uuid.uuid4()
        reader.read(text2, force, self.audioplayer.timestamp)

    @tryprint
    def read_text(self, text):
        if not self.reader:
            return
        self.audioplayer.timestamp = uuid.uuid4()
        self.reader.read(text, True, self.audioplayer.timestamp)

    def loadreader(self, use, privateconfig=None, init=True, uid=None):
        aclass = importlib.import_module("tts." + use).TTS
        if uid is None:
            uid = uuid.uuid4()
        obj = aclass(use, self.audioplayer.play, privateconfig, init, uid)
        return obj

    def __reader_usewhich(self):

        for key in globalconfig["reader"]:
            if globalconfig["reader"][key]["use"] and os.path.exists(
                ("LunaTranslator/tts/" + key + ".py")
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

    @tryprint
    def selectprocess(self, selectedp, title):
        pids, pexe, hwnd = selectedp
        if len(NativeUtils.collect_running_pids(pids)) == 0:
            return
        if not title:
            title = windows.GetWindowText(hwnd)

        if not globalconfig["sourcestatus2"]["texthook"]["use"]:
            return
        gameuid, reflist = findgameuidofpath(pexe)
        if gameuid:
            if globalconfig["startgamenototop"] == False:
                idx = reflist.index(gameuid)
                reflist.insert(0, reflist.pop(idx))
        else:
            gameuid = find_or_create_uid(savehook_new_list, pexe, title)
            savehook_new_list.insert(0, gameuid)
        self.textsource.start(hwnd, pids, pexe, gameuid, autostart=False)

    def starttextsource(self, use=None, checked=True):
        self.translation_ui.showhidestate = False
        self.translation_ui.refreshtooliconsignal.emit()

        self.translation_ui.set_color_transparency()
        self.translation_ui.adjustbuttons()
        gobject.base.selecthookbuttonstatus.emit(
            globalconfig["sourcestatus2"]["texthook"]["use"]
        )
        self.textsource = None
        if checked:
            classes = {
                "ocr": ocrtext,
                "copy": copyboard,
                "texthook": texthook,
                "filetrans": filetrans,
                "mssr": mssr,
            }
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
            else:
                self.textsource = classes[use]()

    @threader
    def startmecab(self):
        self.mecab_ = None
        try:
            self.mecab_ = mecab()
        except:
            pass

    @threader
    def startoutputer(self):
        for classname in globalconfig["textoutputer"]:
            if not os.path.exists(
                "LunaTranslator/textio/textoutput/" + classname + ".py"
            ):
                continue
            aclass = importlib.import_module("textio.textoutput." + classname).Outputer
            self.outputers[classname] = aclass(classname)

    def dispatchoutputer(self, text, isorigin):
        for kls in self.outputers.values():
            kls.puttask(text, isorigin)

    def fanyiinitmethod(self, classname):
        try:
            which = translate_exits(classname, which=True)
            if which is None:
                return None
            if which == 0:
                aclass = importlib.import_module("translator." + classname).TS
            elif which == 1:
                aclass = importlib.import_module("userconfig.copyed." + classname).TS
            return aclass(classname)
        except Exception as e:
            self.displayinfomessage(
                _TR(dynamicapiname(classname))
                + " import failed : "
                + str(stringfyerror(e)),
                "<msg_error_Translator>",
            )
            raise e

    @threader
    def prepare(self, now=None, remove=False, _=None):
        self.commonloader("fanyi", self.translators, self.fanyiinitmethod, now, remove)

    def commonloader(
        self, fanyiorcishu, dictobject, initmethod, _type=None, remove=False
    ):
        if _type:
            self.commonloader_warp(fanyiorcishu, dictobject, initmethod, _type)
        else:
            if remove:
                __ = []
                for key in globalconfig[fanyiorcishu]:
                    if translate_exits(key):
                        continue
                    __.append(key)
                for key in __:
                    try:
                        globalconfig[fanyiorcishu].pop(key)
                        translatorsetting.pop(key)
                    except:
                        pass
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
                    # 对于首选的翻译，如果关闭后重新激活，则置顶而非置底
                    # 若手动调整到非指定位置，则保持不变
                    if (
                        fanyiorcishu == "fanyi"
                        and _type == globalconfig["toppest_translator"]
                    ):
                        globalconfig[rankkey].insert(0, _type)
                    else:
                        globalconfig[rankkey].append(_type)
            else:
                if _type in globalconfig[rankkey]:
                    globalconfig[rankkey].remove(_type)
                return
            item = initmethod(_type)
            if item:
                dictobject[_type] = item
        except:
            print_exc()
            if _type in globalconfig[rankkey]:
                globalconfig[rankkey].remove(_type)

    @threader
    def startxiaoxueguan(self, type_=None, _=None):
        self.commonloader("cishu", self.cishus, self.cishuinitmethod, type_)

    def cishuinitmethod(self, type_):

        aclass = importlib.import_module("cishu." + type_)
        aclass = getattr(aclass, type_)
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

    def setdarkandbackdrop(self, widget, dark):
        ismenulist = isinstance(widget, (QMenu, PopupWidget)) or (
            type(widget) == QFrame
        )
        if ((not ismenulist)) and self.__dontshowintaborsetbackdrop(widget):
            return
        if ismenulist:
            name = globalconfig["theme3"]
            NativeUtils.SetCornerNotRound(int(widget.winId()), False, name == "QTWin11")
            if name == "QTWin11":
                NativeUtils.setAcrylicEffect(
                    int(widget.winId()), True, [0x40F7F7FA, 0x40212121][dark]
                )
            else:
                NativeUtils.clearEffect(int(widget.winId()))
        else:
            NativeUtils.SetTheme(
                int(widget.winId()), dark, globalconfig["WindowBackdrop"]
            )

    def checkkeypresssatisfy(self, key, df=False):
        if not globalconfig["wordclickkbtriggerneed"].get(key, df):
            return -1
        keystring = globalconfig["wordclickkbtrigger"].get(key)
        if not keystring:
            return -1
        try:
            modes, vkcode = parsekeystringtomodvkcode(
                keystring, modes=True, canonlymod=True
            )
        except:
            print_exc()
            return -1
        allvk = [mod_map_r[mod] for mod in modes] + ([vkcode] if vkcode else [])
        return all(windows.GetAsyncKeyState(vk) & 0x8000 for vk in allvk)

    def aboutlinkclicked(self, link, parent):

        if link == "WEIXIN":
            return self.createimageviewsig.emit(parent)
        if link == "/":
            link = dynamiclink("/", docs=True)
        os.startfile(link)

    @threader
    def clickwordcallback(self, wordd: dict, append=False):
        if isinstance(wordd, WordSegResult):
            word = wordd
        elif isinstance(wordd, dict):
            word = WordSegResult.from_dict(wordd)
        if word.specialinfo:
            self.aboutlinkclicked(word.specialinfo, self.translation_ui)
            return
        wordwhich = lambda k: (word.word, word.prototype)[
            globalconfig["usewordoriginfor"].get(k, False)
        ]
        sentence = self.currenttext

        def __openlink(word1):
            for link in globalconfig["useopenlinklink1"]:
                os.startfile(
                    link.replace("{word}", word1).replace("{sentence}", sentence)
                )

        funcs = {
            "copyword": lambda word1: NativeUtils.ClipBoard.setText(
                (NativeUtils.ClipBoard.text + word1) if append else word1
            ),
            "searchword": lambda word1: self.searchwordW.search_word.emit(
                word1, sentence, append
            ),
            "openlink": __openlink,
            "searchword_S": lambda word1: threader(gobject.base.hover_search_word.emit)(
                word1, sentence, append, False, False
            ),
        }
        noneedkeys = []
        keytriggered = []
        for k in funcs:
            if not globalconfig["use" + k]:
                continue
            result = self.checkkeypresssatisfy(k)
            if result == -1:
                noneedkeys.append(k)
            elif result:
                keytriggered.append(k)
        for k in keytriggered if keytriggered else noneedkeys:
            funcs[k](wordwhich(k))

    def __dontshowintaborsetbackdrop(self, widget: QWidget):
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
            NativeUtils.SetWindowInTaskbar(
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
        NativeUtils.SetWindowInTaskbar(
            int(widget.winId()), globalconfig["showintab_sub"], False
        )

    def createmenu1(self):
        trayMenu = QMenu(self.commonstylebase)
        showAction = LAction("显示", trayMenu)
        showAction.triggered.connect(self.translation_ui.show_)
        settingAction = LAction(qtawesome.icon("fa.gear"), "设置", trayMenu)
        settingAction.triggered.connect(gobject.base.settin_ui_showsignal)
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
        return trayMenu

    def inittray(self):
        self.tray = QSystemTrayIcon()
        self.tray.setIcon(getExeIcon(getcurrexe()))
        self.tray.setContextMenu(self.createmenu1())
        self.tray.activated.connect(self.leftclicktray)
        self.tray.messageClicked.connect(self.__trayclicked)
        self.trayclicked = print
        self.tray.show()
        version = NativeUtils.QueryVersion(getcurrexe())
        if "load_doc_or_log" not in globalconfig:
            self.showtraymessage(
                _TR("使用说明"),
                "",
                lambda: os.startfile(dynamiclink(docs=True)),
            )
            self.settin_ui.show()
        elif version != tuple(globalconfig["load_doc_or_log"]):
            vs = ".".join(str(_) for _ in version)
            if vs.endswith(".0"):
                vs = vs[:-2]
            self.showtraymessage(
                "v" + vs,
                _TR("更新记录"),
                lambda: os.startfile(dynamiclink("/ChangeLog")),
            )

        globalconfig["load_doc_or_log"] = version

    def __trayclicked(self):
        self.trayclicked()

    def triggertoupdate(self):
        self.istriggertoupdate = True
        NativeUtils.dispatchcloseevent()

    def leftclicktray(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.translation_ui.showhideui()

    def showtraymessage(self, title, message, callback):
        self.trayclicked = callback
        try:
            self.tray.showMessage(title, message, getExeIcon(getcurrexe()))
        except:
            # xp版自定义icon不支持
            self.tray.showMessage(title, message, QSystemTrayIcon.MessageIcon.NoIcon)

    def destroytray(self):
        self.tray.hide()
        self.tray = None

    def setshowintab(self):
        for widget in QApplication.topLevelWidgets():
            self.setshowintab_checked(widget)

    def ismenulistframeless(self, widget: QWidget):
        ismenulist = isinstance(widget, (QMenu, PopupWidget)) or (
            type(widget) == QFrame
        )
        return ismenulist or self.__dontshowintaborsetbackdrop(widget)

    def cornerornot(self, w=None):
        __ = [w] if w else QApplication.topLevelWidgets()
        for widget in __:
            if self.ismenulistframeless(widget):
                continue
            NativeUtils.SetCornerNotRound(
                int(widget.winId()), globalconfig["force_rect"], False
            )

    def setcommonstylesheet(self):

        dark = nowisdark()
        darklight = ["light", "dark"][dark]

        self.currentisdark = dark

        for widget in QApplication.topLevelWidgets():
            self.setdarkandbackdrop(widget, dark)
        style = ""
        for _ in (0,):
            try:
                name = globalconfig["theme3"]
                _fn = None
                for n in static_data["themes"]:
                    if n["name"] == name:
                        _fn = n["file"][darklight]
                        break

                if not _fn:
                    break

                if _fn.endswith(".py"):
                    style = importlib.import_module(
                        "files.LunaTranslator_qss." + _fn[:-3].replace("/", ".")
                    ).stylesheet()
                elif _fn.endswith(".qss"):
                    with open(
                        "files/LunaTranslator_qss/{}".format(_fn),
                        "r",
                    ) as ff:
                        style = ff.read()
            except:
                print_exc()
        fontstr = lambda fsize: "font:{fontsize}pt  {fonttype}; {bold}".format(
            fontsize=fsize,
            fonttype=globalconfig["settingfonttype"],
            bold=("", "font-weight: bold;")[globalconfig["settingfontbold"]],
        )
        style += "*{{  {}  }}".format(fontstr(globalconfig["settingfontsize"]))
        style += "QListWidget {{ {} }}".format(
            fontstr(globalconfig["settingfontsize"] + 2)
        )
        style += "QGroupBox{ background:transparent; } QGroupBox#notitle{ margin-top:0px;} QGroupBox#notitle:title {margin-top: 0px;}"
        self.commonstylebase.setStyleSheet(style)
        font = QFont()
        font.setFamily(globalconfig["settingfonttype"])
        font.setPointSizeF(globalconfig["settingfontsize"])
        font.setBold(globalconfig["settingfontbold"])
        QApplication.instance().setFont(font)

    def get_font_default(self, lang: Languages, issetting: bool) -> str:
        # global font_default_used
        # if lang in font_default_used.keys():
        #     return font_default_used[lang]

        t = "setting_font_type_default" if issetting else "font_type_default"
        l = lang if lang in static_data[t].keys() else "default"

        font_default = ""

        if isinstance(static_data[t][l], list):
            fontlist = static_data[t][l]
        elif isinstance(static_data[t][l], dict):
            fontlist = static_data[t][l].get(("normal", "xp")[sys_le_xp], [])
        else:
            fontlist = []
        is_font_installed = lambda font: QFont(font).exactMatch()
        for font in fontlist:
            if is_font_installed(font):
                font_default = font
                break
        if font_default == "":
            font_default = QFontDatabase.systemFont(
                QFontDatabase.SystemFont.GeneralFont
            ).family()

        # font_default_used["lang"] = font_default
        return font_default

    def set_font_default(self, lang: Languages, fonttype: str) -> None:
        globalconfig[fonttype] = self.get_font_default(
            lang, True if fonttype == "settingfonttype" else False
        )

    def parsedefaultfont(self):
        for k in ["fonttype", "fonttype2", "settingfonttype"]:
            if globalconfig[k] == "":
                l = Languages.Japanese if k == "fonttype" else getlanguse()
                self.set_font_default(l, k)
                # globalconfig[k] = QFontDatabase.systemFont(
                #     QFontDatabase.SystemFont.GeneralFont
                # ).family()

    def loadui(self, startwithgameuid):
        QApplication.instance().installEventFilter(self)
        self.parsedefaultfont()
        self.loadmetadatas()

        self.translation_ui = TranslatorWindow()
        NativeUtils.SetWindowInTaskbar(
            int(self.translation_ui.winId()), globalconfig["showintab"], True
        )
        self.translation_ui.show()
        self.translation_ui.aftershowdosomething()
        self.mainuiloadafter()
        startgame(startwithgameuid)

    def mainuiloadafter(self):
        self.WindowMessageCallback_ptr = NativeUtils.WindowMessageCallback_t(
            self.WindowMessageCallback
        )
        self.WinEventHookCALLBACK_ptr = NativeUtils.WinEventHookCALLBACK_t(
            self.WinEventHookCALLBACK
        )
        NativeUtils.globalmessagelistener(
            self.WinEventHookCALLBACK_ptr, self.WindowMessageCallback_ptr
        )
        self.MonitorPidVolume_callback = NativeUtils.MonitorPidVolume_callback_t(
            self.MonitorPidVolume_callback_f
        )
        NativeUtils.StartMonitorVolume(self.MonitorPidVolume_callback)
        self.safeloadprocessmodels()
        self.prepare(remove=True)
        self.startxiaoxueguan()
        self.startmecab()
        self.startoutputer()

        class commonstylebase(QWidget):
            pass

        self.commonstylebase = commonstylebase(self.translation_ui)
        self.setcommonstylesheet()
        self.settin_ui = Setting(self.commonstylebase)
        self.transhis = transhist(self.commonstylebase)
        self.startreader()
        self.searchwordW = searchwordW(self.commonstylebase)
        self.hookselectdialog = hookselect(self.commonstylebase)
        self.WordViewTooltip = WordViewTooltip(self.commonstylebase)
        self.starttextsource()
        self.inittray()
        self.playtimemanager = playtimemanager()
        self.urlprotocol()
        self.serviceinit()
        versioncheckthread()

    def WinEventHookCALLBACK(self, event, hwnd, idObject):
        try:
            if event == windows.EVENT_SYSTEM_FOREGROUND:
                self.translation_ui.checksettop()
            myhwnd = self.hwnd
            if not myhwnd:
                return
            if (
                event == windows.EVENT_OBJECT_DESTROY
                and idObject == windows.OBJID_WINDOW
            ):
                if hwnd == myhwnd:
                    self.hwnd = None
        except:
            print_exc()

    def MonitorPidVolume_callback_f(self, mute):
        self.translation_ui.processismuteed = mute
        self.translation_ui.refreshtooliconsignal.emit()

    def openlink(self, file: str):
        if file.startswith("http") and checkisusingwine():
            self.translation_ui.displaylink.emit(file)
            return
        return os.startfile(file)

    def WindowMessageCallback(self, msg: int, value1: c_void_p, value2: c_void_p):
        if msg == 0:
            if globalconfig["darklight2"] == 0:
                self.setstylesheetsignal.emit()
        elif msg == 1:
            running = not (value1 == None and value2 == None)
            self.translation_ui.checksettop()
            self.translation_ui.magpiecallback.emit(running)
        elif msg == 2:
            self.translation_ui.closesignal.emit()
        elif msg == 3:
            gobject.base.clipboardcallback.emit(
                bool(value1), cast(value2, c_wchar_p).value
            )
        elif msg == 4:
            self.showtraymessage("Magpie", cast(value2, c_wchar_p).value, lambda: 1)
        elif msg == 5:
            magpie_config.update(json.loads(cast(value2, c_wchar_p).value))

    def _dowhenwndcreate(self, obj):
        if not isinstance(obj, QWidget):
            return
        hwnd = obj.winId()
        if not hwnd:  # window create/destroy,when destroy winId is None
            return
        windows.SetProp(int(obj.winId()), "Magpie.ToolWindow", windows.HANDLE(1))
        if gobject.istest:
            return
        self.cornerornot(obj)
        self.setshowintab_checked(obj)
        NativeUtils.SetWindowExtendFrame(int(hwnd))
        if self.currentisdark is not None:
            self.setdarkandbackdrop(obj, self.currentisdark)

    def eventFilter(self, obj: QObject, event: QEvent):
        if event.type() == QEvent.Type.LanguageChange:
            if "updatelangtext" in dir(obj):
                obj.updatelangtext()
        elif event.type() == QEvent.Type.WinIdChange:
            self._dowhenwndcreate(obj)

        return False

    def loadmetadatas(self):

        for k in globalconfig["metadata"]:
            try:
                targetmod[k] = importlib.import_module("metadata." + k).searcher(k)
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
        command = '"{}" --URLProtocol "%1"'.format(getcurrexe())
        winreg.SetValue(keysub, r"", winreg.REG_SZ, command)
