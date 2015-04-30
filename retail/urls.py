from django.conf.urls import patterns, url
from retail import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index')
)