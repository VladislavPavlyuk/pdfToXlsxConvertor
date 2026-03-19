from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("upload/", views.upload_files, name="upload_files"),
    path("convert/", views.convert_files, name="convert_files"),
    path("convert/selected/", views.convert_selected_uploads, name="convert_selected_uploads"),
    path("uploads/", views.list_uploads, name="list_uploads"),
    path("uploads/delete/", views.delete_uploads, name="delete_uploads"),
    path("outputs/", views.list_outputs, name="list_outputs"),
    path("outputs/delete/", views.delete_outputs, name="delete_outputs"),
    path("outputs/copy/", views.copy_outputs, name="copy_outputs"),
    path("outputs/move/", views.move_outputs, name="move_outputs"),
]
