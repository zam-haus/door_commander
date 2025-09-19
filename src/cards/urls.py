from django.urls import path
from django.contrib import admin

from . import views

urlpatterns = [
    path('', views.home, name='cards-home'),
    path('modify/<uuid:card_id>/', views.modify, name='cards-modify'),
    path('disable/', views.disable_scan, name='cards-disable-scan'),
    path('register/', views.register, name='cards-register'),
]
