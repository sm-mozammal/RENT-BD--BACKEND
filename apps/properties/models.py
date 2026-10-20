from decimal import Decimal
from django.conf import settings
from django.db import models
from django.utils import timezone

try:
    from apps.common.models import TimeStampedUUIDModel
    from apps.common.utils import mask_phone_number
except (ImportError, ModuleNotFoundError):
    from ..common.models import TimeStampedUUIDModel
    from ..common.utils import mask_phone_number


class Property(TimeStampedUUIDModel):
    class PropertyType(models.TextChoices):
        APARTMENT = 'APARTMENT', 'Apartment'
        SUBLET = 'SUBLET', 'Sublet'
        HOSTEL = 'HOSTEL', 'Hostel'
        DUPLEX = 'DUPLEX', 'Duplex'

    class TenantCategory(models.TextChoices):
        FAMILY = 'FAMILY', 'Family'
        BACHELOR_MALE = 'BACHELOR_MALE', 'Bachelor Male'
        BACHELOR_FEMALE = 'BACHELOR_FEMALE', 'Bachelor Female'
        ANY = 'ANY', 'Any'

    class FairPriceStatus(models.TextChoices):
        GREAT_DEAL = 'GREAT_DEAL', 'Great Deal'
        FAIR_PRICE = 'FAIR_PRICE', 'Fair Price'
        OVERPRICED = 'OVERPRICED', 'Overpriced'

    class GasSupplyType(models.TextChoices):
        LINE_GAS = 'LINE_GAS', 'Line Gas'
        CYLINDER = 'CYLINDER', 'Cylinder'
        NONE = 'NONE', 'None'

    class WaterloggingRisk(models.TextChoices):
        NONE = 'NONE', 'None'
        MILD = 'MILD', 'Mild'
        HIGH = 'HIGH', 'High'

    class WaterQuality(models.TextChoices):
        EXCELLENT = 'EXCELLENT', 'Excellent'
        ADEQUATE = 'ADEQUATE', 'Adequate'
        IRREGULAR = 'IRREGULAR', 'Irregular'

    # Landlord
    landlord = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='properties',
    )

    # Core Listing Information
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    property_type = models.CharField(
        max_length=20,
        choices=PropertyType.choices,
        default=PropertyType.APARTMENT,
    )
    tenant_category = models.CharField(
        max_length=20,
        choices=TenantCategory.choices,
        default=TenantCategory.FAMILY,
        db_index=True,
    )

    # Financials (BDT)
    rent_amount = models.DecimalField(max_digits=10, decimal_places=2)
    security_deposit = models.DecimalField(max_digits=10, decimal_places=2)
    service_charge = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('3500.00'))
    estimated_utilities = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('2000.00'))

    # Unit Specifications
    bedrooms = models.PositiveSmallIntegerField(default=2)
    bathrooms = models.PositiveSmallIntegerField(default=2)
    balconies = models.PositiveSmallIntegerField(default=1)
    square_feet = models.PositiveIntegerField(default=900)
    floor_level = models.PositiveSmallIntegerField(default=3)
    total_floors = models.PositiveSmallIntegerField(default=7)

    # Location & Mapping
    latitude = models.FloatField(default=23.8103, db_index=True)
    longitude = models.FloatField(default=90.4125, db_index=True)
    area_neighborhood = models.CharField(max_length=120, default='Mirpur 10', db_index=True)
    full_address = models.CharField(max_length=255)

    # Badges & Status
    class ModerationStatus(models.TextChoices):
        ACTIVE = 'active', 'Active'
        PENDING_APPROVAL = 'pending_approval', 'Pending Approval'
        FLAGGED_SPAM = 'flagged_spam', 'Flagged Spam'
        RENTED = 'rented', 'Rented'
        REJECTED = 'rejected', 'Rejected'

    status = models.CharField(
        max_length=20,
        choices=ModerationStatus.choices,
        default=ModerationStatus.ACTIVE,
        db_index=True,
    )
    has_geo_tagged_photos = models.BooleanField(default=True)
    is_available = models.BooleanField(default=True, db_index=True)  # Property Vault (True=Available, False=Rented)
    is_owner_verified = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False, db_index=True)

    # AI & Area Insights
    fair_price_status = models.CharField(
        max_length=20,
        choices=FairPriceStatus.choices,
        default=FairPriceStatus.FAIR_PRICE,
    )
    fair_price_percent_diff = models.FloatField(default=0.0)
    area_average_rent = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('20000.00'))
    alleyWidthFeet = models.FloatField(default=16.0)

    # Utility & Living Quality
    gas_supply = models.CharField(
        max_length=20,
        choices=GasSupplyType.choices,
        default=GasSupplyType.LINE_GAS,
    )
    waterlogging_risk = models.CharField(
        max_length=20,
        choices=WaterloggingRisk.choices,
        default=WaterloggingRisk.NONE,
    )
    water_quality = models.CharField(
        max_length=20,
        choices=WaterQuality.choices,
        default=WaterQuality.EXCELLENT,
    )
    night_safety_rating = models.FloatField(default=4.5)

    # Expiry tracking (15-day automated availability check)
    last_confirmed_available_at = models.DateTimeField(default=timezone.now)

    objects = models.Manager()

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_available', 'tenant_category', 'rent_amount']),
            models.Index(fields=['latitude', 'longitude']),
        ]

    def __str__(self):
        rent = getattr(self, 'rent_amount', '0')
        area = getattr(self, 'area_neighborhood', '')
        title = getattr(self, 'title', 'Property')
        return f"{title} ({area}) - ৳{rent}"

    @property
    def landlord_name(self) -> str:
        landlord = getattr(self, 'landlord', None)
        return str(getattr(landlord, 'full_name', '') or '')

    @property
    def landlord_phone_masked(self) -> str:
        landlord = getattr(self, 'landlord', None)
        phone = getattr(landlord, 'phone_number', '') if landlord else ''
        return mask_phone_number(phone) if phone else ''

    @property
    def landlord_is_nid_verified(self) -> bool:
        landlord = getattr(self, 'landlord', None)
        profile = getattr(landlord, 'landlord_profile', None) if landlord else None
        return bool(getattr(profile, 'is_nid_verified', False)) if profile else False

    @property
    def landlord_rating(self) -> float:
        landlord = getattr(self, 'landlord', None)
        profile = getattr(landlord, 'landlord_profile', None) if landlord else None
        if profile and hasattr(profile, 'rental_rating'):
            try:
                return float(profile.rental_rating)
            except (ValueError, TypeError):
                return 4.8
        return 4.8

    @property
    def total_move_in_cost(self) -> float:
        """
        Move-in Cost Calculator: First month rent + Security deposit + Service charge + Estimated utilities
        """
        try:
            rent = float(getattr(self, 'rent_amount', 0) or 0)
            deposit = float(getattr(self, 'security_deposit', 0) or 0)
            service = float(getattr(self, 'service_charge', 0) or 0)
            utilities = float(getattr(self, 'estimated_utilities', 0) or 0)
            return rent + deposit + service + utilities
        except (TypeError, ValueError):
            return 0.0


