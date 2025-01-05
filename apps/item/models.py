from django.db import models
from apps.main.models import BaseModel
from django.utils import timezone

# apps.inventory.
# from apps.inventory.models import Kitchen


class UQC(BaseModel):
    name = models.CharField(max_length=120, null=True, blank=True)
    code = models.CharField(max_length=110, null=True, blank=True)
    organization_id = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.code})" if self.code else self.name

    class Meta:
        db_table = "uqc"
        ordering = ["auto_id"]


class HsnSac(BaseModel):
    hsnsac_code = models.CharField(max_length=120)
    description = models.CharField(max_length=120, null=True, blank=True)
    organization_id = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.hsnsac_code

    class Meta:
        db_table = "hsn_sac"
        ordering = ["auto_id"]


class MeasurementUnit(BaseModel):
    UNIT_TYPE_CHOICES = [
        ("simple", "Simple"),
    ]

    name = models.CharField(max_length=50, null=True, blank=True)
    decimal_places = models.IntegerField(null=True, blank=True)
    organization_id = models.CharField(max_length=255, null=True, blank=True)
    uqc = models.ForeignKey(UQC, on_delete=models.CASCADE, null=True, blank=True)
    symbol = models.CharField(max_length=10, null=True, blank=True)
    # parent_unit = models.ForeignKey(
    #     "self",
    #     on_delete=models.CASCADE,
    #     null=True,
    #     blank=True,
    #     related_name="child_units",
    # )
    unit_type = models.CharField(
        max_length=50,
        choices=UNIT_TYPE_CHOICES,
        default="simple",
    )
    is_active = models.BooleanField(default=True, null=True, blank=True)
    is_primary_unit = models.BooleanField(default=False)

    def __str__(self):
        return str(self.name) if self.name else "Unnamed Unit"

    class Meta:
        db_table = "measurement_unit"


class StockGroup(BaseModel):
    name = models.CharField(max_length=120, null=True, blank=True)
    alias = models.CharField(max_length=120, null=True, blank=True)
    organization_id = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True, null=True, blank=True)
    is_primary_group = models.BooleanField(default=False)
    # related_group = models.ForeignKey(
    #     "self",
    #     on_delete=models.CASCADE,
    #     null=True,
    #     blank=True,
    #     related_name="related_stock_groups",
    # )
    parent_group = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="child_stock_groups",
    )

    def __str__(self):
        return str(self.name) if self.name else "Unnamed StockGroup"

    class Meta:
        db_table = "stock_group"


class ItemGroup(BaseModel):
    parent_group = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sub_groups",
    )
    group_name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.group_name

    class Meta:
        db_table = "item_groups"
        ordering = ["auto_id"]


class Tax(BaseModel):
    organization_id = models.CharField(max_length=255, null=True, blank=True)
    tax = models.IntegerField()

    def __str__(self):
        return str(self.tax)

    class Meta:
        db_table = "tax"


class StockClassification(BaseModel):
    name = models.CharField(max_length=120, null=True, blank=True)
    organization_id = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True, null=True, blank=True)
    is_primary_classification = models.BooleanField(default=False)

    def __str__(self):
        return str(self.name) if self.name else "Unnamed Stock Classification"

    class Meta:
        db_table = "category"


class Product(BaseModel):
    name = models.CharField(max_length=120, null=True, blank=True)
    category = models.ForeignKey(
        StockClassification,
        on_delete=models.CASCADE,
        related_name="products",
        null=True,
        blank=True,
    )
    organization_id = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True, null=True, blank=True)
    related_product = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="product_updates",
    )
    is_primary_stock_nature = models.BooleanField(default=False)

    def __str__(self):
        return str(self.name) if self.name else "Unnamed Product"

    class Meta:
        db_table = "product"


class Brand(BaseModel):
    name = models.CharField(max_length=120, null=True, blank=True)
    organization_id = models.CharField(max_length=255, null=True, blank=True)
    parent_brand = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="child_brands",
    )
    is_primary_brand = models.BooleanField(default=False)

    def __str__(self):
        return str(self.name) if self.name else "Unnamed Brand"

    class Meta:
        db_table = "brand"


