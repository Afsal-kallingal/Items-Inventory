import requests
from rest_framework import viewsets, status, pagination
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from drf_yasg.utils import swagger_auto_schema
from django.conf import settings
from apps.main.viewsets import BaseModelViewSet
from rest_framework import serializers
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from barcode import Code128
from barcode.writer import SVGWriter
from io import BytesIO
from django.core.files.base import ContentFile
from django.db.models import Max

# from rest_framework.response import Response
import base64
from rest_framework.views import APIView
import uuid
from rest_framework.exceptions import ValidationError

# from django.shortcuts import get_object_or_404
from apps.item.models import (
    Brand,
    UQC,
    HsnSac,
    MeasurementUnit,
    StockGroup,
    Tax,
    StockClassification,
    Product,
    StockCategory,
    Branch,
    Godown,
    Rack,
    StockItem,
    AlternateUnits,
    BarcodeDetails,
    ItemGroup,
    Kitchen,
)

from apps.item.api_v1.serializers import (
    BrandSerializer,
    UQCSerializer,
    HsnSacSerializer,
    MeasurementUnitSerializer,
    StockGroupTreeSerializer,
    TaxSerializer,
    StockClassificationSerializer,
    ProductSerializer,
    StockCategoryTreeSerializer,
    BranchSerializer,
    GodownSerializer,
    RackSerializer,
    ItemSerializer,
    AlternateUnitsSerializer,
    BarcodeDetailsSerializer,
    ItemGroupSerializer,
    ListViewIteamSerializer,
    SingleViewStockItemSerializer,
    CreateStockItemSerializer,
    StockcategoryNameSerializer,
    StockGroupNameSerializer,
    RackTreeSerializer,
    RackNameListSerializer,
    StockGroupSerializer,
    StockCategorySerializer,
    GodownNameSerializer,
    StockClassificationNameSerializer,
    SingleViewListViewProductSerializer,
    SingleViewListMeasurementUnitSerializer,
    StockItemNameSerializer,
    StockNaturalNameSerializer,
    UpdateStockItemSerializer,
    KitchenSerializer,
    StockItemSalesListSerializer,
    StockItemPurchaseListSerializer,
    UnitDetailedStockItemSerializer,
    StockItemUnitsListSerializer,
    KitchenNameSerializer,
    BrandNameList,
    StockJurnalItemReportSerializer,
    StockCategoryListSerializer,
    SalesPurchaseItemSerializer,
)


