from django.contrib import admin

# Register your models here.
from .models import (
    Category,
    CategoryResult,
    Product,
    SalesImport,
    SalesRecord,
    Store,
)


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = (
        "number",
        "name",
    )
    search_fields = (
        "number",
        "name",
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
        "level",
        "parent",
    )
    list_filter = (
        "level",
    )
    search_fields = (
        "code",
        "name",
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "sku",
        "description",
        "category",
    )
    search_fields = (
        "sku",
        "description",
    )
    list_filter = (
        "category",
    )


@admin.register(SalesImport)
class SalesImportAdmin(admin.ModelAdmin):
    list_display = (
        "store",
        "reporting_month",
        "from_date",
        "to_date",
        "channel",
        "source_filename",
        "imported_at",
    )
    list_filter = (
        "reporting_month",
        "channel",
    )
    search_fields = (
        "store__number",
        "store__name",
        "source_filename",
    )


@admin.register(CategoryResult)
class CategoryResultAdmin(admin.ModelAdmin):
    list_display = (
        "sales_import",
        "category",
        "quantity",
        "sales",
        "cogs",
        "gross_margin",
        "margin_percentage",
    )
    list_filter = (
        "sales_import__reporting_month",
        "sales_import__store",
    )
    search_fields = (
        "category__code",
        "category__name",
        "sales_import__store__number",
    )


@admin.register(SalesRecord)
class SalesRecordAdmin(admin.ModelAdmin):
    list_display = (
        "sales_import",
        "product",
        "quantity",
        "sales",
        "gross_margin",
        "margin_percentage",
    )
    search_fields = (
        "product__sku",
        "product__description",
    )