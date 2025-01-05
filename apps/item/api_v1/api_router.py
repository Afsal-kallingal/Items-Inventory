from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# from django.urls import path
from rest_framework.routers import DefaultRouter, SimpleRouter

from apps.item.api_v1.views import (
    BrandViewSet,
    UQCViewSet,
    HsnSacViewSet,
    MeasurementUnitViewSet,
    StockGroupViewSet,
    TaxViewSet,
    StockClassificationViewSet,
    ProductViewSet,
    StockCategoryViewSet,
    BranchViewSet,
    GodownViewSet,
    RackViewSet,
    StockItemViewSet,
    ItemGroupViewSet,
    AlternateUnitsViewSet,
    BarcodeDetailsViewSet,
    KitchenModelViewset,
    stock_category_name_list,
    stock_group_name_list,
    rack_name_list,
    godown_name_list,
    stock_classification_name_list,
    stock_item_name_list,
    stock_nature_name_list,
    brand_name_list,
    StockItemSalesListView,
    StockItemPurchaseListView,
    # BarcodeViewSet,
    kitchen_name_list,
    unit_detailed_stockitem_list,
    godowns_for_the_branch,
    godown_stock_items,
    StockItemUnitsListView,
    # stock_jurnal_stock_report,
    CreatePrimaryEntitiesView,
    godown_location_wise_list_view,
    SalesPurchaseStockItemsDetailedViews,
    godown_rack_list,
)

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()


router.register("brand", BrandViewSet, basename="brand")
router.register("uqc", UQCViewSet, basename="uqc")
router.register("hsnsac", HsnSacViewSet, basename="hsnsac")
router.register("measurement-unit", MeasurementUnitViewSet, basename="measurement-unit")
router.register("stock-group", StockGroupViewSet, basename="stock-group")
router.register("tax", TaxViewSet, basename="tax")
router.register(
    "stock-classification", StockClassificationViewSet, basename="stock-classification"
)
router.register("stock-nature", ProductViewSet, basename="stock-nature")
router.register("stock-category", StockCategoryViewSet, basename="stock-category")
router.register("branch", BranchViewSet, basename="branch")
router.register("godown", GodownViewSet, basename="godown")
router.register("rack", RackViewSet, basename="rack")
router.register("stock-item", StockItemViewSet, basename="item")
router.register("item-groups", ItemGroupViewSet, basename="item-groups")
router.register("alternate-units", AlternateUnitsViewSet, basename="alternate-units")
router.register("barcode-details", BarcodeDetailsViewSet, basename="barcode-details")
router.register("kitchen", KitchenModelViewset, basename="kitchen")
# router.register("barcode", BarcodeViewSet, basename='barcode')


urlpatterns = [
    path(
        "stock-category-names/", stock_category_name_list, name="stock-category-names"
    ),
    path("stock-group-names/", stock_group_name_list, name="stock-group-names"),
    path("rack-names/", rack_name_list, name="rack-names"),
    path("godown-names/", godown_name_list, name="godown-names"),
    path(
        "stock-classification-names/",
        stock_classification_name_list,
        name="stock-classification-names",
    ),
    path("stock-item-names/", stock_item_name_list, name="stock-item-names"),
    path("stock-nature-names/", stock_nature_name_list, name="stock-nature-names"),
    path("brand-names/", brand_name_list, name="brand-names"),
    path(
        "stock-items/sales/",
        StockItemSalesListView.as_view(),
        name="stock-item-sales-list",
    ),
    path(
        "stock-items/purchase/",
        StockItemPurchaseListView.as_view(),
        name="stock-item-purchase-list",
    ),
    path("kitchen-names/", kitchen_name_list, name="kitchen-names"),
    path(
        "unit-detailed-stockitem-list/",
        unit_detailed_stockitem_list,
        name="unit-detailed-stockitem-list",
    ),
    path("branch-godown-list/", godowns_for_the_branch, name="brand-godown-list"),
    path("godown-items/", godown_stock_items, name="godown-stock-items"),
    path(
        "stock-items-units/",
        StockItemUnitsListView.as_view(),
        name="stock-item-units-list",
    ),
    path(
        "create-primary-entities/",
        CreatePrimaryEntitiesView.as_view(),
        name="create-primary-entities",
    ),
    path(
        "godowns/location-wise/<uuid:branch_id>/",
        godown_location_wise_list_view,
        name="godown_location_wise_list",
    ),
    path(
        "godowns/location-wise/",
        godown_location_wise_list_view,
        name="godown_location_primary",
    ),
    path(
        "stock-items/detailed/",
        SalesPurchaseStockItemsDetailedViews.as_view(),
        name="stock-item-detail_viewset",
    ),
    path("godown-rack-list/", godown_rack_list, name="godown-rack-list"),
]


app_name = "api_v1"
urlpatterns += router.urls

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
