from django.contrib import admin
from apps.item.models import (
    UQC,
    HsnSac,
    MeasurementUnit,
    StockGroup,
    ItemGroup,
    Tax,
    StockClassification,
    Product,
    Brand,
    StockCategory,
    Branch,
    Godown,
    Rack,
    StockItem,
)


class UQCAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "code",
        "organization_id",
        "date_added",
        "updated_at",
        "is_deleted",
    )
    search_fields = ("name", "code", "organization_id")
    list_filter = ("is_deleted", "date_added", "updated_at")


admin.site.register(UQC, UQCAdmin)


class HsnSacAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "hsnsac_code",
        "description",
        "organization_id",
        "date_added",
        "updated_at",
        "is_deleted",
    )
    search_fields = ("hsnsac_code", "description", "organization_id")
    list_filter = ("is_deleted", "date_added", "updated_at")


admin.site.register(HsnSac, HsnSacAdmin)


class MeasurementUnitAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "decimal_places",
        "uqc",
        "symbol",
        "organization_id",
        "date_added",
        "updated_at",
        "is_deleted",
    )
    search_fields = ("name", "symbol", "organization_id")
    list_filter = ("is_deleted", "date_added", "updated_at")


admin.site.register(MeasurementUnit, MeasurementUnitAdmin)


class StockGroupAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "alias",
        "organization_id",
        "parent_group",
        "is_active",
        "date_added",
        "updated_at",
        "is_deleted",
    )
    search_fields = ("name", "alias", "organization_id")
    list_filter = ("is_active", "is_deleted", "date_added", "updated_at")


admin.site.register(StockGroup, StockGroupAdmin)


class ItemGroupAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "group_name",
        "description",
        "parent_group",
        "date_added",
        "updated_at",
        "is_deleted",
    )
    search_fields = ("group_name", "description", "organization_id")
    list_filter = ("is_deleted", "date_added", "updated_at")


admin.site.register(ItemGroup, ItemGroupAdmin)


class TaxAdmin(admin.ModelAdmin):
    list_display = ("id", "tax", "date_added", "updated_at", "is_deleted")
    search_fields = ("tax", "organization_id")
    list_filter = ("is_deleted", "date_added", "updated_at")


admin.site.register(Tax, TaxAdmin)


class StockClassificationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "organization_id",
        "is_active",
        "date_added",
        "updated_at",
        "is_deleted",
    )
    search_fields = ("name", "organization_id")
    list_filter = ("is_active", "is_deleted", "date_added", "updated_at")


admin.site.register(StockClassification, StockClassificationAdmin)


class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "category",
        "organization_id",
        "is_active",
        "related_product",
        "date_added",
        "updated_at",
        "is_deleted",
    )
    search_fields = ("name", "organization_id")
    list_filter = ("is_active", "is_deleted", "date_added", "updated_at")


admin.site.register(Product, ProductAdmin)


class BrandAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "organization_id",
        "parent_brand",
        "date_added",
        "updated_at",
        "is_deleted",
    )
    search_fields = ("name", "organization_id")
    list_filter = ("is_deleted", "date_added", "updated_at")


admin.site.register(Brand, BrandAdmin)


class StockCategoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "alias",
        "organization_id",
        "is_active",
        "parent_category",
        "category_image",
        "date_added",
        "updated_at",
        "is_deleted",
    )
    search_fields = ("name", "alias", "organization_id")
    list_filter = ("is_active", "is_deleted", "date_added", "updated_at")


admin.site.register(StockCategory, StockCategoryAdmin)


class BranchAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "organization_id",
        "email",
        "state_id",
        "contact_number",
        "stock_limit",
        "is_active",
        "parent_branch",
        "date_added",
        "updated_at",
        "is_deleted",
    )
    search_fields = ("name", "email", "organization_id")
    list_filter = ("is_active", "is_deleted", "date_added", "updated_at")


admin.site.register(Branch, BranchAdmin)


class GodownAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "organization_id",
        "email",
        "state_id",
        "contact_number",
        "stock_limit",
        "is_active",
        "parent_godown",
        "branch",
        "date_added",
        "updated_at",
        "is_deleted",
    )
    search_fields = ("name", "email", "organization_id")
    list_filter = ("is_active", "is_deleted", "date_added", "updated_at")


admin.site.register(Godown, GodownAdmin)


class RackAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "organization_id",
        "godown",
        "parent_rack",
        "is_active",
        "date_added",
        "updated_at",
        "is_deleted",
    )
    search_fields = ("name", "organization_id")
    list_filter = ("is_active", "is_deleted", "date_added", "updated_at")


admin.site.register(Rack, RackAdmin)


class ItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "item_code",
        "organization_id",
        "item_type",
        "unit",
        "brand",
        "stock_nature",
        "date_added",
        "updated_at",
    )
    search_fields = ("name", "item_code", "barcode", "organization_id")
    list_filter = ("item_type", "is_deleted", "date_added", "updated_at")


admin.site.register(StockItem, ItemAdmin)


class ItemHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "item",
        "name",
        "item_code",
        "modified_at",
    )
    search_fields = ("item__name", "item_code", "barcode", "organization_id")
    list_filter = ("modified_at",)

    ordering = ["-modified_at"]
