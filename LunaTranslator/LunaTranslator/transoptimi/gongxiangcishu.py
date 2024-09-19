from myutils.config import globalconfig
from myutils.utils import case_insensitive_replace
import xml.etree.ElementTree as ET
import os, gobject, re
from gui.inputdialog import getsomepath1


def vnrshareddict(self):

    self.vnrshareddict = {}
    self.vnrshareddict_pre = {}
    self.vnrshareddict_post = {}
    self.sorted_vnrshareddict = []
    self.sorted_vnrshareddict_pre = []
    self.sorted_vnrshareddict_post = []
    self.vnrsharedreg = []

    if globalconfig["gongxiangcishu"]["use"] and os.path.exists(
        globalconfig["gongxiangcishu"]["path"]
    ):
        xml = ET.parse(globalconfig["gongxiangcishu"]["path"])

        for _ in xml.find("terms").findall("term"):
            # print(_.get('type'))
            # macro 宏(正则) 忽略
            # yomi 人名读音 可忽略
            # input 直接替换
            # trans 翻译优化
            # output 输出替换
            # tts 忽略
            # game #游戏名 忽略
            # name #人名 忽略
            # suffix #后缀（们）等 忽略
            # prefix #前缀 忽略
            _type = _.get("type")
            try:
                src = _.find("sourceLanguage").text
                tgt = _.find("language").text
                if tgt == "en":
                    continue
                pattern = _.find("pattern").text
                try:
                    text = _.find("text").text
                except:
                    text = ""

                try:
                    regex = _.find("regex").text

                except:

                    if "eos" in text or "amp" in text or "&" in text:

                        continue
                    if _type == "trans":
                        self.vnrshareddict[pattern] = {
                            "src": src,
                            "tgt": tgt,
                            "text": text,
                        }
                    elif _type == "input":
                        self.vnrshareddict_pre[pattern] = {
                            "src": src,
                            "tgt": tgt,
                            "text": text,
                        }
                    elif _type == "output":
                        self.vnrshareddict_post[pattern] = {
                            "src": src,
                            "tgt": tgt,
                            "text": text,
                        }
            except:
                pass

        keys = list(self.vnrshareddict.keys())
        keys.sort(key=lambda key: len(key), reverse=True)
        self.sorted_vnrshareddict = [(key, self.vnrshareddict[key]) for key in keys]
        keys = list(self.vnrshareddict_pre.keys())
        keys.sort(key=lambda key: len(key), reverse=True)
        self.sorted_vnrshareddict_pre = [
            (key, self.vnrshareddict_pre[key]) for key in keys
        ]
        keys = list(self.vnrshareddict_post.keys())
        keys.sort(key=lambda key: len(key), reverse=True)
        self.sorted_vnrshareddict_post = [
            (key, self.vnrshareddict_post[key]) for key in keys
        ]


class Process:

    def __init__(self) -> None:
        self.status = None
        self.checkchange()

    def checkchange(self):
        s = (
            globalconfig["gongxiangcishu"]["use"],
            globalconfig["gongxiangcishu"]["path"],
        )
        if self.status != s:
            self.status = s
            vnrshareddict(self)

    def process_before(self, content):
        ___idx = 1
        self.checkchange()
        context = {}

        for key, value in self.sorted_vnrshareddict_pre:

            if key in content:
                content = content.replace(key, value["text"])
        for key, value in self.sorted_vnrshareddict:

            if key in content:
                # print(key)
                # if self.vnrshareddict[key]['src']==self.vnrshareddict[key]['tgt']:
                #     content=content.replace(key,self.vnrshareddict[key]['text'])
                # else:
                if ___idx == 1:
                    xx = "ZX{}Z".format(chr(ord("B") + gobject.baseobject.zhanweifu))
                elif ___idx == 2:
                    xx = "{{{}}}".format(gobject.baseobject.zhanweifu)
                elif ___idx == 3:
                    xx = key
                content = content.replace(key, xx)
                context[xx] = key
                gobject.baseobject.zhanweifu += 1
        return content, context

    def process_after(self, res: str, context):

        for key in context:
            res = case_insensitive_replace(
                res, key, self.vnrshareddict[context[key]]["text"]
            )
        for key, value in self.sorted_vnrshareddict_post:
            if key in res:
                res = res.replace(key, value["text"])
        return res

    @staticmethod
    def get_setting_window(parent_window):
        return getsomepath1(
            parent_window,
            "共享辞书",
            globalconfig["gongxiangcishu"],
            "path",
            "共享辞书",
            None,
            False,
            "*.xml",
        )