class StockItemViewSet(BaseModelViewSet):
    queryset = StockItem.objects.all()
    # serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ["name", "item_code"]

    def get_queryset(self):
        queryset = StockItem.objects.all()
        organization = self.request.user.fk_organization
        return queryset.filter(organization_id=organization)

    def get_serializer_class(self):
        if self.action == "list":
            return SingleViewStockItemSerializer
        elif self.action == "create":
            return CreateStockItemSerializer
        elif self.action == "retrieve":
            return SingleViewStockItemSerializer
        elif self.action in ["update", "partial_update"]:
            return UpdateStockItemSerializer
        else:
            return ItemSerializer

    @swagger_auto_schema(
        operation_description="Create a new item.",
        responses={201: CreateStockItemSerializer},
    )
    def create(self, request, *args, **kwargs):
        try:
            data = request.data.copy()

            image = data.get("image")
            if image and isinstance(image, str):
                try:
                    format, imgstr = (
                        image.split(";base64,") if "base64," in image else ("", image)
                    )
                    ext = format.split("/")[-1] if format else "png"
                    decoded_image = ContentFile(
                        base64.b64decode(imgstr), name=f"image.{ext}"
                    )
                    data["image"] = decoded_image
                except Exception:
                    raise ValidationError(
                        {"image": ["Invalid Base64-encoded image data."]}
                    )

            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Stock item created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        except serializers.ValidationError as ve:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Validation Error: {ve.detail}",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error creating stock item: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Retrieve a list of items.",
        responses={200: ListViewIteamSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(
                StockItem.objects.filter(organization_id=request.user.fk_organization)
            )
            serializer = ListViewIteamSerializer(queryset, many=True)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Items retrieved successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error retrieving items: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Update a specific item by ID.",
        responses={200: UpdateStockItemSerializer},
    )
    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop("partial", False)
            instance = self.get_object()
            serializer = self.get_serializer(
                instance, data=request.data, partial=partial
            )
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            full_serializer = SingleViewStockItemSerializer(instance)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Item updated successfully.",
                    "data": full_serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except serializers.ValidationError as ve:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Validation Error: {ve.detail}",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error updating item: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Retrieve a specific item by ID.",
        responses={200: SingleViewStockItemSerializer},
    )
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = StockItem.objects.get(id=kwargs["pk"])
            # instance = self.get_object()
            instance = StockItem.objects.get(id=kwargs["pk"])
            serializer = SingleViewStockItemSerializer(instance)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Item retrieved successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            print(e)
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error retrieving item: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Delete a specific item by ID.",
        responses={200: "Item deleted successfully."},
    )
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Item deleted successfully.",
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error deleting item: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class CreatePrimaryEntitiesView(APIView):
    def get_next_auto_id(self, model):
        max_auto_id = model.objects.aggregate(Max("auto_id"))["auto_id__max"] or 0
        return max_auto_id + 1

    def post(self, request, *args, **kwargs):
        organization_id = request.data.get("organization_id")

        if not organization_id:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": "organization_id is required.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        response_data = {}

        try:
            stock_category, created = StockCategory.objects.get_or_create(
                organization_id=organization_id,
                is_primary_stock_category=True,
                defaults={
                    "name": "Primary Stock Category",
                    "alias": "primary_stock_category",
                    "is_active": True,
                    "auto_id": self.get_next_auto_id(StockCategory),
                },
            )
            response_data["stock_category"] = {
                "status": "created" if created else "exists",
                "id": stock_category.id,
            }

            stock_group, created = StockGroup.objects.get_or_create(
                organization_id=organization_id,
                is_primary_group=True,
                defaults={
                    "name": "Primary Stock Group",
                    "alias": "primary_stock_group",
                    "is_active": True,
                    "auto_id": self.get_next_auto_id(StockGroup),
                },
            )
            response_data["stock_group"] = {
                "status": "created" if created else "exists",
                "id": stock_group.id,
            }

            measurement_unit, created = MeasurementUnit.objects.get_or_create(
                organization_id=organization_id,
                is_primary_unit=True,
                defaults={
                    "name": "Primary Measurement Unit",
                    "unit_type": "simple",
                    "is_active": True,
                    "auto_id": self.get_next_auto_id(MeasurementUnit),
                },
            )
            response_data["measurement_unit"] = {
                "status": "created" if created else "exists",
                "id": measurement_unit.id,
            }

            godown, created = Godown.objects.get_or_create(
                organization_id=organization_id,
                is_primary_godown=True,
                defaults={
                    "name": "Primary Godown",
                    "is_active": True,
                    "auto_id": self.get_next_auto_id(Godown),
                },
            )
            response_data["godown"] = {
                "status": "created" if created else "exists",
                "id": godown.id,
            }

            rack, created = Rack.objects.get_or_create(
                organization_id=organization_id,
                is_primary_rack=True,
                defaults={
                    "name": "Primary Rack",
                    "is_active": True,
                    "auto_id": self.get_next_auto_id(Rack),
                },
            )
            response_data["rack"] = {
                "status": "created" if created else "exists",
                "id": rack.id,
            }

            stock_classification, created = StockClassification.objects.get_or_create(
                organization_id=organization_id,
                is_primary_classification=True,
                defaults={
                    "name": "Primary Stock Classification",
                    "is_active": True,
                    "auto_id": self.get_next_auto_id(StockClassification),
                },
            )
            response_data["stock_classification"] = {
                "status": "created" if created else "exists",
                "id": stock_classification.id,
            }

            product, created = Product.objects.get_or_create(
                organization_id=organization_id,
                is_primary_stock_nature=True,
                defaults={
                    "name": "Primary Stock Nature",
                    "category": stock_classification,
                    "is_active": True,
                    "auto_id": self.get_next_auto_id(Product),
                },
            )
            response_data["product"] = {
                "status": "created" if created else "exists",
                "id": product.id,
            }

            brand, created = Brand.objects.get_or_create(
                organization_id=organization_id,
                is_primary_brand=True,
                defaults={
                    "name": "Primary Brand",
                    "is_active": True,
                    "auto_id": self.get_next_auto_id(Brand),
                },
            )
            response_data["brand"] = {
                "status": "created" if created else "exists",
                "id": brand.id,
            }

            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Primary entities created successfully.",
                    "data": response_data,
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return Response(
                {
                    "StatusCode": 6002,
                    "error": f"Error creating primary entities: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class CustomPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 1000
    page_query_param = "page"


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def stock_item_name_list(request):
    organization = request.user.fk_organization
    queryset = StockItem.objects.filter(organization_id=organization)
    # queryset = StockItem.objects.all()
    paginator = CustomPagination()
    paginated_queryset = paginator.paginate_queryset(queryset, request)
    serializer = StockItemNameSerializer(paginated_queryset, many=True)
    return paginator.get_paginated_response(serializer.data)


class BrandViewSet(BaseModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    filter_backends = [SearchFilter]
    search_fields = ["name"]

    def get_queryset(self):
        return Brand.objects.filter(organization_id=self.request.user.fk_organization)

    @swagger_auto_schema(
        operation_description="Create a new brand.",
        responses={201: BrandSerializer},
    )
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Brand created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error creating brand: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Retrieve a list of brands.",
        responses={200: BrandSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Brands retrieved successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error retrieving brands: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Retrieve a specific brand by ID.",
        responses={200: BrandSerializer},
    )
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Brand retrieved successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error retrieving brand: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Update a specific brand by ID.",
        responses={200: BrandSerializer},
    )
    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop("partial", False)
            instance = self.get_object()
            serializer = self.get_serializer(
                instance, data=request.data, partial=partial
            )
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Brand updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error updating brand: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Delete a specific brand by ID.",
        responses={200: "Brand deleted successfully."},
    )
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Brand deleted successfully.",
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error deleting brand: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UQCViewSet(BaseModelViewSet):
    queryset = UQC.objects.all()
    serializer_class = UQCSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ["name", "code"]

    @swagger_auto_schema(
        operation_description="Create a new UQC.",
        responses={201: UQCSerializer},
    )
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "UQC created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error creating UQC: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Retrieve a list of UQC.",
        responses={200: UQCSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "UQC retrieved successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error retrieving UQC: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Retrieve a specific UQC by ID.",
        responses={200: UQCSerializer},
    )
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "UQC retrieved successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error retrieving UQC: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Update a specific UQC.",
        responses={200: UQCSerializer},
    )
    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop("partial", False)
            instance = self.get_object()
            serializer = self.get_serializer(
                instance, data=request.data, partial=partial
            )
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "UQC updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except serializers.ValidationError as ve:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Validation Error: {ve.detail}",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error updating UQC: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Delete a specific UQC by ID.",
        responses={200: "UQC deleted successfully."},
    )
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "UQC deleted successfully.",
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error deleting UQC: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class HsnSacViewSet(BaseModelViewSet):
    queryset = HsnSac.objects.all()
    serializer_class = HsnSacSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ["hsnsac_code", "description"]

    def get_queryset(self):
        queryset = HsnSac.objects.all()
        organization = self.request.user.fk_organization
        return queryset.filter(organization_id=organization)

    @swagger_auto_schema(
        operation_description="Create a new HSN/SAC code.",
        responses={201: HsnSacSerializer},
    )
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "HSN/SAC code created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error creating HSN/SAC code: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Retrieve a list of HSN/SAC codes.",
        responses={200: HsnSacSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "HSN/SAC codes retrieved successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error retrieving HSN/SAC codes: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Retrieve a specific HSN/SAC code by ID.",
        responses={200: HsnSacSerializer},
    )
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "HSN/SAC code retrieved successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error retrieving HSN/SAC code: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Update a specific HSN/SAC code by ID.",
        responses={200: HsnSacSerializer},
    )
    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop("partial", False)
            instance = self.get_object()
            serializer = self.get_serializer(
                instance, data=request.data, partial=partial
            )
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "HSN/SAC code updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error updating HSN/SAC code: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Delete a specific HSN/SAC code by ID.",
        responses={200: "HSN/SAC code deleted successfully."},
    )
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "HSN/SAC code deleted successfully.",
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error deleting HSN/SAC code: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class MeasurementUnitViewSet(BaseModelViewSet):
    queryset = MeasurementUnit.objects.all()
    serializer_class = MeasurementUnitSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ["name"]

    def get_queryset(self):
        queryset = MeasurementUnit.objects.all()
        organization = self.request.user.fk_organization
        return queryset.filter(organization_id=organization)

    def get_serializer_class(self):
        if self.action == "list":
            return SingleViewListMeasurementUnitSerializer
        elif self.action == "retrieve":
            return SingleViewListMeasurementUnitSerializer
        else:
            return MeasurementUnitSerializer

    @swagger_auto_schema(
        operation_description="Create a new measurement unit.",
        responses={201: MeasurementUnitSerializer},
    )
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Measurement unit created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error creating measurement unit: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Retrieve a list of measurement units.",
        responses={200: SingleViewListMeasurementUnitSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Measurement units retrieved successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error retrieving measurement units: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Retrieve a specific measurement unit by ID.",
        responses={200: SingleViewListMeasurementUnitSerializer},
    )
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Measurement unit retrieved successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error retrieving measurement unit: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Update a specific measurement unit by ID.",
        responses={200: MeasurementUnitSerializer},
    )
    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop("partial", False)
            instance = self.get_object()
            serializer = self.get_serializer(
                instance, data=request.data, partial=partial
            )
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Measurement unit updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error updating measurement unit: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Delete a specific measurement unit by ID.",
        responses={200: "Measurement unit deleted successfully."},
    )
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Measurement unit deleted successfully.",
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error deleting measurement unit: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class StockGroupViewSet(BaseModelViewSet):
    queryset = StockGroup.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ["name", "alias"]

    def get_queryset(self):
        queryset = StockGroup.objects.all()
        organization = self.request.user.fk_organization
        return queryset.filter(organization_id=organization)

    def get_serializer_class(self):
        if self.action == "tree":
            return StockGroupTreeSerializer
        return StockGroupSerializer

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Stock group created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error creating stock group: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Stock groups retrieved successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error retrieving stock groups: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["get"], url_path="tree")
    def tree(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset().filter(parent_group__isnull=True)
            serializer = StockGroupTreeSerializer(queryset, many=True)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Stock groups retrieved successfully in tree structure.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error retrieving stock groups: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop("partial", False)
            instance = self.get_object()
            serializer = self.get_serializer(
                instance, data=request.data, partial=partial
            )
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Stock group updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error updating stock group: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def destroy(self, request, *args, **kwargs):
        """
        Delete a stock group.
        """
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Stock group deleted successfully.",
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error deleting stock group: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def stock_group_name_list(request):
    organization = request.user.fk_organization
    queryset = StockGroup.objects.filter(organization_id=organization)
    # queryset = StockGroup.objects.all()
    serializer = StockGroupNameSerializer(queryset, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def stock_nature_name_list(request):
    organization = request.user.fk_organization
    queryset = Product.objects.filter(organization_id=organization)
    # queryset = Product.objects.all()
    serializer = StockNaturalNameSerializer(queryset, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def brand_name_list(request):
    organization = request.user.fk_organization
    queryset = Brand.objects.filter(organization_id=organization)
    serializer = BrandNameList(queryset, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def kitchen_name_list(request):
    organization = request.user.fk_organization
    queryset = Kitchen.objects.filter(organization_id=organization)
    serializer = KitchenNameSerializer(queryset, many=True)
    return Response(serializer.data)


class TaxViewSet(BaseModelViewSet):
    queryset = Tax.objects.all()
    serializer_class = TaxSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ["tax"]

    # def get_queryset(self):
    #     queryset = Tax.objects.all()
    #     organization = self.request.user.fk_organization
    #     return queryset.filter(organization_id=organization)

    @swagger_auto_schema(
        operation_description="Create a new tax entry.",
        responses={201: TaxSerializer},
    )
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Tax entry created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error creating tax entry: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Retrieve a list of taxes.",
        responses={200: TaxSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Taxes retrieved successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error retrieving taxes: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Retrieve a specific tax entry by ID.",
        responses={200: TaxSerializer},
    )
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Tax entry retrieved successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error retrieving tax entry: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Update a specific tax entry by ID.",
        responses={200: TaxSerializer},
    )
    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop("partial", False)
            instance = self.get_object()
            serializer = self.get_serializer(
                instance, data=request.data, partial=partial
            )
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Tax entry updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error updating tax entry: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Delete a specific tax entry by ID.",
        responses={200: "Tax entry deleted successfully."},
    )
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Tax entry deleted successfully.",
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error deleting tax entry: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def stock_classification_name_list(request):
    organization = request.user.fk_organization
    queryset = StockClassification.objects.filter(organization_id=organization)
    # queryset = StockClassification.objects.all()
    serializer = StockClassificationNameSerializer(queryset, many=True)
    return Response(serializer.data)


class StockClassificationViewSet(BaseModelViewSet):
    queryset = StockClassification.objects.all()
    serializer_class = StockClassificationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ["name"]

    def get_queryset(self):
        return StockClassification.objects.filter(
            organization_id=self.request.user.fk_organization
        )

    @swagger_auto_schema(
        operation_description="Create a new stock classification.",
        responses={201: StockClassificationSerializer},
    )
    def create(self, request, *args, **kwargs):
        try:
            # data = request.data
            # # Add organization_id from the request's user
            # data['organization_id'] = request.user.fk_organization

            # serializer = StockClassificationSerializer(data=data)
            # serializer.is_valid(raise_exception=True)
            # serializer.save()

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Stock classification created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error creating stock classification: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Retrieve a list of stock classifications.",
        responses={200: StockClassificationSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Stock classifications retrieved successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error retrieving stock classifications: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Retrieve a specific stock classification by ID.",
        responses={200: StockClassificationSerializer},
    )
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Stock classification retrieved successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error retrieving stock classification: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Update a specific stock classification by ID.",
        responses={200: StockClassificationSerializer},
    )
    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop("partial", False)
            instance = self.get_object()
            serializer = self.get_serializer(
                instance, data=request.data, partial=partial
            )
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Stock classification updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error updating stock classification: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Delete a specific stock classification by ID.",
        responses={200: "Stock classification deleted successfully."},
    )
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Stock classification deleted successfully.",
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error deleting stock classification: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ProductViewSet(BaseModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ["name"]

    def get_queryset(self):
        return Product.objects.filter(organization_id=self.request.user.fk_organization)

    def get_serializer_class(self):
        if self.action == "list":
            return SingleViewListViewProductSerializer
        elif self.action == "retrieve":
            return SingleViewListViewProductSerializer
        else:
            return ProductSerializer

    @swagger_auto_schema(
        operation_description="Retrieve a list of products.",
        responses={200: SingleViewListViewProductSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Products retrieved successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error retrieving products: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Retrieve details of a specific product by ID.",
        responses={200: SingleViewListViewProductSerializer},
    )
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Product retrieved successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error retrieving product: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Create a new product.",
        responses={201: ProductSerializer},
    )
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Product created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        except serializers.ValidationError as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Validation Error: {e.detail}",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error creating product: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Update an existing product.",
        responses={200: ProductSerializer},
    )
    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop("partial", False)
            instance = self.get_object()
            serializer = self.get_serializer(
                instance, data=request.data, partial=partial
            )
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Product updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except serializers.ValidationError as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Validation Error: {e.detail}",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error updating product: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Delete a specific product by ID.",
        responses={200: "Product deleted successfully."},
    )
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Product deleted successfully.",
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error deleting product: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class StockCategoryViewSet(BaseModelViewSet):
    queryset = StockCategory.objects.all()
    serializer_class = StockCategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ["name", "alias"]

    def get_queryset(self):
        return StockCategory.objects.filter(
            organization_id=self.request.user.fk_organization
        )

    def get_serializer_class(self):
        if self.action == "list":
            return StockCategoryListSerializer
        else:
            return StockCategorySerializer

    def create(self, request, *args, **kwargs):
        try:
            data = request.data.copy()

            image = data.get("category_image")
            if image and isinstance(image, str):
                try:
                    format, imgstr = (
                        image.split(";base64,") if "base64," in image else ("", image)
                    )
                    ext = format.split("/")[-1] if format else "png"
                    decoded_image = ContentFile(
                        base64.b64decode(imgstr), name=f"category_image.{ext}"
                    )
                    data["category_image"] = decoded_image
                except Exception:
                    raise ValidationError(
                        {"category_image": ["Invalid Base64-encoded image data."]}
                    )

            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Stock category created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        except ValidationError as ve:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": ve.detail,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error creating stock category: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Stock categories retrieved successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error retrieving stock categories: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["get"], url_path="tree")
    def tree(self, request, *args, **kwargs):
        try:
            # Get top-level categories
            queryset = self.get_queryset().filter(parent_category__isnull=True)
            serializer = StockCategoryTreeSerializer(queryset, many=True)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Stock categories retrieved successfully in tree structure.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error retrieving stock categories in tree: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop("partial", False)
            instance = self.get_object()
            serializer = self.get_serializer(
                instance, data=request.data, partial=partial
            )
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Stock category updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error updating stock category: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Stock category deleted successfully.",
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error deleting stock category: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def stock_category_name_list(request):
    queryset = StockCategory.objects.filter(
        organization_id=request.user.fk_organization
    )
    # queryset = StockCategory.objects.all()
    serializer = StockcategoryNameSerializer(queryset, many=True)
    return Response(serializer.data)


