import uuid
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.db import models


class TimeStampedUUIDModel(models.Model):
    """
    Abstract base model providing UUID primary key and timestamp fields.
    """
    DoesNotExist = ObjectDoesNotExist
    MultipleObjectsReturned = MultipleObjectsReturned

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    class Meta:
        abstract = True
        ordering = ['-created_at']
