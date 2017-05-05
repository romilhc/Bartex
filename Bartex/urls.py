"""Bartex URL Configuration

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
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from BarterSystem.views import *

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', index),
    url(r'^signin/', signin),
    url(r'^signup/', signup),
    url(r'^home/',home),
<<<<<<< HEAD
    url(r'^postin/',postin),
    url(r'^ref/',ref),
    #url(r'^swapost/',swapost),
=======
    url(r'^ref/',ref),
>>>>>>> 025c2bb1b678b0c72f2663873c9a3849e8f9b52f
    url(r'^profile/',profile),
    url(r'^contactus/',contact),
    url(r'^about/',about),
    url(r'^post/',post)
]  +static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
