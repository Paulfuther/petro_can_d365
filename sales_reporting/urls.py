from django.urls import path

from . import views

app_name = "sales_reporting"

urlpatterns = [
    path(
        "upload/",
        views.upload_sales_reports,
        name="upload",
    ),
    path(
        "developer/",
        views.developer_workbook_inspector,
        name="developer_inspector",
    ),
    path(
        "developer/category-import/",
        views.developer_category_import,
        name="developer_category_import",
    ),
    path(
        "analytics/category-trend/",
        views.category_trend,
        name="category_trend",
    ),
]