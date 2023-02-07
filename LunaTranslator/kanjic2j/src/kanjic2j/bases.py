#!python
# filename : kanjic2j/core.py
# core of kanjic2j

import codecs
import sys
import os

xcj = xjc = {}
oo = 20070128


def init():
    global xcj, xjc
    print 'Initializing..'
    import cPickle as cp
    print 'Loading xcj..',
    f1 = file(os.path.join(os.path.dirname(__file__), 'kanjic2j_xcj.dat'))
    xcj = cp.load(f1)
    f1.close()
    print 'Done!'
    print 'Loading xjc..',
    f1 = file(os.path.join(os.path.dirname(__file__), 'kanjic2j_xjc.dat'))
    xjc = cp.load(f1)
    f1.close()
    print 'Done!'
try:
    init()
except:
    print 'Error!'


class Kjfile:
    global xcj
    mxcj = xcj

    def __init__(self, ain):
        if (isinstance(ain, str))or(isinstance(ain, file)):
            self.open_file(ain)
        elif isinstance(ain, unicode):
            self.data = ain
        else:
            self.data = unicode('unknown input', 'utf-8')
        if self.data.find('\r\n') >= 0:
            self.linebreak = '\r\n'
        elif self.data.find('\r') >= 0:
            self.linebreak = '\r'
        else:
            self.linebreak = '\n'

    def open_file(self, ain):
        if isinstance(ain, str):
            try:
                ain = codecs.open(ain, 'r', 'utf-8')
                self.data = ain.read()
            except:
                ain = file(ain)
                self.data = unicode(ain.read(), 'utf-8')
            finally:
                ain.close()
        else:
            self.data = unicode(ain.read(), 'utf-8')

    def save_file(self, aout, linebreak=None):
        if linebreak is None:
            linebreak = self.linebreak
        if type(aout) == str:
            aout = codecs.open(aout, 'w', 'utf-8')
            aout.write(self.data.replace(self.linebreak, linebreak))
            aout.close()

    @staticmethod
    def workdanji(ach):
        if Kjfile.mxcj.has_key(ach):
            return Kjfile.mxcj[ach]
        else:
            return (ach,)

    def work(self):
        '''
        need to be override
        '''
        re = []
        for i in xrange(0, len(self.data)):
            tmp = Kjfile.workdanji(self.data[i])
            re.append(tmp[0])
        return Kjfile(u''.join(re))


def open_file(afile):
    return Kjfile(afile)

