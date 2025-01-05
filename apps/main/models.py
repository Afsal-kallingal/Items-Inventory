# import uuid
# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from apps.user_account.models import User


# class BaseModel(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     auto_id = models.IntegerField(db_index=True, unique=True,default=1)
#     date_added = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True) 
#     creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="+")
#     updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="+")  # User who last updated
#     is_deleted = models.BooleanField(default=False)

#     class Meta:
#         abstract = True

import uuid
from django.db import models

class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    auto_id = models.IntegerField(db_index=True, unique=True, default=1)
    date_added = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    creator = models.UUIDField(null=True, blank=True)  # Store the creator's UUID
    updated_by = models.UUIDField(null=True, blank=True)  # Store the UUID of the last updater
    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True
