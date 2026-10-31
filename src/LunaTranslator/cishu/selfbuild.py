from myutils.utils import checkmd5reloadmodule
import gobject, inspect, os
from cishu.cishubase import cishubase


class Cishu(cishubase):
    def __init__(self, *a):
        self.internal = None
        self.__lastm = None
        super().__init__(*a)

    def __getuserfile(self):
        # 隐藏 arg（selfbuild_file，不在 args 里、无 UI）：实例要加载的
        # 用户文件（复制实例各用各的）；未设置时加载默认文件
        fname = self.gconfig.get("selfbuild_file") or "selfbuild_cishu.py"
        return fname, gobject.getconfig(fname)

    def mayreinit(self):
        fname, fpath = self.__getuserfile()
        # 模块缓存名跟文件走：不同实例的文件互不干扰
        module = checkmd5reloadmodule(fpath, os.path.splitext(fname)[0])
        if module and (module.MyCishu != self.__lastm):
            self.__lastm = module.MyCishu
            # 用自身 typename（而非硬编码 "selfbuild"）：每个实例读
            # 各自的配置
            self.internal: cishubase = module.MyCishu(self.typename)
            self.internal.init()

    def search(self, word, sentence=None) -> str:
        self.mayreinit()
        if not self.internal:
            return None
        sig = inspect.signature(self.internal.search)
        np = len(sig.parameters)
        if np == 1:
            return self.internal.search(word)
        elif np == 2:
            return self.internal.search(word, sentence=sentence)
        else:
            raise Exception("unknown args")

    def getUrl(self, word) -> str:
        self.mayreinit()
        if not self.internal:
            return None
        return self.internal.getUrl(word)