class BranchViewSet(BaseModelViewSet):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ["name"]

    @swagger_auto_schema(
        operation_description="Create a new branch.",
        responses={201: BranchSerializer},
    )
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Branch created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error creating branch: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Retrieve a list of branches.",
        responses={200: BranchSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Branches retrieved successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error retrieving branches: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Retrieve details of a specific branch.",
        responses={200: BranchSerializer},
    )
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Branch details retrieved successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error retrieving branch: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Update a branch.",
        responses={200: BranchSerializer},
    )
    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop("partial", False)
            instance = self.get_object()
            serializer = self.get_serializer(
                instance, data=request.data, partial=partial
            )
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Branch updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error updating branch: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Delete a branch.",
        responses={200: "Branch deleted successfully."},
    )
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Branch deleted successfully.",
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error deleting branch: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class GodownViewSet(BaseModelViewSet):
    queryset = Godown.objects.all()
    serializer_class = GodownSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ["name"]

    def get_queryset(self):
        return Godown.objects.filter(organization_id=self.request.user.fk_organization)

    # def get_serializer_class(self):
    #     if self.action == "list":
    #         return SingleViewGodownSerializer
    #     elif self.action == "retrieve":
    #         return SingleViewGodownSerializer
    #     else:
    #         return GodownSerializer

    @swagger_auto_schema(
        operation_description="Create a new godown.",
        responses={201: GodownSerializer},
    )
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Godown created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error creating godown: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Retrieve a list of godowns.",
        responses={200: GodownSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Godowns retrieved successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error retrieving godowns: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Retrieve details of a specific godown.",
        responses={200: GodownSerializer},
    )
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Godown details retrieved successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error retrieving godown: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Update a godown.",
        responses={200: GodownSerializer},
    )
    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop("partial", False)
            instance = self.get_object()
            serializer = self.get_serializer(
                instance, data=request.data, partial=partial
            )
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Godown updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error updating godown: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Delete a godown.",
        responses={200: "Godown deleted successfully."},
    )
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Godown deleted successfully.",
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error deleting godown: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def godown_name_list(request):
    queryset = Godown.objects.filter(organization_id=request.user.fk_organization)
    # queryset = Godown.objects.all()
    serializer = GodownNameSerializer(queryset, many=True)
    return Response(serializer.data)


