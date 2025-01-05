import requests
from django.conf import settings
from django.db import transaction, models
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound
from rest_framework.decorators import action
from apps.main.viewsets import BaseModelViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.filters import SearchFilter
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework import serializers, status

# from rest_framework import status
from apps.inventory.models import (
    Openingstock,
    FinancialYear,
    StockReport,
    InventoryTransaction,
    StockJournal,
    # StockJournalEntry,
)
from apps.inventory.api_v1.serializers import (
    OpeningstockSerializer,
    FinancialYearSerializer,
    CreateInventoryTransactionSerializer,
    ListInventoryTransactionSerializer,
    StockSReportSerializer,
    StockJournalSerializer,
    CreateStockJournalSerializer,
    StockJournalFullListSerializer,
)


class OpeningBalanceViewSet(BaseModelViewSet):
    queryset = Openingstock.objects.all()
    serializer_class = OpeningstockSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ["stock_item__name"]

    def get_queryset(self):
        return Openingstock.objects.filter(
            organization_id=self.request.user.fk_organization
        )

    @swagger_auto_schema(
        operation_description="Retrieve a list of opening balances.",
        responses={200: OpeningstockSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Opening balances retrieved successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error retrieving opening balances: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Create a new opening balance.",
        responses={201: OpeningstockSerializer},
    )
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Opening balance created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error creating opening balance: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Retrieve details of a specific opening balance.",
        responses={200: OpeningstockSerializer},
    )
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Opening balance retrieved successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error retrieving opening balance: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Update an opening balance.",
        responses={200: OpeningstockSerializer},
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
                    "message": "Opening balance updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error updating opening balance: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Delete an opening balance.",
        responses={200: "Opening balance deleted successfully."},
    )
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Opening balance deleted successfully.",
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error deleting opening balance: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class FinancialYearViewSet(BaseModelViewSet):
    queryset = FinancialYear.objects.all()
    serializer_class = FinancialYearSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ["start_date"]

    def get_queryset(self):
        return FinancialYear.objects.filter(
            organization_id=self.request.user.fk_organization
        )

    @swagger_auto_schema(
        operation_description="Retrieve a list of financial years.",
        responses={200: FinancialYearSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Financial years retrieved successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error retrieving financial years: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Create a new financial year.",
        responses={201: FinancialYearSerializer},
    )
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Financial year created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error creating financial year: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Retrieve details of a specific financial year.",
        responses={200: FinancialYearSerializer},
    )
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Financial year retrieved successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error retrieving financial year: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Update a financial year.",
        responses={200: FinancialYearSerializer},
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
                    "message": "Financial year updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error updating financial year: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Delete a financial year.",
        responses={200: "Financial year deleted successfully."},
    )
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Financial year deleted successfully.",
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error deleting financial year: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class StockReportViewSet(BaseModelViewSet):
    queryset = StockReport.objects.all()
    serializer_class = StockSReportSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ["item__name", "godown__name", "financial_year__name"]

    def get_queryset(self):
        return StockReport.objects.filter(
            organization_id=self.request.user.fk_organization
        )

    @swagger_auto_schema(
        operation_description="Retrieve a list of stock summaries.",
        responses={200: StockSReportSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Stock summaries retrieved successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error retrieving stock summaries: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Retrieve details of a specific stock summary.",
        responses={200: StockSReportSerializer},
    )
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Stock summary retrieved successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error retrieving stock summary: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Create a new stock summary.",
        responses={201: StockSReportSerializer},
    )
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Stock summary created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error creating stock summary: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Update a stock summary.",
        responses={200: StockSReportSerializer},
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
                    "message": "Stock summary updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error updating stock summary: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Delete a specific stock summary.",
        responses={200: "Stock summary deleted successfully."},
    )
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Stock summary deleted successfully.",
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error deleting stock summary: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["get"], url_path="summary-by-item")
    @swagger_auto_schema(
        operation_description="Retrieve summarized stock details grouped by item.",
        responses={200: StockSReportSerializer(many=True)},
    )
    def summary_by_item(self, request, *args, **kwargs):
        try:
            queryset = (
                StockReport.objects.values("item__name")
                .annotate(
                    total_quantity=models.Sum("quantity"),
                    total_opening_balance=models.Sum("opening_balance"),
                    total_closing_balance=models.Sum("closing_balance"),
                )
                .order_by("item__name")
            )
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Stock summaries by item retrieved successfully.",
                    "data": queryset,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error retrieving stock summaries by item: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class InventoryTransactionViewSet(BaseModelViewSet):
    queryset = InventoryTransaction.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ["item__name", "reference_document"]

    def get_queryset(self):
        return InventoryTransaction.objects.filter(
            organization_id=self.request.user.fk_organization
        )

    def get_serializer_class(self):
        if self.action == "list":
            return ListInventoryTransactionSerializer
        # elif self.action == "create":
        #     return CreateInventoryTransactionSerializer
        else:
            return CreateInventoryTransactionSerializer

    @swagger_auto_schema(
        operation_description="Retrieve a list of inventory transactions.",
        responses={200: ListInventoryTransactionSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Inventory transactions retrieved successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error retrieving inventory transactions: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Create a new inventory transaction.",
        request_body=CreateInventoryTransactionSerializer,
        responses={201: CreateInventoryTransactionSerializer},
    )
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Inventory transaction created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        except serializers.ValidationError as ve:
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
                    "error": f"Error creating inventory transaction: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Update an inventory transaction.",
        request_body=CreateInventoryTransactionSerializer,
        responses={200: CreateInventoryTransactionSerializer},
    )
    @transaction.atomic
    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop("partial", False)
            instance = self.get_object()
            serializer = self.get_serializer(
                instance, data=request.data, partial=partial
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Inventory transaction updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except serializers.ValidationError as ve:
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
                    "error": f"Error updating inventory transaction: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Delete an inventory transaction.",
        responses={200: "Inventory transaction deleted successfully."},
    )
    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.delete()
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Inventory transaction deleted successfully.",
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error deleting inventory transaction: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class StockJournalViewSet(BaseModelViewSet):
    # queryset = StockJournal.objects.all()
    queryset = StockJournal.objects.prefetch_related(
        "entries", "source_godown", "destination_godown", "adjustment_godown"
    )
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ["voucher_number"]

    def get_queryset(self):
        return StockJournal.objects.filter(
            organization_id=self.request.user.fk_organization
        )

    def get_serializer_class(self):
        if self.action == "create" or self.action == "update":
            return CreateStockJournalSerializer
        elif self.action == "list" or self.action == "retrieve":
            return StockJournalFullListSerializer
        return StockJournalSerializer

    @swagger_auto_schema(
        operation_description="Create a new stock journal.",
        responses={201: CreateStockJournalSerializer},
    )
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Stock journal created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error creating stock journal: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Retrieve a list of stock journals.",
        responses={200: StockJournalSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Stock journals retrieved successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error retrieving stock journals: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Retrieve details of a specific stock journal.",
        responses={200: StockJournalSerializer},
    )
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Stock journal retrieved successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error retrieving stock journal: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Update a stock journal.",
        responses={200: CreateStockJournalSerializer},
    )
    @transaction.atomic
    def update(self, request, *args, **kwargs):
        """
        Update a Stock Journal and its related transactions.
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
                    "message": "Stock journal updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error updating stock journal: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @swagger_auto_schema(
        operation_description="Delete a specific stock journal.",
        responses={200: "Stock journal deleted successfully."},
    )
    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.entries.all().delete()
            self.perform_destroy(instance)
            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Stock journal deleted successfully.",
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": f"Error deleting stock journal: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


#     @swagger_auto_schema(
#         method="get",
#         operation_description="Retrieve entries for a specific stock journal.",
#         responses={200: StockJournalEntrySerializer(many=True)},
#     )
#     @action(detail=True, methods=["get"], url_path="entries")
#     def get_entries(self, request, pk=None):
#         try:
#             journal = self.get_object()
#             entries = journal.entries.all()
#             serializer = StockJournalEntrySerializer(entries, many=True)
#             return Response(
#                 {
#                     "StatusCode": 6000,
#                     "message": "Entries retrieved successfully.",
#                     "data": serializer.data,
#                 },
#                 status=status.HTTP_200_OK,
#             )
#         except Exception as e:
#             return Response(
#                 {
#                     "StatusCode": 6001,
#                     "error": f"Error retrieving entries: {str(e)}",
#                 },
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             )


class BulkInventoryTransactionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        transactions_data = request.data.get("transactions", [])

        if not transactions_data:
            return Response(
                {
                    "StatusCode": 6001,
                    "error": "Transactions data is required.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        response_data = []

        try:
            with transaction.atomic():
                for transaction_data in transactions_data:
                    serializer = CreateInventoryTransactionSerializer(
                        data=transaction_data
                    )
                    serializer.is_valid(raise_exception=True)
                    transaction_instance = serializer.save()
                    response_data.append(
                        {
                            "id": transaction_instance.id,
                            "message": "Transaction created successfully.",
                        }
                    )

            return Response(
                {
                    "StatusCode": 6000,
                    "message": "Bulk inventory transactions processed successfully.",
                    "data": response_data,
                },
                status=status.HTTP_201_CREATED,
            )

        except serializers.ValidationError as ve:
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
                    "StatusCode": 6002,
                    "error": f"Error processing bulk inventory transactions: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
