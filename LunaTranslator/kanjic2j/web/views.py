from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from kanjic2j_web.models import Log
import kanjic2j as kj
import datetime

def index(request):
    context = {}
    return render(request, "kanji/index.html", context)

def work(request):
    if request.method == 'POST':
        if not request.POST.has_key('data'):
            raise Http404
        result = __work_core(request.POST['data'])
        if len(result) >= 15:
            mxp = Log(use_time=datetime.datetime.now(),filename=result[:15],
                address=request.META.get('HTTP_X_FORWARDED_FOR', request.META['REMOTE_ADDR'])
            )
            mxp.save()
        return HttpResponse(u''.join(result))
    else:
        raise Http404

def __work_core(data):
    mylyc = kj.WebLyrics(data).work()
    return mylyc.data

