"""robolike URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
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
from django.conf.urls import url
from django.contrib import admin
from django.conf.urls import include
from django.views.generic.edit import CreateView
from . forms import UserCreateForm
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    url('^', include('django.contrib.auth.urls')),

    url('^login$', auth_views.login, name='login'),

    url(r'^register/$', views.register, name='register'),
    # url(r'^logout$', 'django.contrib.auth.views.logout',name="logout"),
    # url('^register/', CreateView.as_view(
    #     template_name='socialtune/register.html',
    #     form_class=UserCreateForm,
    #     success_url='/'
    # )),
    url(r'^run$', views.run, name='run'),
    url(r'^settings$', views.settings, name='settings'),
    url(r'^profile$', views.profile, name='profile'),
    url(r'^history$', views.history, name='history'),
    url(r'^ipn(?P<uid>[0-9]+)$', views.ipn, name='ipn'),
    url(r'^$', views.index, name='index'),
    url(r'^set|del|setc|delc$', views.set, name='set'),
    url(r'^admin/', admin.site.urls),
]
