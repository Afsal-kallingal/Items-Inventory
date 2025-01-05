# from rest_framework import serializers
from apps.main.functions import get_auto_id

# class BaseModelSerializer(serializers.ModelSerializer):
#     auto_id = serializers.CharField(read_only=True)
#     creator = serializers.CharField(read_only=True)
#     date_added = serializers.CharField(read_only=True)
#     updated_at = serializers.CharField(read_only=True)  
#     updated_by = serializers.CharField(read_only=True)  

#     def create(self, validated_data):
#         validated_data["auto_id"] = get_auto_id(self.Meta.model)
#         validated_data["creator"] = self.context["request"].user
#         validated_data["updated_by"] = self.context["request"].user
#         return super().create(validated_data)

#     def update(self, instance, validated_data):
#         validated_data["updated_by"] = self.context["request"].user  # Set updated_by on update
#         return super().update(instance, validated_data)

#     class Meta:
#         abstract = True

from rest_framework import serializers
import uuid

class BaseModelSerializer(serializers.ModelSerializer):
    auto_id = serializers.CharField(read_only=True)
    creator = serializers.UUIDField(read_only=True)  # Now a UUID field
    date_added = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    updated_by = serializers.UUIDField(read_only=True)  # Now a UUID field

    def create(self, validated_data):
        # Generate auto_id
        validated_data["auto_id"] = get_auto_id(self.Meta.model)
        
        # Set creator to request user UUID if available
        user = self.context["request"].user
        if user and user.is_authenticated:
            validated_data["creator"] = user.id  # Assign UUID from user.id
        
        # Set updated_by to request user UUID if available
        validated_data["updated_by"] = user.id if user and user.is_authenticated else None

        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Set updated_by to request user UUID on update
        user = self.context["request"].user
        validated_data["updated_by"] = user.id if user and user.is_authenticated else None

        return super().update(instance, validated_data)

    class Meta:
        abstract = True
