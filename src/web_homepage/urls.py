from django.urls import path
from django.contrib import admin

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('open/<uuid:id>/', views.open, name='open'),
    path('open-group/<uuid:id>/', views.open_group, name='open_group'),
    path('admin/', admin.site.urls),
]
