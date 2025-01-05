from apps.main.serializers import BaseModelSerializer
from rest_framework import serializers
from django.db import transaction, models
from django.utils import timezone
from datetime import datetime, date
from django.db.models import Max
from django.core.exceptions import ValidationError
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
    # StockItemHistory,
    BranchHistory,
    Kitchen,
)
from apps.inventory.models import (
    Openingstock,
    StockReport,
)


class UQCSerializer(BaseModelSerializer):
    class Meta:
        model = UQC
        fields = "__all__"
        read_only_fields = [
            "id",
            "auto_id",
            "date_added",
            "creator",
            "updated_at",
            "updated_by",
        ]

    def validate_name(self, value):
        if value and len(value) > 120:
            raise serializers.ValidationError("Name cannot exceed 120 characters.")
        return value

    # def validate_organization_id(self, value):
    #     if not value:
    #         raise serializers.ValidationError("Organization ID is required.")
    #     return value

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.code = validated_data.get("code", instance.code)
        instance.organization_id = validated_data.get(
            "organization_id", instance.organization_id
        )
        instance.save()
        return instance


class HsnSacSerializer(BaseModelSerializer):
    class Meta:
        model = HsnSac
        fields = "__all__"
        read_only_fields = [
            "id",
            "auto_id",
            "date_added",
            "creator",
            "updated_at",
            "updated_by",
        ]

    def validate_hsnsac_code(self, value):
        if not value:
            raise serializers.ValidationError("HSN/SAC code is required.")
        if len(value) > 120:
            raise serializers.ValidationError(
                "HSN/SAC code cannot exceed 120 characters."
            )
        return value

    def validate_organization_id(self, value):
        if not value:
            raise serializers.ValidationError("Organization ID is required.")
        return value

    def update(self, instance, validated_data):
        instance.hsnsac_code = validated_data.get("hsnsac_code", instance.hsnsac_code)
        instance.description = validated_data.get("description", instance.description)
        instance.organization_id = validated_data.get(
            "organization_id", instance.organization_id
        )
        instance.save()
        return instance


