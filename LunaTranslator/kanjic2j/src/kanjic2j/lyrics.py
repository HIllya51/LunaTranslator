#!python
# -*- coding: utf-8 -*-
# filename: kanjic2j/lyrics.py
# special for lyrics

from .bases import *


class Lyrics(Kjfile):
    __kanas = [
        u"ん", u"ン",
        u"わ", u"ワ", u"ら", u"ラ", u"や", u"ヤ", u"ま", u"マ", u"は", u"ハ",
        u"な", u"ナ", u"た", u"タ", u"さ", u"サ", u"か", u"カ", u"あ", u"ア",
        u"ゐ", u"ヰ", u"り", u"リ", u"み", u"ミ", u"ひ", u"ヒ", u"に", u"ニ",
        u"ち", u"チ", u"し", u"シ", u"き", u"キ", u"い", u"イ",
        u"る", u"ル", u"ゆ", u"ユ", u"む", u"ム", u"ふ", u"フ", u"ぬ", u"ヌ",
        u"つ", u"ツ", u"す", u"ス", u"く", u"ク", u"う", u"ウ",
        u"ゑ", u"ヱ", u"れ", u"レ", u"め", u"メ", u"へ", u"ヘ", u"ね", u"ネ",
        u"て", u"テ", u"せ", u"セ", u"け", u"ケ", u"え", u"エ",
        u"を", u"ヲ", u"ろ", u"ロ", u"よ", u"ヨ", u"も", u"モ", u"ほ", u"ホ",
        u"の", u"ノ", u"と", u"ト", u"そ", u"ソ", u"こ", u"コ", u"お", u"オ",
        u"が", u"ぎ", u"ぐ", u"げ", u"ご", u"ざ", u"じ", u"ず", u"ぜ", u"ぞ",
        u"だ", u"ぢ", u"づ", u"で", u"ど", u"ば", u"び", u"ぶ", u"べ", u"ぼ",
        u"ぱ", u"ぴ", u"ぷ", u"ぺ", u"ぽ", u"ヴ", u"ぁ", u"ぃ", u"ぅ", u"ぇ",
        u"ぉ", u"ゃ", u"ゅ", u"ょ", u"っ", u"ガ", u"ギ", u"グ", u"ゲ", u"ゴ",
        u"ザ", u"ジ", u"ズ", u"ゼ", u"ゾ", u"ダ", u"ヂ", u"ヅ", u"デ", u"ド",
        u"バ", u"ビ", u"ブ", u"ベ", u"ボ", u"パ", u"ピ", u"プ", u"ぺ", u"ポ",
        u"ゔ", u"ァ", u"ィ", u"ゥ", u"ェ", u"ォ", u"ャ", u"ュ", u"ョ", u"ッ"
    ]
    __splitch = [
        '\n', '/', '.', '(', ')', '\t', ' ',
        u'。', u'（', u'）', u'【', u'】',
        '[', ']',
    ]
    __special = [
        u'凋叶棕',
    ]

    def __init__(self, ain):
        Kjfile.__init__(self, ain)
        self.__split()

    def __prepare(self):
        self.data = self.data.replace(self.linebreak, '\n')
        if self.data[len(self.data) - 1] != '\n':
            self.data += '\n'

    def __findnext(self, now):
        t1 = oo
        t2 = None
        for ea in Lyrics.__splitch:
            xp = self.data.find(ea, now)
            if (xp > 0)and(xp < t1):
                t1 = xp
                t2 = ea
        for ea in Lyrics.__special:
            xp = self.data.find(ea, now)
            if (xp > 0)and(xp < t1):
                t1 = xp
                t2 = ea
        return t1, t2

    @staticmethod
    def __test(tmpstr):
        if len(tmpstr) < 3:
            return True
        for ea in Lyrics.__kanas:
            if tmpstr.find(ea) >= 0:
                return True
        return False

    def __split(self):
        self.__prepare()
        self.__tmpstr = []
        self.__sps = ['']
        self.__flags = []
        u = 0
        while True:
            v, sp = self.__findnext(u)
            if sp is None:
                break
            self.__tmpstr.append(self.data[u:v])
            self.__sps.append(sp)
            self.__flags.append(Lyrics.__test(self.__tmpstr[-1]))
            u = v + len(sp)

    def worksent(self, mstr):
        xtmp = []
        for l in xrange(0, len(mstr)):
            qtmp = Lyrics.workdanji(mstr[l])
            xtmp.append(qtmp[0])
        return u''.join(xtmp)

    def work(self):
        ptmp = []
        for i in xrange(0, len(self.__tmpstr)):
            ptmp.append(self.__sps[i])
            if self.__flags[i]:
                p1 = self.worksent(self.__tmpstr[i])
                ptmp[i] += p1
            else:
                ptmp[i] += self.__tmpstr[i]
        ptmp.append(self.__sps[-1])
        return Kjfile(u''.join(ptmp))

