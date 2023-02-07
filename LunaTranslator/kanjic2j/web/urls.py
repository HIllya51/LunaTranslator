from django.conf.urls import patterns, url

from kanjic2j_web import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
	url(r'^work/$', views.work, name='work'),
)