class PropertyImage(TimeStampedUUIDModel):
    class RoomType(models.TextChoices):
        BEDROOM = 'BEDROOM', 'Bedroom'
        LIVING_ROOM = 'LIVING_ROOM', 'Living Room'
        KITCHEN = 'KITCHEN', 'Kitchen'
        WASHROOM = 'WASHROOM', 'Washroom'
        BALCONY = 'BALCONY', 'Balcony'
        EXTERIOR = 'EXTERIOR', 'Exterior'

    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='images',
    )
    image = models.ImageField(upload_to='property_photos/', blank=True, null=True)
    image_url = models.URLField(blank=True, default='')
    room_type = models.CharField(
        max_length=20,
        choices=RoomType.choices,
        default=RoomType.LIVING_ROOM,
    )
    is_geo_tagged = models.BooleanField(default=True)
    captured_at = models.DateTimeField(default=timezone.now)
    exif_latitude = models.FloatField(blank=True, null=True)
    exif_longitude = models.FloatField(blank=True, null=True)

    objects = models.Manager()

    def __str__(self):
        return f"Image for {self.property.title} ({self.room_type})"

    def get_final_image_url(self) -> str:
        try:
            if bool(getattr(self, 'image', None)):
                url = getattr(self.image, 'url', None)
                if url:
                    return str(url)
        except (ValueError, AttributeError):
            pass
        return str(getattr(self, 'image_url', '') or '')


class SavedProperty(TimeStampedUUIDModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='saved_properties',
    )
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='saved_by_users',
    )

    objects = models.Manager()

    class Meta:
        unique_together = ('user', 'property')

    def __str__(self):
        return f"{self.user.full_name} saved {self.property.title}"


class SavedSearch(TimeStampedUUIDModel):
    """
    Saved Search & Instant Alerts:
    Tenants save location and budget parameters (e.g. Uttara, under 15,000 BDT)
    to receive instant alerts when a matching flat goes live.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='saved_searches',
    )
    name = models.CharField(max_length=120)
    area = models.CharField(max_length=120, blank=True, default='')
    tenant_category = models.CharField(max_length=20, blank=True, default='')
    min_rent = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    max_rent = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    bedrooms = models.PositiveSmallIntegerField(null=True, blank=True)
    push_alerts_enabled = models.BooleanField(default=True)
    last_alert_sent_at = models.DateTimeField(null=True, blank=True)

    objects = models.Manager()

    def __str__(self):
        return f"SavedSearch: {self.name} for {self.user.full_name}"


class SavedSearchAlert(TimeStampedUUIDModel):
    """
    Instant Alerts triggered when a newly listed property matches a SavedSearch.
    """
    saved_search = models.ForeignKey(
        SavedSearch,
        on_delete=models.CASCADE,
        related_name='alerts',
    )
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='triggered_alerts',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='property_alerts',
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)

    objects = models.Manager()

    class Meta:
        ordering = ['-created_at']
        unique_together = ('saved_search', 'property')

    def __str__(self):
        return f"Alert for {self.user.full_name}: {self.title}"


