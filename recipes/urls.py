from django.urls import path
from . import views

urlpatterns = [
    path("", views.sku_list, name="sku-list"),
    path("create/", views.sku_create, name="sku-create"),
    path("edit/<int:pk>/", views.sku_edit, name="sku-edit"),
    path("delete/<int:pk>/", views.sku_delete, name="sku-delete"),

    # Bulk Upload
    path("bulk-upload/", views.bulk_upload, name="bulk-upload"),
    path("download-sample-csv/", views.download_sample_csv, name="download-sample-csv"),
    path("download-sample-excel/", views.download_sample_excel, name="download-sample-excel"),

    # Bulk Actions
    path("bulk-actions/", views.bulk_actions, name="bulk-actions"),
]
