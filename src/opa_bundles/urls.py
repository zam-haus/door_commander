from django.urls import path
from django.contrib import admin

from . import views

urlpatterns = [
    path('bundles/<str:filename>', views.get_bundle, name='get_bundle'),
    path('decision-log/<str:hostname>', views.post_decision_log, name='post_decision_log'),
    path('status/<str:hostname>', views.post_status, name='post_status'),
    #path('admin/', admin.site.urls),
]
