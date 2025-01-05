from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter
from django.urls import path, include

from apps.inventory.api_v1.views import (
    OpeningBalanceViewSet,
    FinancialYearViewSet,
    StockReportViewSet,
    InventoryTransactionViewSet,
    StockJournalViewSet,
    BulkInventoryTransactionView,
)

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()


router.register("opening-stock", OpeningBalanceViewSet, basename="opening-stock")
router.register("stock-report", StockReportViewSet, basename="stock-report")
router.register(
    "inventory-transaction",
    InventoryTransactionViewSet,
    basename="inventory-transaction",
)
router.register("financial-year", FinancialYearViewSet, basename="financial-year")
router.register("stock-journal", StockJournalViewSet, basename="stock-journal")


urlpatterns = [
    path("bulk-inventory-transactions/", BulkInventoryTransactionView.as_view(), name="bulk_inventory_transactions"),
]

app_name = "api_v1"
urlpatterns += router.urls
