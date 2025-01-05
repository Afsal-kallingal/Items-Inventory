from django.db import models, transaction
import uuid
from django.core.exceptions import ValidationError
from datetime import date
from django.utils.translation import gettext_lazy as _
from apps.main.models import BaseModel
from apps.item.models import StockItem, Godown, MeasurementUnit


class InventoryBaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date_added = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    creator = models.CharField(
        max_length=255, null=True, blank=True, help_text="ID of the user who created this entry"
    )
    updated_by = models.CharField(
        max_length=255, null=True, blank=True, help_text="ID of the user who last updated this entry"
    )
    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True


class FinancialYear(BaseModel):
    start_date = models.DateField()
    end_date = models.DateField()
    organization_id = models.UUIDField()

    def __str__(self):
        return f"Financial Year: {self.start_date} to {self.end_date}"

    class Meta:
        db_table = "financial_year"
        unique_together = ("organization_id", "start_date", "end_date")


class Openingstock(BaseModel):
    organization_id = models.UUIDField(null=True, blank=True)
    quantity = models.PositiveIntegerField(null=True, blank=True, default=0)
    stock_item = models.ForeignKey(
        StockItem, on_delete=models.CASCADE, null=True, blank=True, related_name="opening_balances"
    )
    rate = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True, default=0
    )
    amount = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True, default=0
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        
        return (
            f"{self.stock_item.name} - {self.quantity}"
            if self.stock_item
            else "Opening Balance"
        )

    class Meta:
        db_table = "Openingstock"
        # ordering = ["auto_id"]
        # verbose_name = "Opening stock"
        # verbose_name_plural = "Opening stock"



class StockReport(InventoryBaseModel):
    organization_id = models.UUIDField(
        null=True, blank=True, help_text="Unique identifier for the organization"
    )
    financial_year = models.ForeignKey(
        FinancialYear,
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name="stock_reports",
        help_text="Reference to the financial year",
    )
    item = models.ForeignKey(
        StockItem,
        on_delete=models.CASCADE,
        related_name="stock_item_reports",
        help_text="Reference to the stock item",
    )
    godown = models.ForeignKey(
        Godown,
        on_delete=models.CASCADE,
        null=True,
        related_name="stock_reports",
        help_text="Reference to the godown associated with the stock",
    )
    quantity = models.FloatField(default=0.0, help_text="Quantity of stock")
    received = models.IntegerField(default=0, help_text="Quantity of stock received")
    opening_balance = models.IntegerField(
        default=0, help_text="Opening balance of the stock"
    )
    closing_balance = models.IntegerField(
        default=0, help_text="Closing balance of the stock"
    )
    is_active = models.BooleanField(
        default=True, help_text="Indicates if the stock report is active"
    )

    def __str__(self):
        return f"Stock Report: {self.item} | FY: {self.financial_year}"

    class Meta:
        db_table = "stock_report"
        verbose_name = "Stock Report"
        verbose_name_plural = "Stock Reports"
        # ordering = ["-created_at"]


