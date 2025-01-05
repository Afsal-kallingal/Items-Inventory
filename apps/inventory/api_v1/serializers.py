from django.db import transaction
from rest_framework import serializers
from apps.main.serializers import BaseModelSerializer
from django.db.models import Max
from apps.inventory.models import (
    Openingstock,
    FinancialYear,
    StockReport,
    InventoryTransaction,
    StockJournal,
    StockJournalEntry,
)
# from datetime import  date


class OpeningstockSerializer(BaseModelSerializer):
    class Meta:
        model = Openingstock
        fields = "__all__"
        read_only_fields = [
            "id",
            "auto_id",
            "date_added",
            "creator",
            "updated_at",
            "updated_by",
        ]

    def update(self, instance, validated_data):
        instance.organization_id = validated_data.get(
            "organization_id", instance.organization_id
        )
        instance.quantity = validated_data.get("quantity", instance.quantity)
        instance.stock_item = validated_data.get("stock_item", instance.stock_item)
        instance.rate = validated_data.get("rate", instance.rate)
        instance.amount = validated_data.get("amount", instance.amount)
        instance.is_active = validated_data.get("is_active", instance.is_active)
        instance.save()
        return instance


class FinancialYearSerializer(BaseModelSerializer):
    class Meta:
        model = FinancialYear
        fields = "__all__"
        read_only_fields = [
            "id",
            "auto_id",
            "date_added",
            "creator",
            "updated_at",
            "updated_by",
        ]

    def update(self, instance, validated_data):
        instance.organization_id = validated_data.get(
            "organization_id", instance.organization_id
        )
        instance.start_date = validated_data.get("start_date", instance.start_date)
        instance.end_date = validated_data.get("end_date", instance.end_date)
        instance.is_active = validated_data.get("is_active", instance.is_active)
        instance.save()
        return instance

    def validate_organization_id(self, value):
        if not value:
            raise serializers.ValidationError("Organization ID is required.")
        return value


class InventoryBaseSerializer(serializers.ModelSerializer):
    date_added = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    creator = serializers.CharField(read_only=True)
    updated_by = serializers.CharField(read_only=True)

    def create(self, validated_data):
        request = self.context.get("request", None)
        if request and hasattr(request, "user") and request.user:
            validated_data["creator"] = str(request.user.id)
            validated_data["updated_by"] = str(request.user.id)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        request = self.context.get("request", None)
        if request and hasattr(request, "user") and request.user:
            validated_data["updated_by"] = str(request.user.id)
        return super().update(instance, validated_data)

    def validate(self, data):
        if not data.get("organization_id"):
            raise serializers.ValidationError("Organization ID is required.")
        return data

    class Meta:
        abstract = True


class StockSReportSerializer(InventoryBaseSerializer):
    class Meta:
        model = StockReport
        fields = "__all__"
        read_only_fields = [
            "id",
            # "auto_id",
            "date_added",
            "creator",
            "updated_at",
            "updated_by",
        ]


class CreateInventoryTransactionSerializer(InventoryBaseSerializer):
    class Meta:
        model = InventoryTransaction
        fields = "__all__"
        read_only_fields = [
            "id",
            # "auto_id",
            "date_added",
            "creator",
            "updated_at",
            "updated_by",
        ]

    def validate(self, data):
        if data["quantity"] <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero.")
        if not data.get("organization_id"):
            raise serializers.ValidationError("Organization ID is required.")
        if not data.get("item"):
            raise serializers.ValidationError("Item is required.")
        if not data.get("transaction_type"):
            raise serializers.ValidationError("Transaction type is required.")
        return data

    def create(self, validated_data):
        transaction = InventoryTransaction(**validated_data)
        transaction.save()
        return transaction

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class ListInventoryTransactionSerializer(InventoryBaseSerializer):
    item_name = serializers.CharField(source="item.name", read_only=True)
    godown_name = serializers.CharField(source="godown.name", read_only=True)
    unit_name = serializers.CharField(source="unit.name", read_only=True)

    class Meta:
        model = InventoryTransaction
        fields = [
            "id",
            "organization_id",
            "item",
            "item_name",
            "unit",
            "unit_name",
            "godown",
            "godown_name",
            "quantity",
            "transaction_type",
            "evaluation_method",
            "transaction_date",
            "reference_document_type",
            "reference_document",
            "remarks",
        ]
        read_only_fields = ["id", "transaction_date"]


