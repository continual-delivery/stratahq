from django.conf.urls import url

from . import views

app_name = 'strata'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
]