class InventoryTransaction(InventoryBaseModel):
    TRANSACTION_TYPE_CHOICES = [
        ("Inbound", "Inbound"),
        ("Outbound", "Outbound"),
        ("Transfer", "Transfer"),
        ("Adjustment", "Adjustment"),
    ]

    EVALUATION_METHOD_CHOICES = [
        ("10", "FIFO"),
        ("20", "LIFO"),
        ("30", "AVERAGE"),
    ]

    organization_id = models.UUIDField()
    item = models.ForeignKey(
        StockItem, on_delete=models.CASCADE, related_name="inventory_transactions"
    )
    unit = models.ForeignKey(
        MeasurementUnit, on_delete=models.CASCADE, related_name="inventory_transactions"
    )
    godown = models.ForeignKey(
        Godown, on_delete=models.CASCADE,null=True, blank=True, related_name="inventory_transactions"
    )
    quantity = models.IntegerField()
    transaction_type = models.CharField(
        max_length=20, choices=TRANSACTION_TYPE_CHOICES
    )
    evaluation_method = models.CharField(
        max_length=10, choices=EVALUATION_METHOD_CHOICES, default="10"
    )
    transaction_date = models.DateTimeField(auto_now_add=True)
    reference_document_type = models.CharField(max_length=255, null=True, blank=True)
    reference_document = models.CharField(max_length=255, null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)

    def clean(self):
        """Validate the model fields before saving."""
        if self.quantity <= 0:
            raise ValidationError("Quantity must be greater than zero.")
        if not self.organization_id:
            raise ValidationError("Organization ID is required.")
        if not self.item:
            raise ValidationError("Item is required.")
        if not self.transaction_type:
            raise ValidationError("Transaction type is required.")


    @transaction.atomic
    def save(self, *args, **kwargs):
        self.clean()

        stock_report, created = StockReport.objects.get_or_create(
            organization_id=self.organization_id,
            item=self.item,
            godown=self.godown,
            defaults={"opening_balance": 0, "closing_balance": 0},
        )
        if self.pk:
            previous_transaction = InventoryTransaction.objects.filter(pk=self.pk).first()
            if previous_transaction:
                if previous_transaction.transaction_type == "Inbound":
                    stock_report.closing_balance -= previous_transaction.quantity
                elif previous_transaction.transaction_type == "Outbound":
                    stock_report.closing_balance += previous_transaction.quantity
                    
        if self.transaction_type == "Inbound":
            stock_report.closing_balance += self.quantity
        elif self.transaction_type == "Outbound":
            stock_report.closing_balance -= self.quantity

        stock_report.save()
        super().save(*args, **kwargs)

    @transaction.atomic
    def delete(self, *args, **kwargs):
        stock_report = StockReport.objects.filter(
            organization_id=self.organization_id,
            item=self.item,
            godown=self.godown,
        ).first()

        if stock_report:
            if self.transaction_type == "Inbound":
                stock_report.closing_balance -= self.quantity
            elif self.transaction_type == "Outbound":
                stock_report.closing_balance += self.quantity
            stock_report.save()
        super().delete(*args, **kwargs)

    class Meta:
        db_table = "inventory_transaction"
        ordering = ["-transaction_date"]
        verbose_name = "Inventory Transaction"
        verbose_name_plural = "Inventory Transactions"


class StockJournal(BaseModel):
    
    voucher_number = models.CharField(
        max_length=15,
        null=True,
        blank=True,
        help_text="Voucher number for the stock journal",
    )
    transaction_type = models.IntegerField(
        choices=[(0, "Stock-Transfer"), (1, "Stock-Adjustment"),(2, "Stock-journal")],
        null=True,
        blank=True,
        help_text="Type of transaction: 0-Transfer, 1-Adjustment",
    )
    source_branch = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Source branch involved in the transaction",
    )
    destination_branch = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Destination branch involved in the transaction",
    )
    source_godown = models.ForeignKey(
        Godown,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="stock_journal_source_godown",
    )
    destination_godown = models.ForeignKey(
        Godown,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="stock_journal_destination_godown",
    )
    adjustment_branch = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Adjustment branch involved in the transaction",
    )
    adjustment_godown = models.ForeignKey(
        Godown,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="stock_journal_adjustment_godown",
    )
    organization_id = models.UUIDField(
        null=True, blank=True, help_text="Organization ID for this journal"
    )
    note = models.TextField(
        null=True, blank=True, help_text="Notes or remarks for this journal"
    )

    class Meta:
        db_table = "stock_journal"
        verbose_name = "Stock Journal"
        verbose_name_plural = "Stock Journals"
        ordering = ["-date_added"]

    def __str__(self):
        return f"Journal {self.voucher_number or 'Unnumbered'}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.handle_inventory_transactions()

    def handle_inventory_transactions(self):
        for entry in self.entries.all():
            entry.process_transaction()


class StockJournalEntry(BaseModel):
    journal = models.ForeignKey(
        StockJournal,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="entries",
        help_text="Reference to the journal",
    )
    item = models.ForeignKey(
        StockItem,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="stock_journal_items",
        help_text="Stock item involved in the transaction",
    )
    quantity = models.FloatField(
        null=True, blank=True, help_text="Quantity of the item involved"
    )
    rate = models.FloatField(
        null=True, blank=True, help_text="Rate of the item involved"
    )
    total_amount = models.FloatField(
        null=True, blank=True, help_text="Total amount calculated (rate * quantity)"
    )
    transaction_type = models.IntegerField(
        choices=[(0, "Destination"), (1, "Source"), (2, "Adjustment")],
        null=True,
        blank=True,
        help_text="Type of entry: Destination=0, Source=1, Adjustment=2",
    )
    current_quantity = models.FloatField(
        null=True, blank=True, help_text="Current quantity in stock before transaction"
    )
    new_quantity = models.FloatField(
        null=True, blank=True, help_text="New quantity after transaction"
    )

    class Meta:
        db_table = "stock_journal_entry"
        verbose_name = "Stock Journal Entry"
        verbose_name_plural = "Stock Journal Entries"
        ordering = ["-date_added"]

    def __str__(self):
        return f"Entry for {self.item.name if self.item else 'Unknown Item'}"