# class InventoryTransactionSerializer(BaseModelSerializer):
#     class Meta:
#         model = InventoryTransaction
#         fields = "__all__"
#         read_only_fields = [
#             "id",
#             "auto_id",
#             "date_added",
#             "creator",
#             "updated_at",
#             "updated_by",
#         ]

#     def validate(self, data):
#         if data["quantity"] <= 0:
#             raise serializers.ValidationError("Quantity must be greater than zero.")
#         if not data.get("organization_id"):
#             raise serializers.ValidationError("Organization ID is required.")
#         if not data.get("item"):
#             raise serializers.ValidationError("Item is required.")
#         if not data.get("transaction_type"):
#             raise serializers.ValidationError("Transaction type is required.")
#         return data

#     @transaction.atomic
#     def create(self, validated_data):
#         transaction = super().create(validated_data)

#         self._update_stock_report(transaction)

#         return transaction

#     @transaction.atomic
#     def update(self, instance, validated_data):
#         previous_quantity = instance.quantity
#         previous_type = instance.transaction_type

#         for attr, value in validated_data.items():
#             setattr(instance, attr, value)
#         instance.save()

#         self._adjust_stock_report(instance, previous_quantity, previous_type)

#         return instance

#     def _update_stock_report(self, transaction):
#         stock_report, created = StockReport.objects.get_or_create(
#             organization_id=transaction.organization_id,
#             item=transaction.item,
#             godown=transaction.godown,
#             defaults={"opening_balance": 0, "closing_balance": 0},
#         )

#         if transaction.transaction_type == "Inbound":
#             stock_report.closing_balance += transaction.quantity
#         elif transaction.transaction_type == "Outbound":
#             stock_report.closing_balance -= transaction.quantity

#         stock_report.save()

#     def _adjust_stock_report(self, transaction, previous_quantity, previous_type):
#         stock_report = StockReport.objects.get(
#             organization_id=transaction.organization_id,
#             item=transaction.item,
#             godown=transaction.godown,
#         )

#         if previous_type == "Inbound":
#             stock_report.closing_balance -= previous_quantity
#         elif previous_type == "Outbound":
#             stock_report.closing_balance += previous_quantity

#         if transaction.transaction_type == "Inbound":
#             stock_report.closing_balance += transaction.quantity
#         elif transaction.transaction_type == "Outbound":
#             stock_report.closing_balance -= transaction.quantity

#         stock_report.save()


# class StockJournalEntrySerializer(BaseModelSerializer):
#     class Meta:
#         model = StockJournalEntry
#         fields = "__all__"


# class CreateStockJournalSerializer(BaseModelSerializer):
#     entries = StockJournalEntrySerializer(many=True, write_only=True)

#     class Meta:
#         model = StockJournal
#         fields = "__all__"

#     @transaction.atomic
#     def create(self, validated_data):
#         entries_data = validated_data.pop("entries", [])
#         stock_journal = StockJournal.objects.create(**validated_data)

#         for entry_data in entries_data:
#             journal_entry = StockJournalEntry.objects.create(
#                 journal=stock_journal, **entry_data
#             )
#             self._create_inventory_transactions(journal_entry, stock_journal)

#         return stock_journal

#     def _create_inventory_transactions(self, journal_entry, stock_journal):
#         if stock_journal.transaction_type == 0:  # Stock-Transfer
#             # Outbound transaction from source godown
#             outbound_transaction = InventoryTransaction.objects.create(
#                 organization_id=stock_journal.organization_id,
#                 item=journal_entry.item,
#                 unit=journal_entry.item.unit,
#                 godown=stock_journal.source_godown,
#                 quantity=-journal_entry.quantity,  # Negative for outbound
#                 transaction_type="Outbound",
#                 reference_document_type="StockJournal",
#                 reference_document=f"Journal {stock_journal.voucher_number}",
#                 remarks=f"Transfer from {stock_journal.source_godown} to {stock_journal.destination_godown}",
#             )
#             self._log_transaction_effect(outbound_transaction)

