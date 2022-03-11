from django.urls import path

from . import views

urlpatterns = [
    path('', views.index),
    path('pie/', views.pie),
    path('amchart/', views.amchart),
    # path('copy/', views.index_copy),
]