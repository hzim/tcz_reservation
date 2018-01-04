"""tcz URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
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
from django.contrib.auth import views as auth_views
from courts import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'tczusers', views.UserViewSet)
router.register(r'tczhours', views.TczHourViewSet)

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/(?P<day>[0-9]{2})/', views.courts, name='courts'),
    url(r'^auth_login/$', auth_views.login, {'template_name': 'courts/login.html'}, name='auth_login'),
    url(r'^auth_logout/$', auth_views.logout, {'next_page': '/'}, name='auth_logout'),
    url(r'^admin/', admin.site.urls, name='admin'),
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