class RackViewSet(BaseModelViewSet):
    queryset = Rack.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ["name", "godown__name"]

    def get_queryset(self):
        return Rack.objects.filter(organization_id=self.request.user.fk_organization)

    def get_serializer_class(self):
        if self.action == "tree":
            return RackTreeSerializer
        return RackSerializer

    @swagger_auto_schema(
        operation_description="Create a new rack.",
        responses={201: RackSerializer},
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                "StatusCode": 6000,
                "message": "Rack created successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )

    @swagger_auto_schema(
        operation_description="Retrieve a specific rack by ID.",
        responses={200: RackSerializer},
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(
            {
                "StatusCode": 6000,
                "message": "Rack retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @swagger_auto_schema(
        operation_description="Update a rack.",
        responses={200: RackSerializer},
    )
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                "StatusCode": 6000,
                "message": "Rack updated successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @swagger_auto_schema(
        operation_description="Delete a rack.",
        responses={200: "Rack deleted successfully."},
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {
                "StatusCode": 6000,
                "message": "Rack deleted successfully.",
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"], url_path="tree")
    def tree(self, request):
        queryset = self.get_queryset().filter(parent_rack__isnull=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {
                "StatusCode": 6000,
                "message": "Racks retrieved in tree structure.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def rack_name_list(request):
    queryset = Rack.objects.filter(organization_id=request.user.fk_organization)
    # queryset = Rack.objects.all()
    serializer = RackNameListSerializer(queryset, many=True)
    return Response(serializer.data)


class AlternateUnitsViewSet(BaseModelViewSet):
    queryset = AlternateUnits.objects.all()
    serializer_class = AlternateUnitsSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ["stock_item__name"]

    @swagger_auto_schema(
        operation_description="Retrieve a list of alternate units.",
        responses={200: AlternateUnitsSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Alternate units retrieved successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error retrieving alternate units: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Create a new alternate unit.",
        responses={201: AlternateUnitsSerializer},
    )
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Alternate unit created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error creating alternate unit: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Retrieve a specific alternate unit by ID.",
        responses={200: AlternateUnitsSerializer},
    )
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a specific alternate unit.
        """
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Alternate unit retrieved successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error retrieving alternate unit: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Update an existing alternate unit.",
        responses={200: AlternateUnitsSerializer},
    )
    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop("partial", False)
            instance = self.get_object()
            serializer = self.get_serializer(
                instance, data=request.data, partial=partial
            )
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Alternate unit updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error updating alternate unit: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Delete a specific alternate unit.",
        responses={200: "Alternate unit deleted successfully."},
    )
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Alternate unit deleted successfully.",
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error deleting alternate unit: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class BarcodeDetailsViewSet(BaseModelViewSet):
    queryset = BarcodeDetails.objects.all()
    serializer_class = BarcodeDetailsSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ["organization_id", "barcode", "item_name"]

    @swagger_auto_schema(
        operation_description="Create a new barcode detail.",
        responses={201: BarcodeDetailsSerializer},
    )
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Barcode detail created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error creating barcode detail: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Retrieve a flat list of barcode details.",
        responses={200: BarcodeDetailsSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        """
        Retrieve a list of all barcode details.
        """
        try:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Barcode details retrieved successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error retrieving barcode details: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Retrieve a specific barcode detail by ID.",
        responses={200: BarcodeDetailsSerializer},
    )
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Barcode detail retrieved successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error retrieving barcode detail: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Update an existing barcode detail.",
        responses={200: BarcodeDetailsSerializer},
    )
    def update(self, request, *args, **kwargs):
        """
        Update an existing barcode detail.
        """
        try:
            partial = kwargs.pop("partial", False)
            instance = self.get_object()
            serializer = self.get_serializer(
                instance, data=request.data, partial=partial
            )
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Barcode detail updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error updating barcode detail: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Delete a specific barcode detail.",
        responses={200: "Barcode detail deleted successfully."},
    )
    def destroy(self, request, *args, **kwargs):
        """
        Delete a specific barcode detail by ID.
        """
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Barcode detail deleted successfully.",
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error deleting barcode detail: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ItemGroupViewSet(BaseModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = ItemGroup.objects.all()
    serializer_class = ItemGroupSerializer
    filter_backends = [SearchFilter]
    search_fields = ["group_name"]

    @swagger_auto_schema(
        operation_description="Retrieve a list of item groups.",
        responses={200: ItemGroupSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class KitchenModelViewset(BaseModelViewSet):
    queryset = Kitchen.objects.all()
    serializer_class = KitchenSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ["name"]

    @swagger_auto_schema(
        operation_description="Retrieve a list of Kitchen records.",
        responses={200: KitchenSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Kitchen records retrieved successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error retrieving Kitchen records: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Retrieve a specific Kitchen record by ID.",
        responses={200: KitchenSerializer},
    )
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Kitchen record retrieved successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error retrieving Kitchen record: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Create a new Kitchen record.",
        responses={201: KitchenSerializer},
    )
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Kitchen record created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error creating Kitchen record: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Update a specific Kitchen record by ID.",
        responses={200: KitchenSerializer},
    )
    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop("partial", False)
            instance = self.get_object()
            serializer = self.get_serializer(
                instance, data=request.data, partial=partial
            )
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Kitchen record updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error updating Kitchen record: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Partially update a specific Kitchen record by ID.",
        responses={200: KitchenSerializer},
    )
    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Delete a specific Kitchen record by ID.",
        responses={200: "Kitchen record deleted successfully."},
    )
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Kitchen record deleted successfully.",
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error deleting Kitchen record: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class StockItemSalesListView(ListAPIView):
    serializer_class = StockItemSalesListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ["name"]
    pagination_class = CustomPagination

    def get_queryset(self):
        return StockItem.objects.filter(
            organization_id=self.request.user.fk_organization
        )

        # return StockItem.objects.all()


class StockItemPurchaseListView(ListAPIView):
    serializer_class = StockItemPurchaseListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ["name"]
    pagination_class = CustomPagination

    def get_queryset(self):
        return StockItem.objects.filter(
            organization_id=self.request.user.fk_organization
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def unit_detailed_stockitem_list(request):
    queryset = StockItem.objects.filter(organization_id=request.user.fk_organization)
    # queryset = StockItem.objects.all()
    serializer = UnitDetailedStockItemSerializer(queryset, many=True)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def godowns_for_the_branch(request):
    branch_id = request.data.get("branch")

    if not branch_id:
        return Response(
            {"StatusCode": 6001, "message": "Branch ID is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        godowns = Godown.objects.filter(branch=branch_id)

        if not godowns.exists():
            return Response(
                {
                    "StatusCode": 6001,
                    "message": "No godowns found for the provided branch ID.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = GodownNameSerializer(godowns, many=True)

        return Response(
            {
                "StatusCode": 6000,
                "message": "Godowns retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        return Response(
            {
                "StatusCode": 6001,
                "message": f"An error occurred: {str(e)}",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# @api_view(["POST"])
# @permission_classes([IsAuthenticated])
# def godowns_for_the_branch(request):
#     branch_id = request.data.get("branch")

#     if not branch_id:
#         return Response(
#             {"StatusCode": 6001, "message": "Branch ID is required."},
#             status=status.HTTP_400_BAD_REQUEST,
#         )

#     branch_id = branch_id.strip()
#     print(f"Received Branch ID: {repr(branch_id)}")  # Log exact input

#     try:
#         # Query godowns
#         godowns = Godown.objects.filter(branch__iexact=branch_id)
#         print(f"Godowns Count: {godowns.count()}")  # Log count
#         print(f"Query: {godowns.query}")  # Log raw SQL query

#         serializer = GodownNameSerializer(godowns, many=True)

#         return Response(
#             {
#                 "StatusCode": 6000,
#                 "message": "Godowns retrieved successfully.",
#                 "data": serializer.data,
#             },
#             status=status.HTTP_200_OK,
#         )
#     except Exception as e:
#         return Response(
#             {
#                 "StatusCode": 6001,
#                 "message": f"An error occurred: {str(e)}",
#             },
#             status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def godown_stock_items(request):
    godown_id = request.data.get("godown")
    if not godown_id:
        return Response(
            {"error": "godown ID is required."}, status=status.HTTP_400_BAD_REQUEST
        )
    try:
        stocks = StockItem.objects.filter(godown=godown_id)
        serializer = StockJurnalItemReportSerializer(stocks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class StockItemUnitsListView(ListAPIView):
    # queryset = StockItem.objects.prefetch_related("alternative_units", "unit").all()
    queryset = StockItem.objects.all()
    serializer_class = StockItemUnitsListSerializer
    # permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ["name"]


# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def stock_jurnal_stock_report(request):
#     queryset = StockItem.objects.filter(organization_id=request.user.fk_organization)
#     # queryset = StockItem.objects.all()
#     serializer = StockJurnalItemReportSerializer(queryset, many=True)
#     return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def godown_location_wise_list_view(request, branch_id=None):
    try:
        if branch_id:
            godowns = Godown.objects.filter(branch=branch_id)

            if not godowns.exists():
                return Response(
                    {
                        "StatusCode": 6001,
                        "message": "No godowns found for the provided branch ID.",
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            godowns = Godown.objects.filter(is_primary_godown=True)

            if not godowns.exists():
                return Response(
                    {
                        "StatusCode": 6001,
                        "message": "No primary godowns found.",
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

        serializer = GodownNameSerializer(godowns, many=True)

        return Response(
            {
                "StatusCode": 6000,
                "message": "Godowns retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        return Response(
            {
                "StatusCode": 6001,
                "message": f"An error occurred: {str(e)}",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class SalesPurchaseStockItemsDetailedViews(ListAPIView):
    serializer_class = SalesPurchaseItemSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ["name"]
    pagination_class = CustomPagination

    def get_queryset(self):
        return StockItem.objects.filter(
            organization_id=self.request.user.fk_organization
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def godown_rack_list(request):
    try:
        godown_id = request.data.get("godown")
        if not godown_id:
            return Response(
                {"detail": "Godown ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        racks = Rack.objects.filter(godown=godown_id)
        serializer = RackNameListSerializer(racks, many=True)
        return Response(
            {"status": "success", "data": serializer.data},
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return Response(
            {"status": "error", "message": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
