#!python
# -*- coding: utf-8 -*-
# filename : init.py
# initialization for kanjic2j

def init():
	import cPickle as cp
	print 'input'
	fin=file('kanjic2j/kanjic2j_xjc.dat')
	xjc=cp.load(fin)
	fin.close()
	xcj={}
	for ja,ch in xjc.items():
		if xcj.has_key(ch):
			xcj[ch].append(ja)
		else:
			xcj[ch]=[ja]
	print 'output'
	fout=file('kanjic2j/kanjic2j_xcj.dat','wb')
	cp.dump(xcj,fout)
	fout.close()
	print 'Done.'

def edit():
	import cPickle as cp
	fin=file('kanjic2j/kanjic2j_xcj.dat')
	xcj=cp.load(fin)
	fin.close()
	for e1,e2 in xcj.items():
		if len(e2)>1 and e2[0]==e1:
			tt=e2[1]
			e2[1]=e2[0]
			e2[0]=tt
			print e1,' ',e2[0],' ',e2[1]
	fout=file('kanjic2j/kanjic2j_xcj.dat','wb')
	cp.dump(xcj,fout)
	fout.close()
	print 'Done!'
def edit2():
	import cPickle as cp
	fin=file('kanjic2j/kanjic2j_xcj.dat','rb')
	xcj=cp.load(fin)
	fin.close()
	xcj[u'谁']=[u'誰']
	fout=file('kanjic2j/kanjic2j_xcj.dat','wb')
	cp.dump(xcj,fout)
	fout.close()
	fin=file('kanjic2j/kanjic2j_xjc.dat','rb')
	xjc=cp.load(fin)
	fin.close()
	xjc[u'誰']=u'谁'
	fout=file('kanjic2j/kanjic2j_xjc.dat','wb')
	cp.dump(xjc,fout)
	fout.close()
	print 'Done!'
if __name__=='__main__':
	#init()
	edit()
	#edit2()

