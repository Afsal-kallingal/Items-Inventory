from django.contrib import admin
from apps.inventory.models import (
    FinancialYear,
    Openingstock,
    InventoryTransaction,
)


class FinancialYearAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "start_date",
        "end_date",
        "organization_id",
        "date_added",
        "updated_at",
        "is_deleted",
    )
    
    search_fields = ("start_date", "end_date", "organization_id")
    list_filter = ("is_deleted", "date_added", "updated_at")


class OpeningstockAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "organization_id",
        "stock_item",
        "quantity",
        "rate",
        "amount",
        "is_active",
        "date_added",
        "updated_at",
        "is_deleted",
    )

    search_fields = ("stock_item__name", "organization_id")
    list_filter = ("is_active", "is_deleted", "date_added", "updated_at")


class StockSummaryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "organization_id",
        "stock_item",
        "financial_year",
        "opening_balance",
        "closing_balance",
        "godown",
        "date_added",
        "updated_at",
        "is_deleted",
    )
    search_fields = ("stock_item__name", "organization_id")
    list_filter = ("is_deleted", "date_added", "updated_at")


class InventoryTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "organization_id",
        "item",
        "unit",
        "godown",
        "quantity",
        "transaction_type",
        "evaluation_method",
        "transaction_date",
        "reference_document_type",
        "reference_document",
        "date_added",
        "updated_at",
        "is_deleted",
    )
    search_fields = ("item__name", "organization_id", "reference_document")
    list_filter = (
        "transaction_type",
        "evaluation_method",
        "is_deleted",
        "date_added",
        "updated_at",
    )


admin.site.register(FinancialYear, FinancialYearAdmin)
admin.site.register(Openingstock, OpeningstockAdmin)
admin.site.register(InventoryTransaction, InventoryTransactionAdmin)
