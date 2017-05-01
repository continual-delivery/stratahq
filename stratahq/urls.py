"""stratahq URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.shortcuts import redirect
from django.conf import settings
from django.contrib.auth import views as auth_views

admin.site.site_header = settings.ADMIN_SITE_HEADER

urlpatterns = [
    url(r'^login/$', auth_views.login, {'template_name': 'login.html'},  name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/login'}, name='logout'),
    # Admin site
    url(r'^admin/', admin.site.urls),
    # Redirect root to /admin
    url(r'^$', lambda _: redirect('home:index'), name='index'),
    # The home app
    url(r'^home/', include('home.urls')),
    # The assets app
    url(r'^assets/', include('strata.urls')),
    # The Strata app
    url(r'^strata/', include('strata.urls')),
]
