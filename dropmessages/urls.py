# mysite/urls.py
from django.conf.urls import include
from django.urls import path
from django.contrib import admin

from drop.views import no_resource, web_portal, web_register

urlpatterns = [
    path('', no_resource, name='no_resource'),
    path('web/portal/', web_portal, name='portal'),
    path('web/register/', web_register, name='register'),
    path('web/', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls)
]