class StockCategory(BaseModel):
    name = models.CharField(max_length=120, null=True, blank=True)
    alias = models.CharField(max_length=120, null=True, blank=True)
    # code = models.CharField(max_length=120, null=True, blank=True)
    # number = models.IntegerField(null=True, blank=True)
    organization_id = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True, null=True, blank=True)
    # related_category = models.ForeignKey(
    #     "self",
    #     on_delete=models.CASCADE,
    #     null=True,
    #     blank=True,
    #     related_name="stock_category_updates",
    # )
    parent_category = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="child_categories",
    )
    category_image = models.ImageField(upload_to="category", null=True, blank=True)
    is_primary_stock_category = models.BooleanField(default=False)

    def __str__(self):
        return str(self.name) if self.name else "Unnamed Stock Category"

    class Meta:
        db_table = "stock_category"


class Branch(BaseModel):
    name = models.CharField(max_length=255, null=True, blank=True)
    organization_id = models.UUIDField(null=True, blank=True)
    email = models.EmailField(max_length=255, null=True, blank=True)
    state_id = models.CharField(max_length=50, null=True, blank=True)
    contact_number = models.CharField(max_length=15, null=True, blank=True)
    stock_limit = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )  # Fixed
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )  # Fixed
    branch_type = models.PositiveSmallIntegerField(default=0, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    pincode = models.CharField(max_length=10, null=True, blank=True)
    timezone_id = models.CharField(max_length=120, null=True, blank=True)
    financial_year_start = models.DateField(null=True, blank=True)
    books_begin = models.DateField(null=True, blank=True)
    gstin = models.CharField(max_length=55, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    parent_branch = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="child_branches",
    )
    is_company_branch = models.BooleanField(default=False)
    country_id = models.CharField(max_length=120, null=True, blank=True)

    def __str__(self):
        return str(self.name) if self.name else "Unnamed Branch"

    class Meta:
        db_table = "branch"


class BranchHistory(BaseModel):
    # id = models.BigAutoField(primary_key=True)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name="history")
    name = models.CharField(max_length=255, null=True, blank=True)
    organization_id = models.UUIDField(null=True, blank=True)
    email = models.EmailField(max_length=255, null=True, blank=True)
    state_id = models.CharField(max_length=50, null=True, blank=True)
    contact_number = models.CharField(max_length=15, null=True, blank=True)
    stock_limit = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    latitude = models.CharField(max_length=55, null=True, blank=True)
    longitude = models.CharField(max_length=55, null=True, blank=True)
    branch_type = models.PositiveSmallIntegerField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    pincode = models.CharField(max_length=10, null=True, blank=True)
    timezone_id = models.CharField(max_length=120, null=True, blank=True)
    financial_year_start = models.DateField(null=True, blank=True)
    books_begin = models.DateField(null=True, blank=True)
    gstin = models.CharField(max_length=55, null=True, blank=True)
    is_active = models.BooleanField(null=True, blank=True)
    is_company_branch = models.BooleanField(null=True, blank=True)
    country_id = models.CharField(max_length=120, null=True, blank=True)
    modified_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"History of {self.branch.name} at {self.modified_at}"
            if self.branch and self.modified_at
            else "Branch History Record"
        )

    class Meta:
        db_table = "branch_history"
        ordering = ["-modified_at"]


class Godown(BaseModel):
    name = models.CharField(max_length=255, null=True, blank=True)
    organization_id = models.UUIDField(null=True, blank=True)
    email = models.EmailField(max_length=255, null=True, blank=True)
    state_id = models.CharField(max_length=50, null=True, blank=True)
    contact_number = models.CharField(max_length=55, null=True, blank=True)
    stock_limit = models.DecimalField(
        max_digits=55, decimal_places=2, null=True, blank=True
    )
    latitude = models.CharField(
        max_length=50, null=True, blank=True, help_text="Latitude as a string"
    )
    longitude = models.CharField(
        max_length=50, null=True, blank=True, help_text="Longitude as a string"
    )
    godown_type = models.PositiveSmallIntegerField(default=0, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    pincode = models.CharField(max_length=10, null=True, blank=True)
    timezone_id = models.CharField(max_length=100, null=True, blank=True)
    financial_year_start = models.DateField(null=True, blank=True)
    books_begin = models.DateField(null=True, blank=True)
    gstin = models.CharField(max_length=15, null=True, blank=True)
    status = models.PositiveSmallIntegerField(default=0, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    branch = models.CharField(max_length=100, null=True, blank=True)
    parent_godown = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="child_godowns",
    )
    country_id = models.CharField(max_length=100, null=True, blank=True)
    is_primary_godown = models.BooleanField(default=False)

    def __str__(self):
        return str(self.name) if self.name else "Unnamed Godown"

    class Meta:
        db_table = "godown"


class Rack(BaseModel):
    organization_id = models.UUIDField(null=True, blank=True)
    name = models.CharField(max_length=120, null=True, blank=True)
    godown = models.ForeignKey(
        Godown, on_delete=models.CASCADE, related_name="racks", null=True, blank=True
    )
    parent_rack = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="child_racks",
    )
    # related_rack = models.ForeignKey(
    #     "self",
    #     on_delete=models.CASCADE,
    #     null=True,
    #     blank=True,
    #     related_name="related_racks",
    # )
    is_active = models.BooleanField(default=True)
    is_primary_rack = models.BooleanField(default=False)

    def __str__(self):
        return str(self.name) if self.name else "Unnamed Rack"

    class Meta:
        db_table = "rack"


