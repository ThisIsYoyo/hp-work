from django.urls import path, re_path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    re_path(r'^(?P<file_path>.+)/$', views.FileView.as_view()),
]