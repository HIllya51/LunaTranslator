import kanjic2j as kj
def work(muni):
	mylyric = kj.Lyrics(muni)
	return mylyric.work().data