class AlternateUnits(BaseModel):
    organization_id = models.UUIDField(
        null=True, blank=True, help_text="Organization ID for this alternate unit"
    )
    alternative_unit = models.CharField(
        max_length=100, null=True, blank=True, help_text="Alternative unit name"
    )
    unit_value = models.ForeignKey(
        MeasurementUnit,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="alternate_unit_values",
        help_text="Reference to the unit value",
    )
    related_unit = models.ForeignKey(
        MeasurementUnit,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="alternate_related_units",
        help_text="Reference to the related unit value",
    )
    related_unit_values = models.CharField(max_length=100, null=True, blank=True)
    cost_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Cost price for the alternate unit",
    )
    selling_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Selling price for the alternate unit",
    )
    barcode = models.CharField(
        max_length=300,
        null=True,
        blank=True,
        help_text="Barcode for the alternate unit",
    )

    def __str__(self):
        return (
            f"Alternate Unit: {self.alternative_unit}"
            if self.alternative_unit
            else "Alternate Unit"
        )

    class Meta:
        db_table = "alternate_units"
        verbose_name = "Alternate Unit"
        verbose_name_plural = "Alternate Units"


class Kitchen(BaseModel):
    organization_id = models.UUIDField(null=True, blank=True)
    branch = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name}"


