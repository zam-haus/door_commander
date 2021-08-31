"""door_commander URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include

from django.contrib.auth.views import auth_login, LoginView

urlpatterns = [
    path('', include('web_homepage.urls')),
    # path('admin/', admin.site.urls),
    url(
        r'^accounts/login/$',
        LoginView.as_view(
            template_name='admin/login.html',
            extra_context={
                'title': 'Login',
                'site_title': 'ZAM Door',
                'site_header': 'ZAM Door Commander Login'}),
        name='login'),

    path('accounts/', include('django.contrib.auth.urls')),
]

if settings.OIDC:
    urlpatterns += [
        path('oidc/', include('mozilla_django_oidc.urls')),
    ]
