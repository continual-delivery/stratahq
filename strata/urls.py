from django.conf.urls import url
from django.shortcuts import redirect

from . import views

app_name = 'strata'
urlpatterns = [
    url(r'^$', lambda _: redirect('home:index'), name='index'),
    url(r'^servers/app/$', views.StrataAppServersView.as_view(), name='app_servers' ),
    url(r'^servers/assentis/$', views.StrataAssentisServersView.as_view(), name='assentis_servers' ),
    url(r'^servers/orb/$', views.StrataORBServersView.as_view(), name='orb_servers' ),
]