class StockItem(BaseModel):
    ITEM_TYPE_CHOICES = [
        ("Asset", "Asset"),
        ("Stock", "Stock"),
        ("Non-inventory", "Non-inventory"),
    ]
    GST_TYPE_CHOICES = [
        ("item_rate", "On Item Rate"),
        ("value", "On Value"),
    ]
    MRP_TYPE_CHOICES = [
        ("applicable", "Applicable"),
        ("not_applicable", "Not Applicable"),
    ]
    SUPPLY_TYPE_CHOICES = [
        ("goods", "Goods"),
        ("service", "Service"),
    ]

    organization_id = models.UUIDField(null=True, blank=True)
    name = models.CharField(
        max_length=255, null=True, blank=True, help_text="Name of the item"
    )
    alias = models.CharField(
        max_length=120, null=True, blank=True, help_text="Alias for the item"
    )
    godown = models.ForeignKey(
        Godown,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="godown_items",
    )
    stock_category = models.ForeignKey(
        StockCategory,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="category_items",
    )
    stock_group = models.ForeignKey(
        StockGroup,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="group_items",
    )
    brand = models.ForeignKey(
        Brand, on_delete=models.CASCADE, null=True, blank=True, related_name="items"
    )
    unit = models.ForeignKey(
        MeasurementUnit,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="unit_items",
    )
    alternative_unit = models.BooleanField(
        default=False, help_text="Is there an alternative unit?"
    )
    description = models.TextField(
        null=True, blank=True, help_text="Description of the item"
    )
    stock_nature = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stock_nature_items",
    )
    aditional_details = models.BooleanField(default=False, null=True, blank=True)
    item_type = models.CharField(
        max_length=50,
        choices=ITEM_TYPE_CHOICES,
        default="Stock",
        help_text="Type of the item",
    )
    batch_number_enabled = models.BooleanField(
        default=False, help_text="Enable batch numbers for this item?"
    )
    manufacturing_date = models.DateField(
        null=True, blank=True, help_text="Manufacturing date of the item"
    )
    expiry_date = models.DateField(
        null=True, blank=True, help_text="Expiry date of the item"
    )
    gst_applicable = models.BooleanField(default=False, help_text="Is GST applicable?")
    hsn_sac = models.ForeignKey(
        HsnSac, on_delete=models.CASCADE, null=True, blank=True, related_name="items"
    )
    gst_type = models.CharField(
        max_length=50,
        choices=GST_TYPE_CHOICES,
        null=True,
        blank=True,
        default="item_rate",
        help_text="GST type applicable",
    )
    supply_type = models.CharField(
        max_length=50,
        choices=SUPPLY_TYPE_CHOICES,
        null=True,
        blank=True,
        default="goods",
        help_text="Supply type",
    )
    tax = models.ForeignKey(
        Tax, on_delete=models.SET_NULL, null=True, blank=True, related_name="items"
    )
    mrp_type = models.CharField(
        max_length=50,
        choices=MRP_TYPE_CHOICES,
        null=True,
        blank=True,
        help_text="MRP applicability",
    )
    standard_rate = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Standard rate of the item",
    )
    selling_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Selling price of the item",
    )
    cost_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Cost price of the item",
    )
    min_order_quantity = models.PositiveIntegerField(
        default=1, help_text="Minimum order quantity for the item"
    )
    reorder_level = models.PositiveIntegerField(
        null=True, blank=True, help_text="Reorder level for the item"
    )
    notes = models.TextField(
        null=True, blank=True, help_text="Additional notes for the item"
    )
    item_code = models.CharField(
        max_length=120,
        # unique=True,
        null=True,
        blank=True,
        help_text="Unique code for the item",
    )
    barcode = models.CharField(
        max_length=300,
        null=True,
        blank=True,
        unique=True,
        help_text="Barcode for the item",
    )
    secondary_language_name = models.CharField(
        max_length=125,
        null=True,
        blank=True,
        help_text="Secondary language name for the item",
    )
    image = models.ImageField(
        upload_to="item_images", null=True, blank=True, help_text="Image of the item"
    )
    alternative_units = models.ManyToManyField(
        AlternateUnits,
        blank=True,
        related_name="stock_items_units",
    )
    application_date = models.DateField(
        null=True, blank=True, help_text="Date of application."
    )
    alter_gst_details = models.BooleanField(
        default=False,
        null=True,
        blank=True,
        help_text="Whether GST details were altered.",
    )
    kitchen = models.ForeignKey(
        Kitchen, models.CASCADE, null=True, blank=True, related_name="items_kitchen"
    )
    selling_price_applicable_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date when the selling price becomes applicable",
    )
    cost_price_applicable_date = models.DateField(
        null=True, blank=True, help_text="Date when the cost price becomes applicable"
    )
    mrp_applicable_date = models.DateField(
        null=True, blank=True, help_text="Date when the MRP becomes applicable"
    )

    def __str__(self):
        return str(self.name) if self.name else f"Item {self.id}"

    class Meta:
        db_table = "stock_item"
        ordering = ["name"]


