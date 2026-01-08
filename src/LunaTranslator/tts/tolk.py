# https://github.com/HIllya51/LunaTranslator/pull/2086
import os, NativeUtils
from ctypes import CDLL, c_wchar_p, c_bool
from tts.basettsclass import TTSbase, SpeechParam

Tolk_PATH = None


def __istolkdll(file):
    if not NativeUtils.IsDLLBitSameAsMe(file):
        return False
    return "Tolk_Load" in NativeUtils.AnalysisDllExports(file)


Tolk_PATH = NativeUtils.SearchDllPath("Tolk.dll")
if Tolk_PATH and not __istolkdll(Tolk_PATH):
    Tolk_PATH = None
if not Tolk_PATH:
    for _dir, _, __ in os.walk("."):
        __ = os.path.join(_dir, "Tolk.dll")
        if os.path.isfile(__):
            if __istolkdll(__):
                Tolk_PATH = os.path.abspath(__)
                break


def useExfunction():
    global Tolk_PATH

    return Tolk_PATH is not None


class TTS(TTSbase):
    # Tolk不支持音高和语速调节
    arg_support_pitch = False
    arg_support_speed = False

    def _load_tolk(self):
        global Tolk_PATH
        """加载并初始化Tolk库"""
        if hasattr(self, "_tolk_loaded") and self._tolk_loaded:
            return

        if not Tolk_PATH:
            raise Exception("Tolk.dll not found")

        # 添加DLL目录到搜索路径，以便Tolk能找到读屏软件的DLL
        # (如nvdaControllerClient64.dll, SAAPI64.dll等)
        self._dll_handle = None
        dll_dir = os.path.dirname(Tolk_PATH)
        self._dll_handle = os.add_dll_directory(dll_dir)
        try:
            # Python 3.8+ 支持 os.add_dll_directory
            self._dll_handle = os.add_dll_directory(dll_dir)
        except AttributeError:
            # 旧版本Python，使用SetDllDirectory
            import ctypes

            ctypes.windll.kernel32.SetDllDirectoryW(dll_dir)

        self.tolk = CDLL(Tolk_PATH)
        self._setup_functions()

        # 根据配置设置SAPI选项（必须在Tolk_Load之前调用）
        try_sapi = self.config.get("trySAPI", True)
        prefer_sapi = self.config.get("preferSAPI", False)

        if try_sapi:
            self.tolk.Tolk_TrySAPI(True)
        if prefer_sapi:
            self.tolk.Tolk_PreferSAPI(True)

        # 初始化Tolk
        self.tolk.Tolk_Load()
        self._tolk_loaded = True

    def _setup_functions(self):
        """设置DLL函数签名"""
        # void Tolk_Load()
        self.tolk.Tolk_Load.argtypes = []
        self.tolk.Tolk_Load.restype = None

        # void Tolk_Unload()
        self.tolk.Tolk_Unload.argtypes = []
        self.tolk.Tolk_Unload.restype = None

        # bool Tolk_IsLoaded()
        self.tolk.Tolk_IsLoaded.argtypes = []
        self.tolk.Tolk_IsLoaded.restype = c_bool

        # void Tolk_TrySAPI(bool trySAPI)
        self.tolk.Tolk_TrySAPI.argtypes = [c_bool]
        self.tolk.Tolk_TrySAPI.restype = None

        # void Tolk_PreferSAPI(bool preferSAPI)
        self.tolk.Tolk_PreferSAPI.argtypes = [c_bool]
        self.tolk.Tolk_PreferSAPI.restype = None

        # const wchar_t* Tolk_DetectScreenReader()
        self.tolk.Tolk_DetectScreenReader.argtypes = []
        self.tolk.Tolk_DetectScreenReader.restype = c_wchar_p

        # bool Tolk_HasSpeech()
        self.tolk.Tolk_HasSpeech.argtypes = []
        self.tolk.Tolk_HasSpeech.restype = c_bool

        # bool Tolk_HasBraille()
        self.tolk.Tolk_HasBraille.argtypes = []
        self.tolk.Tolk_HasBraille.restype = c_bool

        # bool Tolk_Output(const wchar_t* str, bool interrupt)
        self.tolk.Tolk_Output.argtypes = [c_wchar_p, c_bool]
        self.tolk.Tolk_Output.restype = c_bool

        # bool Tolk_Speak(const wchar_t* str, bool interrupt)
        self.tolk.Tolk_Speak.argtypes = [c_wchar_p, c_bool]
        self.tolk.Tolk_Speak.restype = c_bool

        # bool Tolk_Silence()
        self.tolk.Tolk_Silence.argtypes = []
        self.tolk.Tolk_Silence.restype = c_bool

    def getvoicelist(self):
        """返回声音列表（读屏软件名称）"""
        # 先加载Tolk
        self._load_tolk()

        # 检测当前活动的读屏软件
        screen_reader = self.tolk.Tolk_DetectScreenReader()

        if screen_reader:
            return [screen_reader], [screen_reader]
        else:
            # 没有检测到读屏软件
            return ["none"], ["无读屏软件"]

    def read(self, content, force=False, timestamp=None):
        """重写read方法，直接调用Tolk输出（不播放音频）"""
        if not content or len(content) == 0:
            return

        # 确保Tolk已加载
        self._load_tolk()

        # 检查Tolk是否已加载
        if not self.tolk.Tolk_IsLoaded():
            # 重新加载
            self.tolk.Tolk_Load()

        # 直接通过Tolk输出到读屏软件
        # force=True时中断之前的朗读
        self.tolk.Tolk_Output(content, force)

    def speak(self, content, voice, param: SpeechParam):
        """speak方法不返回音频数据"""
        # Tolk直接输出到读屏软件，不返回音频
        return None

    def silence(self):
        """停止当前朗读"""
        if hasattr(self, "tolk") and self.tolk:
            self.tolk.Tolk_Silence()

    def __del__(self):
        """清理资源"""
        try:
            if hasattr(self, "_tolk_loaded") and self._tolk_loaded:
                if hasattr(self, "tolk") and self.tolk:
                    self.tolk.Tolk_Unload()
                    self._tolk_loaded = False
            # 清理DLL目录句柄
            if hasattr(self, "_dll_handle") and self._dll_handle:
                self._dll_handle.close()
        except:
            pass
