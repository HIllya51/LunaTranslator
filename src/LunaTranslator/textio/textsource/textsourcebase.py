import gobject, queue
import json, time, re
from traceback import print_exc
from myutils.config import globalconfig, savehook_new_data
from myutils.utils import autosql
from myutils.wrapper import threader
from myutils.mecab import punctuations
from sometypes import TranslateResult


def count_words_mixed(text: str) -> int:
    if not text:
        return 0

    # 1. 将标点符号列表转义并构建成正则表达式的 split 模式
    # re.escape 会自动处理像 . * ? 这样的正则特殊字符
    punc_pattern = "|".join([re.escape(p) for p in punctuations])

    # 2. 先根据标点符号将句子拆分成片段
    # 如果 punc_pattern 为空，则不拆分

    total_count = 0

    # 匹配中日韩 (CJK) 字符的正则
    cjk_regex = re.compile(r"[\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af]")

    for seg in re.split(punc_pattern, text):
        seg = seg.strip()
        if not seg:
            continue

        # --- 处理中日韩字符 ---
        # 统计所有中日韩字符的数量（每个字计为 1）
        cjk_chars = cjk_regex.findall(seg)
        total_count += len(cjk_chars)

        # --- 处理西文单词 (英语、法语等) ---
        # 我们把已经统计过的 CJK 字符替换为空格，防止干扰西文单词提取
        # 这样剩下的就是拉丁字母、数字和空格
        remain_text = cjk_regex.sub(" ", seg)

        # 根据空格切分剩下的文本
        # .split() 不传参数时会处理连续空格、换行符等
        latin_words = remain_text.split()

        # 累计西文单词数
        total_count += len(latin_words)

    return total_count


class basetext:

    def gettextonce(self):
        return None

    def init(self): ...
    def end(self): ...
    def runornot(self, b): ...
    def __init__(self):
        #

        self.textgetmethod = gobject.base.textgetmethod

        self.ending = False
        self.sqlqueue = None
        self.init()

    def startsql(self, sqlfname_all):
        self.sqlqueueput(None)
        self.sqlqueue = queue.Queue()
        try:

            # self.sqlwrite=sqlite3.connect(self.sqlfname,check_same_thread = False, isolation_level=None)
            self.sqlwrite2 = autosql(
                sqlfname_all, check_same_thread=False, isolation_level=None
            )
            # try:
            #     self.sqlwrite.execute('CREATE TABLE artificialtrans(id INTEGER PRIMARY KEY AUTOINCREMENT,source TEXT,machineTrans TEXT,userTrans TEXT);')
            # except:
            #     pass
            try:
                self.sqlwrite2.execute(
                    "CREATE TABLE artificialtrans(id INTEGER PRIMARY KEY AUTOINCREMENT,source TEXT,machineTrans TEXT,origin TEXT);"
                )
            except:
                pass
        except:
            print_exc()
        threader(self.sqlitethread)()

    def updaterawtext(self, text):
        if self.ending:
            return
        gobject.base.updaterawtext(text)

    def dispatchtext(self, *arg, **kwarg):
        if self.ending or not self.isautorunning:
            return
        self.textgetmethod(*arg, **kwarg)

    def waitfortranslation(self, text):
        resultwaitor = queue.Queue()
        self.textgetmethod(
            text,
            is_auto_run=True,
            waitforresultcallback=resultwaitor.put,
            waitforresultcallbackengine=globalconfig["toppest_translator"],
        )
        tsres: TranslateResult = resultwaitor.get()
        return tsres.result

    @property
    def isautorunning(self):
        return globalconfig["autorun"]

    ##################
    def endX(self):
        self.ending = True
        self.sqlqueueput(None)
        self.end()

    def sqlqueueput(self, xx):
        try:
            self.sqlqueue.put(xx)
        except:
            pass

    def sqlitethread(self):
        while not self.ending:
            task = self.sqlqueue.get()
            if not task:
                break
            try:
                if len(task) == 2:
                    src, origin = task
                    lensrc = count_words_mixed(src)
                    ret = self.sqlwrite2.execute(
                        "SELECT * FROM artificialtrans WHERE source = ?", (src,)
                    ).fetchone()
                    try:
                        if (
                            "statistic_wordcount"
                            not in savehook_new_data[gobject.base.gameuid]
                        ):
                            savehook_new_data[gobject.base.gameuid][
                                "statistic_wordcount"
                            ] = 0
                        savehook_new_data[gobject.base.gameuid][
                            "statistic_wordcount"
                        ] += lensrc

                        gobject.base.somedatabase.wordcountqueue.put(
                            (time.time(), gobject.base.gameuid, lensrc)
                        )
                    except:
                        pass
                    if ret is None:
                        try:
                            self.sqlwrite2.execute(
                                "INSERT INTO artificialtrans VALUES(NULL,?,?,?);",
                                (src, json.dumps({}), origin),
                            )
                        except:
                            self.sqlwrite2.execute(
                                "INSERT INTO artificialtrans VALUES(NULL,?,?);",
                                (src, json.dumps({})),
                            )
                elif len(task) == 3:
                    src, clsname, trans = task
                    ret = self.sqlwrite2.execute(
                        "SELECT machineTrans FROM artificialtrans WHERE source = ?",
                        (src,),
                    ).fetchone()
                    if not ret:
                        return
                    ret = json.loads((ret[0]))
                    ret[clsname] = trans
                    ret = json.dumps(ret, ensure_ascii=False)
                    self.sqlwrite2.execute(
                        "UPDATE artificialtrans SET machineTrans = ? WHERE source = ?",
                        (ret, src),
                    )
            except:
                print_exc()