#             # Inbound transaction to destination godown
#             inbound_transaction = InventoryTransaction.objects.create(
#                 organization_id=stock_journal.organization_id,
#                 item=journal_entry.item,
#                 unit=journal_entry.item.unit,
#                 godown=stock_journal.destination_godown,
#                 quantity=journal_entry.quantity,  # Positive for inbound
#                 transaction_type="Inbound",
#                 reference_document_type="StockJournal",
#                 reference_document=f"Journal {stock_journal.voucher_number}",
#                 remarks=f"Transfer to {stock_journal.destination_godown} from {stock_journal.source_godown}",
#             )
#             self._log_transaction_effect(inbound_transaction)

#         elif stock_journal.transaction_type == 1:  # Stock-Adjustment
#             adjustment_transaction = InventoryTransaction.objects.create(
#                 organization_id=stock_journal.organization_id,
#                 item=journal_entry.item,
#                 unit=journal_entry.item.unit,
#                 godown=stock_journal.adjustment_godown,
#                 quantity=journal_entry.quantity,
#                 transaction_type="Adjustment",
#                 reference_document_type="StockJournal",
#                 reference_document=f"Journal {stock_journal.voucher_number}",
#                 remarks=f"Adjustment for {stock_journal.adjustment_godown}",
#             )
#             self._log_transaction_effect(adjustment_transaction)

#         elif stock_journal.transaction_type == 2:  # Stock-Journal
#             journal_transaction = InventoryTransaction.objects.create(
#                 organization_id=stock_journal.organization_id,
#                 item=journal_entry.item,
#                 unit=journal_entry.item.unit,
#                 godown=stock_journal.source_godown,
#                 quantity=journal_entry.quantity,
#                 transaction_type="Journal",
#                 reference_document_type="StockJournal",
#                 reference_document=f"Journal {stock_journal.voucher_number}",
#                 remarks=f"Journal entry in {stock_journal.source_godown}",
#             )
#             self._log_transaction_effect(journal_transaction)

#     def _log_transaction_effect(self, transaction):
#         print(f"Transaction Effect Logged: {transaction.transaction_type} - {transaction.quantity} units at {transaction.godown}")


class StockJournalEntrySerializer(BaseModelSerializer):
    class Meta:
        model = StockJournalEntry
        fields = "__all__"