class MeasurementUnitSerializer(BaseModelSerializer):
    class Meta:
        model = MeasurementUnit
        fields = [
            "id",
            "auto_id",
            "date_added",
            "creator",
            "updated_at",
            "updated_by",
            "name",
            "decimal_places",
            "organization_id",
            "uqc",
            "symbol",
            "unit_type",
            "is_active",
            "is_primary_unit",
        ]
        read_only_fields = [
            "id",
            "auto_id",
            "date_added",
            "creator",
            "updated_at",
            "updated_by",
        ]

    def validate_name(self, value):
        if value and len(value) > 50:  # Enforces max_length consistency with the model
            raise serializers.ValidationError("Name cannot exceed 50 characters.")
        return value

    def validate_organization_id(self, value):
        if not value:
            raise serializers.ValidationError("Organization ID is required.")
        return value

    def validate_decimal_places(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("Decimal places cannot be negative.")
        return value

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.decimal_places = validated_data.get(
            "decimal_places", instance.decimal_places
        )
        instance.organization_id = validated_data.get(
            "organization_id", instance.organization_id
        )
        instance.uqc = validated_data.get("uqc", instance.uqc)
        instance.symbol = validated_data.get("symbol", instance.symbol)
        # instance.parent_unit = validated_data.get("parent_unit", instance.parent_unit)
        instance.unit_type = validated_data.get("unit_type", instance.unit_type)
        instance.is_active = validated_data.get("is_active", instance.is_active)
        instance.save()
        return instance


# class StockGroupTreeSerializer(BaseModelSerializer):
#     children = serializers.SerializerMethodField()

#     class Meta:
#         model = StockGroup
#         fields = [
#             "id",
#             "name",
#             "alias",
#             "organization_id",
#             "is_active",
#             "parent_group",
#             "children",
#         ]

#     def get_children(self, obj):
#         children = obj.child_stock_groups.all()
#         return StockGroupTreeSerializer(children, many=True).data


class StockGroupTreeSerializer(BaseModelSerializer):
    children = serializers.SerializerMethodField()
    parent_group_name = serializers.SerializerMethodField()

    class Meta:
        model = StockGroup
        fields = [
            "id",
            "name",
            "alias",
            "organization_id",
            "is_active",
            "parent_group",
            "parent_group_name",
            "children",
        ]

    def get_children(self, obj):
        children = obj.child_stock_groups.all()
        return StockGroupTreeSerializer(children, many=True).data

    def get_parent_group_name(self, obj):
        return obj.parent_group.name if obj.parent_group else None


class StockGroupSerializer(BaseModelSerializer):
    class Meta:
        model = StockGroup
        fields = [
            "id",
            "date_added",
            "creator",
            "updated_at",
            "updated_by",
            "name",
            "alias",
            "organization_id",
            "is_active",
            "parent_group",
            "is_primary_group",
        ]
        read_only_fields = [
            "id",
            "date_added",
            "creator",
            "updated_at",
            "updated_by",
        ]

    def validate_parent_group(self, value):
        if value and self.instance and value.id == self.instance.id:
            raise serializers.ValidationError("A group cannot be its own parent.")

        current = value
        while current:
            if current == self.instance:
                raise serializers.ValidationError(
                    "Circular reference detected in parent group."
                )
            current = current.parent_group
        return value


class TaxSerializer(BaseModelSerializer):
    class Meta:
        model = Tax
        fields = "__all__"
        read_only_fields = [
            "id",
            "auto_id",
            "date_added",
            "creator",
            "updated_at",
            "updated_by",
        ]

    def validate_tax(self, value):
        if value < 0:
            raise serializers.ValidationError("Tax value cannot be negative.")
        return value


class StockClassificationSerializer(BaseModelSerializer):
    class Meta:
        model = StockClassification
        fields = "__all__"
        read_only_fields = [
            "id",
            "auto_id",
            "date_added",
            "creator",
            "updated_at",
            "updated_by",
        ]

    def validate_name(self, value):
        if (
            value and len(value) > 120
        ):  # Ensures validation matches the model's `max_length`
            raise serializers.ValidationError("Name cannot exceed 120 characters.")
        return value

    def validate_organization_id(self, value):
        if not value:
            raise serializers.ValidationError("Organization ID is required.")
        return value


class ProductSerializer(BaseModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"
        read_only_fields = [
            "id",
            "auto_id",
            "date_added",
            "creator",
            "updated_at",
            "updated_by",
        ]

    def validate_name(self, value):
        if (
            value and len(value) > 120
        ):  # Ensures validation aligns with the model's `max_length`
            raise serializers.ValidationError("Name cannot exceed 120 characters.")
        return value

    def validate_organization_id(self, value):
        if not value:
            raise serializers.ValidationError("Organization ID is required.")
        return value

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.category = validated_data.get("category", instance.category)
        instance.organization_id = validated_data.get(
            "organization_id", instance.organization_id
        )
        instance.is_active = validated_data.get("is_active", instance.is_active)
        instance.related_product = validated_data.get(
            "related_product", instance.related_product
        )
        instance.save()
        return instance


class BrandSerializer(BaseModelSerializer):
    class Meta:
        model = Brand
        fields = "__all__"
        read_only_fields = [
            "id",
            "auto_id",
            "date_added",
            "creator",
            "updated_at",
            "updated_by",
        ]

    def validate_name(self, value):
        if (
            value and len(value) > 120
        ):  # Ensures validation adheres to the model's `max_length`
            raise serializers.ValidationError("Name cannot exceed 120 characters.")
        return value

    def validate_organization_id(self, value):
        if not value:
            raise serializers.ValidationError("Organization ID is required.")
        return value

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.organization_id = validated_data.get(
            "organization_id", instance.organization_id
        )
        instance.parent_brand = validated_data.get(
            "parent_brand", instance.parent_brand
        )
        instance.save()
        return instance


class StockCategorySerializer(BaseModelSerializer):
    class Meta:
        model = StockCategory
        fields = [
            "id",
            "auto_id",
            "date_added",
            "creator",
            "updated_at",
            "updated_by",
            "name",
            "alias",
            "organization_id",
            "is_active",
            "parent_category",
            "category_image",
            "is_primary_stock_category",
        ]
        read_only_fields = [
            "id",
            "auto_id",
            "date_added",
            "creator",
            "updated_at",
            "updated_by",
        ]

    def validate_name(self, value):
        if (
            value and len(value) > 120
        ):  # Ensures validation matches the model's `max_length`
            raise serializers.ValidationError("Name cannot exceed 120 characters.")
        return value

    def validate_parent_category(self, value):
        if value and self.instance and value.id == self.instance.id:
            raise serializers.ValidationError("A category cannot be its own parent.")

        current = value
        while current:
            if current == self.instance:
                raise serializers.ValidationError(
                    "Circular reference detected in parent category."
                )
            current = current.parent_category
        return value

    def validate(self, data):
        if "organization_id" not in data or not data.get("organization_id"):
            raise serializers.ValidationError(
                {"organization_id": "Organization ID is required."}
            )
        return data

    def update(self, instance, validated_data):
        new_parent = validated_data.get("parent_category", instance.parent_category)

        if new_parent:
            if new_parent.id == instance.id:
                raise serializers.ValidationError(
                    {"parent_category": "A category cannot be its own parent."}
                )

            parent = new_parent
            while parent:
                if parent.id == instance.id:
                    raise serializers.ValidationError(
                        {
                            "parent_category": "Circular reference detected in parent category."
                        }
                    )
                parent = parent.parent_category

        for field in [
            "name",
            "alias",
            "organization_id",
            "is_active",
            "parent_category",
            "category_image",
        ]:
            if field in validated_data:
                setattr(instance, field, validated_data[field])

        instance.save()
        return instance


class StockCategoryListSerializer(BaseModelSerializer):
    parent_category_name = serializers.SerializerMethodField()

    class Meta:
        model = StockCategory
        fields = [
            "id",
            "name",
            "alias",
            "organization_id",
            "is_active",
            "parent_category",
            "parent_category_name",
            "category_image",
        ]

    def get_parent_category_name(self, obj):
        if obj.parent_category:
            return obj.parent_category.name
        return None


class StockCategoryTreeSerializer(BaseModelSerializer):
    children = serializers.SerializerMethodField()
    parent_category_name = serializers.SerializerMethodField()

    class Meta:
        model = StockCategory
        fields = [
            "id",
            "auto_id",
            "name",
            "alias",
            "organization_id",
            "is_active",
            "parent_category",
            "parent_category_name",
            "category_image",
            "children",
        ]
        read_only_fields = [
            "id",
            "auto_id",
            "date_added",
            "creator",
            "updated_at",
            "updated_by",
        ]

    def get_children(self, obj):
        children = obj.child_categories.all()
        return StockCategoryTreeSerializer(children, many=True).data

    def get_parent_category_name(self, obj):
        if obj.parent_category:
            return obj.parent_category.name
        return None


class BranchSerializer(BaseModelSerializer):
    class Meta:
        model = Branch
        fields = "__all__"
        read_only_fields = [
            "id",
            "auto_id",
            "date_added",
            "creator",
            "updated_at",
            "updated_by",
        ]

    def validate_name(self, value):
        if value and len(value) > 255:
            raise serializers.ValidationError("Name cannot exceed 255 characters.")
        return value

    def validate_contact_number(self, value):
        if value and not value.isdigit():
            raise serializers.ValidationError(
                "Contact number must contain only digits."
            )
        if value and len(value) > 15:
            raise serializers.ValidationError(
                "Contact number cannot exceed 15 characters."
            )
        return value

    def validate_organization_id(self, value):
        if not value:
            raise serializers.ValidationError("Organization ID is required.")
        return value

    def validate_pincode(self, value):
        if value and not value.isdigit():
            raise serializers.ValidationError("Pincode must contain only digits.")
        if value and len(value) > 10:
            raise serializers.ValidationError("Pincode cannot exceed 10 characters.")
        return value

    def update(self, instance, validated_data):
        BranchHistory.objects.create(
            branch=instance,
            name=instance.name,
            organization_id=instance.organization_id,
            email=instance.email,
            state_id=instance.state_id,
            contact_number=instance.contact_number,
            stock_limit=instance.stock_limit,
            latitude=instance.latitude,
            longitude=instance.longitude,
            branch_type=instance.branch_type,
            address=instance.address,
            pincode=instance.pincode,
            timezone_id=instance.timezone_id,
            financial_year_start=instance.financial_year_start,
            books_begin=instance.books_begin,
            gstin=instance.gstin,
            is_active=instance.is_active,
            is_company_branch=instance.is_company_branch,
            country_id=instance.country_id,
            modified_at=datetime.now(),
        )

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance


class GodownSerializer(BaseModelSerializer):
    class Meta:
        model = Godown
        fields = "__all__"
        read_only_fields = [
            "id",
            "auto_id",
            "date_added",
            "creator",
            "updated_at",
            "updated_by",
        ]

    def validate_name(self, value):
        if value and len(value) > 255:
            raise serializers.ValidationError("Name cannot exceed 255 characters.")
        return value

    def validate_contact_number(self, value):
        if value and not value.isdigit():
            raise serializers.ValidationError(
                "Contact number must contain only digits."
            )
        if value and len(value) > 55:
            raise serializers.ValidationError(
                "Contact number cannot exceed 55 characters."
            )
        return value

    def validate_organization_id(self, value):
        if not value:
            raise serializers.ValidationError("Organization ID is required.")
        return value

    def validate_pincode(self, value):
        if value and not value.isdigit():
            raise serializers.ValidationError("Pincode must contain only digits.")
        if value and len(value) > 10:
            raise serializers.ValidationError("Pincode cannot exceed 10 characters.")
        return value

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.organization_id = validated_data.get(
            "organization_id", instance.organization_id
        )
        instance.email = validated_data.get("email", instance.email)
        instance.state_id = validated_data.get("state_id", instance.state_id)
        instance.contact_number = validated_data.get(
            "contact_number", instance.contact_number
        )
        instance.stock_limit = validated_data.get("stock_limit", instance.stock_limit)
        instance.latitude = validated_data.get("latitude", instance.latitude)
        instance.longitude = validated_data.get("longitude", instance.longitude)
        instance.godown_type = validated_data.get("godown_type", instance.godown_type)
        instance.address = validated_data.get("address", instance.address)
        instance.pincode = validated_data.get("pincode", instance.pincode)
        instance.timezone_id = validated_data.get("timezone_id", instance.timezone_id)
        instance.financial_year_start = validated_data.get(
            "financial_year_start", instance.financial_year_start
        )
        instance.books_begin = validated_data.get("books_begin", instance.books_begin)
        instance.gstin = validated_data.get("gstin", instance.gstin)
        instance.status = validated_data.get("status", instance.status)
        instance.is_active = validated_data.get("is_active", instance.is_active)
        instance.branch = validated_data.get("branch", instance.branch)
        instance.parent_godown = validated_data.get(
            "parent_godown", instance.parent_godown
        )
        instance.country_id = validated_data.get("country_id", instance.country_id)
        instance.save()
        return instance


class RackTreeSerializer(BaseModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Rack
        fields = [
            "id",
            "name",
            "organization_id",
            "godown",
            "parent_rack",
            "is_active",
            "children",
        ]

    def get_children(self, obj):
        children = obj.child_racks.all()
        return RackTreeSerializer(children, many=True).data


class RackSerializer(BaseModelSerializer):
    class Meta:
        model = Rack
        fields = [
            "id",
            "name",
            "godown",
            "organization_id",
            "is_active",
            "parent_rack",
            "is_primary_rack",
            "auto_id",
            "date_added",
            "creator",
            "updated_at",
            "updated_by",
        ]
        read_only_fields = [
            "id",
            "auto_id",
            "date_added",
            "creator",
            "updated_at",
            "updated_by",
        ]

    def validate_name(self, value):
        if value and len(value) > 120:
            raise serializers.ValidationError("Name cannot exceed 120 characters.")
        return value

    def validate_organization_id(self, value):
        if not value:
            raise serializers.ValidationError("Organization ID is required.")
        return value

    def validate_parent_rack(self, value):
        if value and self.instance and value.id == self.instance.id:
            raise serializers.ValidationError("A rack cannot be its own parent.")

        current = value
        while current:
            if current == self.instance:
                raise serializers.ValidationError(
                    "Circular reference detected in parent rack."
                )
            current = current.parent_rack
        return value


class RackNameListSerializer(BaseModelSerializer):
    class Meta:
        model = Rack
        fields = ["id", "name", "is_primary_rack"]


class ItemGroupSerializer(BaseModelSerializer):
    class Meta:
        model = ItemGroup
        fields = [
            "id",
            "parent_group",
            "group_name",
            "description",
            "auto_id",
            "date_added",
            "creator",
            "updated_at",
            "updated_by",
        ]
        read_only_fields = [
            "id",
            "auto_id",
            "date_added",
            "creator",
            "updated_at",
            "updated_by",
        ]

    def validate_group_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Group name cannot be empty.")
        if len(value) > 255:
            raise serializers.ValidationError(
                "Group name cannot exceed 255 characters."
            )
        return value.strip()

    def validate_parent_group(self, value):
        if value and self.instance and value.id == self.instance.id:
            raise serializers.ValidationError("A group cannot be its own parent.")
        return value

    def update(self, instance, validated_data):
        if "group_name" in validated_data:
            validated_data["group_name"] = validated_data["group_name"].strip()
        instance.parent_group = validated_data.get(
            "parent_group", instance.parent_group
        )
        instance.group_name = validated_data.get("group_name", instance.group_name)
        instance.description = validated_data.get("description", instance.description)
        return super().update(instance, validated_data)


class ItemSerializer(BaseModelSerializer):
    class Meta:
        model = StockItem
        fields = "__all__"
        read_only_fields = [
            "id",
            "auto_id",
            "date_added",
            "creator",
            "updated_at",
            "updated_by",
        ]


class AlternateUnitsSerializer(BaseModelSerializer):
    class Meta:
        model = AlternateUnits
        fields = "__all__"
        read_only_fields = [
            "id",
            "auto_id",
            "date_added",
            "creator",
            "updated_at",
            "updated_by",
        ]


class OpeningstockSerializerStockItem(BaseModelSerializer):
    class Meta:
        model = Openingstock
        # fields = [
        #     "organization_id",
        #     "quantity",
        #     "rate",
        #     "amount",
        #     "is_active",
        # ]
        fields = "__all__"
        read_only_fields = [
            "id",
            "auto_id",
            "date_added",
            "creator",
            "updated_at",
            "updated_by",
        ]


class CreateStockItemSerializer(BaseModelSerializer):
    alternative_units = AlternateUnitsSerializer(many=True, required=False)
    opening_stock = OpeningstockSerializerStockItem(required=False)

    class Meta:
        model = StockItem
        fields = [
            "id",
            "organization_id",
            "name",
            "alias",
            "stock_category",
            "stock_group",
            "godown",
            "brand",
            "unit",
            "alternative_unit",
            "description",
            "stock_nature",
            "item_type",
            "batch_number_enabled",
            "manufacturing_date",
            "expiry_date",
            "gst_applicable",
            "aditional_details",
            "hsn_sac",
            "gst_type",
            "supply_type",
            "tax",
            "mrp_type",
            "standard_rate",
            "selling_price",
            "cost_price",
            "min_order_quantity",
            "reorder_level",
            "notes",
            "item_code",
            "barcode",
            "secondary_language_name",
            "image",
            "alternative_units",
            "opening_stock",
            "application_date",
            "alter_gst_details",
            "kitchen",
            "selling_price_applicable_date",
            "cost_price_applicable_date",
            "mrp_applicable_date",
        ]
        read_only_fields = [
            "id",
            "auto_id",
            "date_added",
            "creator",
            "updated_at",
            "updated_by",
        ]

    @transaction.atomic
    def create(self, validated_data):
        alternative_units_data = validated_data.pop("alternative_units", [])
        opening_stock_data = validated_data.pop("opening_stock", None)

        print(f"Validated Data: {validated_data}")
        print(f"Opening Stock Data: {opening_stock_data}")

        validated_data["auto_id"] = self._generate_auto_id()
        stock_item = StockItem.objects.create(**validated_data)

        if alternative_units_data:
            alternative_units = []
            for unit_data in alternative_units_data:
                unit_data["auto_id"] = self._generate_auto_id_for_alternate_units()
                alternative_unit = AlternateUnits.objects.create(**unit_data)
                alternative_units.append(alternative_unit)
            stock_item.alternative_units.add(*alternative_units)

        if opening_stock_data:
            print("Creating Opening Stock....")
            try:
                opening_stock_data["auto_id"] = (
                    self._generate_auto_id_for_opening_stock()
                )
                Openingstock.objects.create(stock_item=stock_item, **opening_stock_data)
            except Exception as e:
                raise serializers.ValidationError({"opening_stock": f"Error: {str(e)}"})

        return stock_item

    def _generate_auto_id(self):
        last_auto_id = StockItem.objects.aggregate(max_id=models.Max("auto_id"))[
            "max_id"
        ]
        return (last_auto_id or 0) + 1

    def _generate_auto_id_for_alternate_units(self):
        last_auto_id = AlternateUnits.objects.aggregate(max_id=models.Max("auto_id"))[
            "max_id"
        ]
        return (last_auto_id or 0) + 1

    def _generate_auto_id_for_opening_stock(self):
        last_auto_id = Openingstock.objects.aggregate(max_id=models.Max("auto_id"))[
            "max_id"
        ]
        return (last_auto_id or 0) + 1


class UpdateStockItemSerializer(BaseModelSerializer):
    alternative_units = AlternateUnitsSerializer(many=True, required=False)
    opening_stock = OpeningstockSerializerStockItem(required=False)

    class Meta:
        model = StockItem
        fields = [
            "id",
            "organization_id",
            "name",
            "alias",
            "stock_category",
            "stock_group",
            "brand",
            "unit",
            "alternative_unit",
            "description",
            "stock_nature",
            "item_type",
            "batch_number_enabled",
            "manufacturing_date",
            "expiry_date",
            "gst_applicable",
            "aditional_details",
            "hsn_sac",
            "gst_type",
            "godown",
            "supply_type",
            "tax",
            "mrp_type",
            "standard_rate",
            "selling_price",
            "cost_price",
            "min_order_quantity",
            "reorder_level",
            "notes",
            "item_code",
            "barcode",
            "secondary_language_name",
            "image",
            "alternative_units",
            "opening_stock",
            "application_date",
            "alter_gst_details",
            "kitchen",
            "selling_price_applicable_date",
            "cost_price_applicable_date",
            "mrp_applicable_date",
        ]
        read_only_fields = [
            "id",
            "auto_id",
            "date_added",
            "creator",
            "updated_at",
            "updated_by",
        ]

    @transaction.atomic
    def update(self, instance, validated_data):
        alternative_units_data = validated_data.pop("alternative_units", [])
        opening_stock_data = validated_data.pop("opening_stock", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if alternative_units_data:
            instance.alternative_units.clear()

            alternative_units = []
            for unit_data in alternative_units_data:
                unit_data["auto_id"] = self._generate_auto_id_for_alternate_units()
                alternative_unit = AlternateUnits.objects.create(**unit_data)
                alternative_units.append(alternative_unit)
            instance.alternative_units.add(*alternative_units)

        if opening_stock_data:
            opening_stock, created = Openingstock.objects.get_or_create(
                stock_item=instance
            )
            for attr, value in opening_stock_data.items():
                setattr(opening_stock, attr, value)
            opening_stock.auto_id = self._generate_auto_id_for_opening_stock()
            opening_stock.save()

        return instance

    def _generate_auto_id_for_alternate_units(self):
        last_auto_id = AlternateUnits.objects.aggregate(max_id=models.Max("auto_id"))[
            "max_id"
        ]
        return (last_auto_id or 0) + 1

    def _generate_auto_id_for_opening_stock(self):
        last_auto_id = Openingstock.objects.aggregate(max_id=models.Max("auto_id"))[
            "max_id"
        ]
        return (last_auto_id or 0) + 1

    # def _save_stock_item_history(self, instance):
    #     StockItemHistory.objects.create(
    #         item=instance,
    #         organization_id=instance.organization_id,
    #         name=instance.name,
    #         alias=instance.alias,
    #         description=instance.description,
    #         item_type=instance.item_type,
    #         stock_category=instance.stock_category,
    #         stock_group=instance.stock_group,
    #         brand=instance.brand,
    #         unit=instance.unit,
    #         alternative_unit=instance.alternative_unit,
    #         stock_nature=instance.stock_nature,
    #         standard_rate=instance.standard_rate,
    #         selling_price=instance.selling_price,
    #         cost_price=instance.cost_price,
    #         min_order_quantity=instance.min_order_quantity,
    #         reorder_level=instance.reorder_level,
    #         batch_number_enabled=instance.batch_number_enabled,
    #         manufacturing_date=instance.manufacturing_date,
    #         expiry_date=instance.expiry_date,
    #         gst_applicable=instance.gst_applicable,
    #         hsn_sac=instance.hsn_sac,
    #         gst_type=instance.gst_type,
    #         supply_type=instance.supply_type,
    #         tax=instance.tax,
    #         mrp_type=instance.mrp_type,
    #         mrp_applicable_date=instance.mrp_applicable_date,
    #         selling_price_applicable_date=instance.selling_price_applicable_date,
    #         cost_price_applicable_date=instance.cost_price_applicable_date,
    #         barcode=instance.barcode,
    #         item_code=instance.item_code,
    #         secondary_language_name=instance.secondary_language_name,
    #         image=instance.image,
    #         notes=instance.notes,
    #         application_date=instance.application_date,
    #         alter_gst_details=instance.alter_gst_details,
    #         kitchen=instance.kitchen,
    #     )


class BarcodeDetailsSerializer(BaseModelSerializer):
    class Meta:
        model = BarcodeDetails
        fields = "__all__"
        read_only_fields = [
            "id",
            "auto_id",
            "date_added",
            "creator",
            "updated_at",
            "updated_by",
        ]

    def validate_organization_id(self, value):
        if not value:
            raise serializers.ValidationError("Organization ID is required.")
        return value

    def update(self, instance, validated_data):
        instance.organization_id = validated_data.get(
            "organization_id", instance.organization_id
        )
        instance.include_selling_price = validated_data.get(
            "include_selling_price", instance.include_selling_price
        )
        instance.include_company_name = validated_data.get(
            "include_company_name", instance.include_company_name
        )
        instance.include_barcode = validated_data.get(
            "include_barcode", instance.include_barcode
        )
        instance.include_item_name = validated_data.get(
            "include_item_name", instance.include_item_name
        )
        instance.include_mrp = validated_data.get("include_mrp", instance.include_mrp)
        instance.include_item_code = validated_data.get(
            "include_item_code", instance.include_item_code
        )
        instance.save()
        return instance


class SingleViewListMeasurementUnitSerializer(BaseModelSerializer):
    uqc_name = serializers.SerializerMethodField()

    class Meta:
        model = MeasurementUnit
        fields = [
            "id",
            "auto_id",
            "date_added",
            "creator",
            "updated_at",
            "updated_by",
            "name",
            "decimal_places",
            "organization_id",
            "uqc",
            "uqc_name",
            "symbol",
            "unit_type",
            "is_active",
            "is_primary_unit",
        ]

    def get_uqc_name(self, obj):
        return obj.uqc.name if obj.uqc else None


class SingleViewListViewProductSerializer(BaseModelSerializer):
    category_name = serializers.CharField(source="category.name")

    class Meta:
        model = Product
        fields = [
            "id",
            "auto_id",
            "date_added",
            "creator",
            "updated_at",
            "updated_by",
            "name",
            "category",
            "category_name",
            "organization_id",
            "is_active",
            "related_product",
        ]


class SingleViewStockItemSerializer(BaseModelSerializer):
    stock_category_name = serializers.CharField(
        source="stock_category.name", read_only=True
    )
    stock_group_name = serializers.CharField(source="stock_group.name", read_only=True)
    brand_name = serializers.CharField(source="brand.name", read_only=True)
    # unit_name = serializers.CharField(source="unit.name", read_only=True)
    stock_nature_name = serializers.CharField(
        source="stock_nature.name", read_only=True
    )
    unit_name = serializers.CharField(source="unit.name", read_only=True)
    hsn_sac_name = serializers.CharField(source="hsn_sac.hsnsac_code", read_only=True)
    tax_name = serializers.CharField(source="tax.tax", read_only=True)
    kitchen_name = serializers.CharField(source="kitchen.name", read_only=True)
    alternative_units = serializers.SerializerMethodField()
    opening_balance = serializers.SerializerMethodField()

    class Meta:
        model = StockItem
        fields = [
            "id",
            "organization_id",
            "name",
            "alias",
            "stock_category_name",
            "stock_group_name",
            "brand_name",
            "unit_name",
            "stock_nature_name",
            "aditional_details",
            "item_type",
            "batch_number_enabled",
            "manufacturing_date",
            "expiry_date",
            "gst_applicable",
            "hsn_sac_name",
            "gst_type",
            "supply_type",
            "brand",
            "godown",
            "stock_category",
            "stock_group",
            "tax",
            "stock_nature",
            "hsn_sac",
            "kitchen",
            "tax_name",
            "mrp_type",
            "standard_rate",
            "selling_price",
            "unit",
            "cost_price",
            "min_order_quantity",
            "reorder_level",
            "notes",
            "item_code",
            "barcode",
            "secondary_language_name",
            "image",
            "alternative_units",
            "opening_balance",
            "application_date",
            "alter_gst_details",
            "kitchen_name",
            "selling_price_applicable_date",
            "cost_price_applicable_date",
            "mrp_applicable_date",
        ]

    def get_alternative_units(self, obj):
        alt_units = obj.alternative_units.all()
        return [
            {
                "organization_id": unit.organization_id,
                "unit_id": unit.id,
                "alternative_unit": unit.alternative_unit,
                "unit_value": unit.unit_value.id if unit.unit_value else None,
                "unit_value_name": unit.unit_value.name if unit.unit_value else None,
                "related_unit": unit.related_unit.id if unit.related_unit else None,
                "related_unit_name": unit.related_unit.name
                if unit.related_unit
                else None,
                "related_unit_values": unit.related_unit_values,
                "cost_price": unit.cost_price if hasattr(unit, "cost_price") else None,
                "selling_price": unit.selling_price
                if hasattr(unit, "selling_price")
                else None,
                "barcode": unit.barcode,
            }
            for unit in alt_units
        ]

    def get_opening_balance(self, obj):
        opening_balance = obj.opening_balances.first()
        if opening_balance:
            return {
                "quantity": opening_balance.quantity,
                "rate": opening_balance.rate,
                "amount": opening_balance.amount,
            }
        return None


# class SingleViewStockItemSerializer(BaseModelSerializer):
#     stock_category_name = serializers.CharField(
#         source="stock_category.name", read_only=True
#     )
#     stock_group_name = serializers.CharField(source="stock_group.name", read_only=True)
#     brand_name = serializers.CharField(source="brand.name", read_only=True)
#     unit_name = serializers.CharField(source="unit.name", read_only=True)
#     alternative_units = serializers.SerializerMethodField()
#     opening_balance = serializers.SerializerMethodField()

#     class Meta:
#         model = StockItem
#         fields = [
#             "id",
#             "organization_id",
#             "name",
#             "alias",
#             "stock_category_name",
#             "stock_group_name",
#             "brand_name",
#             "unit_name",
#             "item_type",
#             "batch_number_enabled",
#             "manufacturing_date",
#             "expiry_date",
#             "gst_applicable",
#             "gst_type",
#             "mrp_type",
#             "standard_rate",
#             "selling_price",
#             "cost_price",
#             "min_order_quantity",
#             "reorder_level",
#             "item_code",
#             "barcode",
#             "alternative_units",
#             "opening_balance",
#         ]

#     def get_opening_balance(self, obj):
#         opening_balance = obj.opening_balances.first()
#         if opening_balance:
#             return {
#                 "quantity": opening_balance.quantity,
#                 "rate": opening_balance.rate,
#                 "amount": opening_balance.amount,
#             }
#         return None

#     def get_alternative_units(self, obj):
#         alt_units = obj.alternative_units.all()
#         return [
#             {
#                 "organization_id": unit.organization_id,
#                 "alternative_unit": unit.alternative_unit,
#                 "unit_value_name": unit.unit_value.name if unit.unit_value else None,
#                 "related_unit_name": unit.related_unit.name if unit.related_unit else None,
#                 "cost_price": unit.cost_price if hasattr(unit, 'cost_price') else None,
#                 "selling_price": unit.selling_price if hasattr(unit, 'selling_price') else None,
#             }
#             for unit in alt_units
#         ]


class ListViewIteamSerializer(BaseModelSerializer):
    class Meta:
        model = StockItem
        fields = "__all__"


# class ListViewIteamSerializer(BaseModelSerializer):
#     class Meta:
#         model = StockItem
#         fields = ["id", "name", "barcode", "selling_price", "cost_price"]


class StockcategoryNameSerializer(BaseModelSerializer):
    class Meta:
        model = StockCategory
        fields = [
            "id",
            "name",
            "is_primary_stock_category",
        ]


class StockGroupNameSerializer(BaseModelSerializer):
    class Meta:
        model = StockGroup
        fields = [
            "id",
            "name",
            "is_primary_group",
        ]


class GodownNameSerializer(BaseModelSerializer):
    class Meta:
        model = Godown
        fields = [
            "id",
            "name",
            "is_primary_godown",
        ]


class StockClassificationNameSerializer(BaseModelSerializer):
    class Meta:
        model = StockClassification
        fields = [
            "id",
            "name",
            "is_primary_classification",
        ]


class StockItemNameSerializer(BaseModelSerializer):
    class Meta:
        model = StockItem
        fields = ["id", "name"]


class StockNaturalNameSerializer(BaseModelSerializer):
    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "is_primary_stock_nature",
        ]


class BrandNameSerializer(BaseModelSerializer):
    class Meta:
        model = Brand
        fields = [
            "id",
            "name",
            "is_primary_brand",
        ]


class KitchenSerializer(BaseModelSerializer):
    class Meta:
        model = Kitchen
        fields = "__all__"
        read_only_fields = [
            "id",
            "auto_id",
            "date_added",
            "creator",
            "updated_at",
            "updated_by",
        ]


class BaseStockItemSerializer(BaseModelSerializer):
    tax_amount = serializers.SerializerMethodField()

    class Meta:
        model = StockItem
        fields = ["id", "name", "tax", "tax_amount"]
        read_only_fields = ["id", "tax", "tax_amount"]

    def get_tax_amount(self, obj):
        if obj.tax and obj.tax.tax is not None:
            return obj.tax.tax
        return 0


class StockJurnalItemReportSerializer(BaseModelSerializer):
    unit_name = serializers.CharField(source="unit.name", read_only=True)
    tax_amount = serializers.CharField(source="tax.tax", read_only=True)
    quantity = serializers.SerializerMethodField()

    class Meta:
        model = StockItem
        fields = [
            "id",
            "name",
            # "standard_rate",
            "selling_price",
            # "cost_price",
            "unit",
            "unit_name",
            "tax",
            "tax_amount",
            # "unit_details",
            "quantity",
        ]

    def get_quantity(self, obj):
        stock_report = StockReport.objects.filter(item=obj).first()
        if stock_report:
            return stock_report.closing_balance
        return 0.0


class StockItemSalesListSerializer(BaseStockItemSerializer):
    class Meta(BaseStockItemSerializer.Meta):
        fields = BaseStockItemSerializer.Meta.fields + ["selling_price"]


class StockItemPurchaseListSerializer(BaseStockItemSerializer):
    class Meta(BaseStockItemSerializer.Meta):
        fields = BaseStockItemSerializer.Meta.fields + ["cost_price"]


class KitchenNameSerializer(BaseModelSerializer):
    class Meta:
        model = Kitchen
        fields = ["id", "name"]


class UnitDetailedStockItemSerializer(BaseModelSerializer):
    stock_category_name = serializers.CharField(
        source="stock_category.name", read_only=True
    )
    stock_group_name = serializers.CharField(source="stock_group.name", read_only=True)
    brand_name = serializers.CharField(source="brand.name", read_only=True)
    unit_name = serializers.CharField(source="unit.name", read_only=True)
    stock_nature_name = serializers.CharField(
        source="stock_nature.name", read_only=True
    )
    hsn_sac_name = serializers.CharField(source="hsn_sac.hsnsac_code", read_only=True)
    tax_name = serializers.CharField(source="tax.tax", read_only=True)
    kitchen_name = serializers.CharField(source="kitchen.name", read_only=True)
    alternative_units = serializers.SerializerMethodField()
    opening_balance = serializers.SerializerMethodField()
    unit_ids = serializers.SerializerMethodField()  # Add a field for unit IDs

    class Meta:
        model = StockItem
        fields = [
            "id",
            "organization_id",
            "name",
            "alias",
            "stock_category_name",
            "stock_group_name",
            "brand_name",
            "unit_name",
            "stock_nature_name",
            "aditional_details",
            "item_type",
            "batch_number_enabled",
            "manufacturing_date",
            "expiry_date",
            "gst_applicable",
            "hsn_sac_name",
            "gst_type",
            "supply_type",
            "tax_name",
            "mrp_type",
            "standard_rate",
            "selling_price",
            "unit",
            "cost_price",
            "min_order_quantity",
            "reorder_level",
            "notes",
            "item_code",
            "barcode",
            "secondary_language_name",
            "image",
            "alternative_units",
            "opening_balance",
            "application_date",
            "alter_gst_details",
            "kitchen_name",
            "selling_price_applicable_date",
            "cost_price_applicable_date",
            "mrp_applicable_date",
            "unit_ids",
        ]

    def get_alternative_units(self, obj):
        alt_units = obj.alternative_units.all()
        return [
            {
                "organization_id": unit.organization_id,
                "unit_id": unit.id,
                "alternative_unit_name": unit.alternative_unit,
                "unit_value_id": unit.unit_value.id if unit.unit_value else None,
                "unit_value_name": unit.unit_value.name if unit.unit_value else None,
                "related_unit_id": unit.related_unit.id if unit.related_unit else None,
                "related_unit_name": unit.related_unit.name
                if unit.related_unit
                else None,
                "related_unit_values": unit.related_unit_values,
                "cost_price": unit.cost_price,
                "selling_price": unit.selling_price,
                "barcode": unit.barcode,
            }
            for unit in alt_units
        ]

    def get_opening_balance(self, obj):
        opening_balance = obj.opening_balances.first()
        if opening_balance:
            return {
                "quantity": opening_balance.quantity,
                "rate": opening_balance.rate,
                "amount": opening_balance.amount,
            }
        return None

    def get_unit_ids(self, obj):
        if obj.unit is None:
            return []
        if not hasattr(obj.unit, "items"):
            return []

        return [{"id": unit.id, "name": unit.name} for unit in obj.unit.items.all()]


# class UnitAlternativeUnitSerializer(BaseModelSerializer):
#     class Meta:
#         model = AlternateUnits
#         fields = ["id", "alternative_unit", "unit_value", "related_unit"]

# class StockItemUnitsListSerializer(BaseModelSerializer):
#     unit_id = serializers.PrimaryKeyRelatedField(source='unit', read_only=True)
#     unit_name = serializers.CharField(source='unit.name', read_only=True)
#     alternative_units_list = serializers.SerializerMethodField()
#     all_units_list = serializers.SerializerMethodField()

#     class Meta:
#         model = StockItem
#         fields = [
#             'id',
#             'name',
#             'unit_id',
#             'unit_name',
#             "standard_rate",
#             "selling_price",
#             "cost_price",
#             'alternative_units_list',
#             'all_units_list',
#         ]

#     def get_alternative_units_list(self, obj):
#         alternative_units = obj.alternative_units.all()
#         return AlternateUnitsSerializer(alternative_units, many=True).data


#     def get_all_units_list(self, obj):
#         if obj.unit is None:
#             return []
#         if not hasattr(obj.unit, 'items'):
#             return []
#         return [
#             {
#                 "id": unit.id,
#                 "name": unit.name
#             }
#             for unit in obj.unit.items.all()
#         ]
class UnitAlternateUnitsUnitSerializer(BaseModelSerializer):
    class Meta:
        model = AlternateUnits
        fields = [
            "id",
            "alternative_unit",
            "unit_value",
            "related_unit",
            "related_unit_values",
            "cost_price",
            "selling_price",
        ]


class StockItemUnitsListSerializer(BaseModelSerializer):
    unit_name = serializers.CharField(source="unit.name", read_only=True)
    tax_amount = serializers.CharField(source="tax.tax", read_only=True)
    unit_details = serializers.SerializerMethodField()
    quantity = serializers.SerializerMethodField()

    class Meta:
        model = StockItem
        fields = [
            "id",
            "name",
            "standard_rate",
            "selling_price",
            "cost_price",
            "unit",
            "quantity",
            "unit_name",
            "tax",
            "tax_amount",
            "unit_details",
        ]

    def get_unit_details(self, obj):
        alternative_units = obj.alternative_units.all()
        alternative_units_data = [
            {
                "unit_id": unit.id,
                "unit_name": unit.alternative_unit,
                "selling_price": unit.selling_price,
                "cost_price": unit.cost_price,
                "main_unit": False,
            }
            for unit in alternative_units
        ]
        main_unit = {
            "unit_id": obj.unit.id if obj.unit else None,
            "unit_name": obj.unit.name if obj.unit else None,
            "standard_rate": float(obj.standard_rate) if obj.standard_rate else None,
            "selling_price": float(obj.selling_price) if obj.selling_price else None,
            "cost_price": float(obj.cost_price) if obj.cost_price else None,
            "main_unit": True,
        }
        alternative_units_data.append(main_unit)
        return {"alternative_units": alternative_units_data}

    def get_quantity(self, obj):
        stock_report = StockReport.objects.filter(item=obj).first()
        if stock_report:
            return stock_report.closing_balance
        return 0.0

# class StockItemUnitsListSerializer(BaseModelSerializer):
#     unit_id = serializers.PrimaryKeyRelatedField(source="unit", read_only=True)
#     unit_name = serializers.CharField(source="unit.name", read_only=True)
#     alternative_units_list = serializers.SerializerMethodField()

#     class Meta:
#         model = StockItem
#         fields = [
#             "id",
#             "name",
#             "unit_id",
#             "unit_name",
#             "standard_rate",
#             "selling_price",
#             "cost_price",
#             "alternative_units_list",
#         ]

#     def get_alternative_units_list(self, obj):
#         # Fetch all alternative units
#         alternative_units = obj.alternative_units.all()

#         # Prepare all alternative units as a list of dictionaries
#         alternative_units_data = [
#             {
#                 "unit_id": unit.id,
#                 "unit_name": unit.alternative_unit,  # Use directly as a string
#                 "selling_price": unit.selling_price,
#                 "cost_price": unit.cost_price,
#             }
#             for unit in alternative_units
#         ]

#         # Create main unit dictionary and append alternative units
#         main_unit = {
#             "unit_id": obj.unit.id if obj.unit else None,
#             "unit_name": obj.unit.name if obj.unit else None,
#             "standard_rate": obj.standard_rate,
#             "selling_price": obj.selling_price,
#             "cost_price": obj.cost_price,
#             "alternative_units": alternative_units_data,  # Append alternative units here
#         }

#         return main_unit


class BrandNameList(BaseModelSerializer):
    class Meta:
        model = Brand
        fields = [
            "id",
            "name",
            "is_primary_brand",
        ]


class SalesPurchaseItemSerializer(BaseModelSerializer):
    quantity = serializers.SerializerMethodField()

    class Meta:
        model = StockItem
        fields = [
            "id",
            # "organization_id",
            "name",
            "quantity",
        ]

    def get_quantity(self, obj):
        stock_report = StockReport.objects.filter(item=obj).first()
        if stock_report:
            return stock_report.closing_balance
        return 0.0
