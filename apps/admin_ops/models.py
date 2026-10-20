from decimal import Decimal
from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.common.models import TimeStampedUUIDModel
from apps.properties.models import Property


class NIDVerificationRequest(TimeStampedUUIDModel):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending Review'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'

    class NIDType(models.TextChoices):
        SMART_CARD = 'smart_card', 'Smart NID Card'
        OLD_NID = 'old_nid', 'Old Paper/Laminated NID'
        BIRTH_CERT = 'birth_cert', 'Birth Certificate'

    landlord = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='nid_verification_requests',
    )
    nid_number = models.CharField(max_length=50)
    nid_type = models.CharField(max_length=30, choices=NIDType.choices, default=NIDType.SMART_CARD)
    nid_front_url = models.URLField(max_length=500, blank=True, default='')
    nid_back_url = models.URLField(max_length=500, blank=True, default='')
    live_selfie_url = models.URLField(max_length=500, blank=True, default='')
    ai_face_match_confidence = models.FloatField(default=90.0)
    extracted_data = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)

    reviewer_notes = models.TextField(blank=True, default='')
    rejection_reason = models.TextField(blank=True, default='')
    reviewed_by = models.CharField(max_length=120, blank=True, default='')
    reviewed_at = models.DateTimeField(null=True, blank=True)

    objects = models.Manager()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"NID Verification for {self.landlord.full_name} ({self.status})"


class GeoPhotoVerification(TimeStampedUUIDModel):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending Verification'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'

    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='geo_photo_verifications',
    )
    landlord_name = models.CharField(max_length=120, blank=True, default='')
    landlord_phone = models.CharField(max_length=30, blank=True, default='')
    photo_url = models.URLField(max_length=500)

    property_lat = models.FloatField(default=23.8103)
    property_lng = models.FloatField(default=90.4125)
    property_address = models.CharField(max_length=255, blank=True, default='')

    exif_lat = models.FloatField(default=23.8103)
    exif_lng = models.FloatField(default=90.4125)

    distance_difference_meters = models.FloatField(default=0.0)
    accuracy_meters = models.FloatField(default=5.0)
    is_camera_live = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)

    objects = models.Manager()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Geo-Photo for {self.property.title} ({self.status})"


class SpamReport(TimeStampedUUIDModel):
    class Status(models.TextChoices):
        PENDING_REVIEW = 'pending_review', 'Pending Review'
        LISTING_BANNED = 'listing_banned', 'Listing Banned'
        LANDLORD_BLOCKED = 'landlord_blocked', 'Landlord Blocked'
        FALSE_POSITIVE = 'false_positive', 'False Positive'

    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='spam_reports',
    )
    original_property = models.ForeignKey(
        Property,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='flagged_duplicates',
    )
    landlord_name = models.CharField(max_length=120, blank=True, default='')
    landlord_phone = models.CharField(max_length=30, blank=True, default='')
    rent_bdt = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    average_area_rent = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    flags = models.JSONField(default=list, blank=True)
    ai_confidence_score = models.FloatField(default=95.0)
    duplicate_match = models.JSONField(null=True, blank=True)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.PENDING_REVIEW, db_index=True)

    objects = models.Manager()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Spam Flag for {self.property.title} ({self.status})"