class CreateStockJournalSerializer(BaseModelSerializer):
    entries = StockJournalEntrySerializer(many=True, write_only=True)

    class Meta:
        model = StockJournal
        fields = "__all__"

    @transaction.atomic
    def create(self, validated_data):
        validated_data["auto_id"] = self._generate_auto_id(StockJournal)

        entries_data = validated_data.pop("entries", [])
        stock_journal = StockJournal.objects.create(**validated_data)

        for entry_data in entries_data:
            entry_data["auto_id"] = self._generate_auto_id(StockJournalEntry)
            StockJournalEntry.objects.create(journal=stock_journal, **entry_data)

        return stock_journal

    def _generate_auto_id(self, model_class):
        last_auto_id = model_class.objects.aggregate(max_id=Max("auto_id"))["max_id"]
        return (last_auto_id or 0) + 1

    def _create_inventory_transactions(self, journal_entry, stock_journal):
        if stock_journal.transaction_type == 0:  # Stock-Transfer
            # Outbound transaction from source godown
            outbound_transaction = InventoryTransaction.objects.create(
                organization_id=stock_journal.organization_id,
                item=journal_entry.item,
                unit=journal_entry.item.unit,
                godown=stock_journal.source_godown,
                quantity=-journal_entry.quantity,  # Negative for outbound
                transaction_type="Outbound",
                reference_document_type="StockJournal",
                reference_document=f"Journal {stock_journal.voucher_number}",
                remarks=f"Transfer from {stock_journal.source_godown} to {stock_journal.destination_godown}",
            )
            self._log_transaction_effect(outbound_transaction)

            # Inbound transaction to destination godown
            inbound_transaction = InventoryTransaction.objects.create(
                organization_id=stock_journal.organization_id,
                item=journal_entry.item,
                unit=journal_entry.item.unit,
                godown=stock_journal.destination_godown,
                quantity=journal_entry.quantity,  # Positive for inbound
                transaction_type="Inbound",
                reference_document_type="StockJournal",
                reference_document=f"Journal {stock_journal.voucher_number}",
                remarks=f"Transfer to {stock_journal.destination_godown} from {stock_journal.source_godown}",
            )
            self._log_transaction_effect(inbound_transaction)

        elif stock_journal.transaction_type == 1:  # Stock-Adjustment
            adjustment_transaction = InventoryTransaction.objects.create(
                organization_id=stock_journal.organization_id,
                item=journal_entry.item,
                unit=journal_entry.item.unit,
                godown=stock_journal.adjustment_godown,
                quantity=journal_entry.quantity,
                transaction_type="Adjustment",
                reference_document_type="StockJournal",
                reference_document=f"Journal {stock_journal.voucher_number}",
                remarks=f"Adjustment for {stock_journal.adjustment_godown}",
            )
            self._log_transaction_effect(adjustment_transaction)

        elif stock_journal.transaction_type == 2:  # Stock-Journal
            journal_transaction = InventoryTransaction.objects.create(
                organization_id=stock_journal.organization_id,
                item=journal_entry.item,
                unit=journal_entry.item.unit,
                godown=stock_journal.source_godown,
                quantity=journal_entry.quantity,
                transaction_type="Journal",
                reference_document_type="StockJournal",
                reference_document=f"Journal {stock_journal.voucher_number}",
                remarks=f"Journal entry in {stock_journal.source_godown}",
            )
            self._log_transaction_effect(journal_transaction)

    def _log_transaction_effect(self, transaction):
        print(
            f"Transaction Effect Logged: {transaction.transaction_type} - {transaction.quantity} units at {transaction.godown}"
        )


class StockJournalSerializer(BaseModelSerializer):
    entries = StockJournalEntrySerializer(many=True, read_only=True)

    class Meta:
        model = StockJournal
        fields = "__all__"


class StockJournalListEntryFullSerializer(BaseModelSerializer):
    item_name = serializers.SerializerMethodField()

    class Meta:
        model = StockJournalEntry
        fields = [
            "id",
            "item",
            "item_name",
            "quantity",
            "rate",
            "total_amount",
            "transaction_type",
            "current_quantity",
            "new_quantity",
        ]

    def get_item_name(self, obj):
        return obj.item.name if obj.item else None


class StockJournalFullListSerializer(BaseModelSerializer):
    entries = StockJournalListEntryFullSerializer(many=True, read_only=True)
    source_godown_name = serializers.SerializerMethodField()
    destination_godown_name = serializers.SerializerMethodField()
    adjustment_godown_name = serializers.SerializerMethodField()
    transaction_type_name = serializers.SerializerMethodField()

    class Meta:
        model = StockJournal
        fields = [
            "id",
            "voucher_number",
            "transaction_type",
            "source_branch",
            "destination_branch",
            "transaction_type_name",
            "source_godown",
            "source_godown_name",
            "destination_godown",
            "destination_godown_name",
            "adjustment_branch",
            "adjustment_godown",
            "adjustment_godown_name",
            "organization_id",
            "note",
            "entries",
        ]

    def get_source_godown_name(self, obj):
        return obj.source_godown.name if obj.source_godown else "none"

    def get_destination_godown_name(self, obj):
        return obj.destination_godown.name if obj.destination_godown else "none"

    def get_adjustment_godown_name(self, obj):
        return obj.adjustment_godown.name if obj.adjustment_godown else "none"

    def get_transaction_type_name(self, obj):
        transaction_type_dict = {
            0: "Stock-Transfer",
            1: "Stock-Adjustment",
            2: "Stock-Journal",
        }
        if obj.transaction_type is None:
            return "none"
        return transaction_type_dict.get(obj.transaction_type, "Unknown")
