from django.urls import path

from . import views

urlpatterns = [
    path('', views.index),
    path("download/", views.downloadFile, name="downloadFile"),
    path("train_data_download/", views.downloadTrainDataFile, name="downloadFile"),
    path("train_target_download/", views.downloadTrainTargetFile, name="downloadFile"),
    path("test_data_download/", views.downloadTestDataFile, name="downloadFile"),
    path("test_target_download/", views.downloadTestTargetFile, name="downloadFile"),
    path("plot/", views.demo_plot_view),
] 