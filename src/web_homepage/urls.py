from django.urls import path
from django.contrib import admin

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('open/<uuid:door_id>/', views.open, name='open'),
    path('admin/', admin.site.urls),
]
