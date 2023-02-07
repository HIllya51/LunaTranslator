#!python
# -*- coding: utf-8 -*-
# filename: kanjic2j/web_lyrics.py
# special for web lyrics

from .lyrics import *


class WebLyrics(Lyrics):
    __hightlight = "<span class='hred'>%s</span>"

    def __init__(self, ain, hightlight=None):
        Lyrics.__init__(self, ain)
        self.hightlight = hightlight if hightlight is not None else WebLyrics.__hightlight

    def work(self):
        tre = Lyrics.work(self)
        return Kjfile(tre.data.replace(tre.linebreak, "<br>"))

    def worksent(self, mstr):
        xtmp = []
        for l in xrange(0, len(mstr)):
            qtmp = Lyrics.workdanji(mstr[l])
            if len(qtmp) > 1:
                xtmp.append(self.hightlight % qtmp[0])
            else:
                xtmp.append(qtmp[0])
        return u''.join(xtmp)