# class StockItemHistory(models.Model):
#     id = models.BigAutoField(primary_key=True)
#     item = models.ForeignKey(
#         StockItem,
#         on_delete=models.CASCADE,
#         related_name="history",
#         help_text="Reference to the stock item this history belongs to",
#     )
#     organization_id = models.UUIDField(
#         null=True, blank=True, help_text="Organization ID"
#     )
#     name = models.CharField(
#         max_length=255, null=True, blank=True, help_text="Name of the item"
#     )
#     alias = models.CharField(
#         max_length=120, null=True, blank=True, help_text="Alias of the item"
#     )
#     description = models.TextField(
#         null=True, blank=True, help_text="Description of the item"
#     )
#     item_type = models.CharField(
#         max_length=50, null=True, blank=True, help_text="Type of the item"
#     )
#     stock_category = models.ForeignKey(
#         StockCategory, on_delete=models.SET_NULL, null=True, blank=True
#     )
#     stock_group = models.ForeignKey(
#         StockGroup, on_delete=models.SET_NULL, null=True, blank=True
#     )
#     brand = models.ForeignKey("Brand", on_delete=models.SET_NULL, null=True, blank=True)
#     unit = models.ForeignKey(
#         MeasurementUnit, on_delete=models.SET_NULL, null=True, blank=True
#     )
#     alternative_unit = models.BooleanField(default=False)
#     stock_nature = models.ForeignKey(
#         Product, on_delete=models.SET_NULL, null=True, blank=True
#     )
#     standard_rate = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         null=True,
#         blank=True,
#         help_text="Standard rate",
#     )
#     selling_price = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         null=True,
#         blank=True,
#         help_text="Selling price",
#     )
#     cost_price = models.DecimalField(
#         max_digits=12, decimal_places=2, null=True, blank=True, help_text="Cost price"
#     )
#     min_order_quantity = models.PositiveIntegerField(
#         default=1, help_text="Min order quantity"
#     )
#     reorder_level = models.PositiveIntegerField(
#         null=True, blank=True, help_text="Reorder level"
#     )
#     batch_number_enabled = models.BooleanField(default=False)
#     manufacturing_date = models.DateField(null=True, blank=True)
#     expiry_date = models.DateField(null=True, blank=True)
#     gst_applicable = models.BooleanField(default=False)
#     hsn_sac = models.ForeignKey(
#         HsnSac, on_delete=models.SET_NULL, null=True, blank=True
#     )
#     gst_type = models.CharField(max_length=50, null=True, blank=True)
#     supply_type = models.CharField(max_length=50, null=True, blank=True)
#     tax = models.ForeignKey("Tax", on_delete=models.SET_NULL, null=True, blank=True)
#     mrp_type = models.CharField(max_length=50, null=True, blank=True)
#     mrp_applicable_date = models.DateField(null=True, blank=True)
#     selling_price_applicable_date = models.DateField(null=True, blank=True)
#     cost_price_applicable_date = models.DateField(null=True, blank=True)
#     barcode = models.CharField(max_length=300, null=True, blank=True)
#     item_code = models.CharField(max_length=120, null=True, blank=True)
#     secondary_language_name = models.CharField(max_length=125, null=True, blank=True)
#     image = models.ImageField(
#         upload_to="item_images/history", null=True, blank=True, help_text="Item image"
#     )
#     alternative_units = models.ManyToManyField(
#         AlternateUnits, blank=True, related_name="history_alternate_units"
#     )
#     application_date = models.DateField(null=True, blank=True)
#     alter_gst_details = models.BooleanField(default=False)
#     kitchen = models.ForeignKey(
#         Kitchen, on_delete=models.CASCADE, null=True, blank=True
#     )
#     notes = models.TextField(null=True, blank=True, help_text="Additional notes")
#     modified_at = models.DateTimeField(
#         default=timezone.now, help_text="Timestamp of the change"
#     )

#     class Meta:
#         db_table = "stock_item_history"
#         verbose_name = "Stock Item History"
#         verbose_name_plural = "Stock Item Histories"
#         ordering = ["-modified_at"]

#     def __str__(self):
#         return f"History of {self.item.name if self.item else 'Unknown Item'} on {self.modified_at}"


class BarcodeDetails(BaseModel):
    organization_id = models.UUIDField(null=True, blank=True)
    include_selling_price = models.BooleanField(default=False)
    include_company_name = models.BooleanField(default=False)
    include_barcode = models.BooleanField(default=False)
    include_item_name = models.BooleanField(default=False)
    include_mrp = models.BooleanField(default=False)
    include_item_code = models.BooleanField(default=False)

    def __str__(self):
        return (
            f"Barcode Details for {self.company.name}"
            if self.company
            else "Barcode Details"
        )

    class Meta:
        db_table = "barcode_details"


class RawMaterial(BaseModel):
    organization_id = models.UUIDField(null=True, blank=True)
    item = models.ForeignKey(
        StockItem,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="raw_materials_main",
    )
    raw_material = models.ForeignKey(
        StockItem,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="raw_materials",
    )
    manufacture_date = models.DateField(null=True, blank=True)
    quantity = models.FloatField(null=True, blank=True)
    unit = models.ForeignKey(
        MeasurementUnit,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="raw_material_units",
    )
    is_active = models.BooleanField(default=True, null=True, blank=True)

    def __str__(self):
        return f"{self.item} - {self.raw_material}"

    class Meta:
        db_table = "raw_materials"
        verbose_name = "Raw Material"
        verbose_name_plural = "Raw Materials"
        ordering = ["auto_id"]
