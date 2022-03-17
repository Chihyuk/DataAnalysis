from django.urls import path

from . import views

urlpatterns = [
    path('', views.index),
    path("download/", views.downloadFile, name="downloadFile"),
    path("plot/", views.demo_plot_view)
] 