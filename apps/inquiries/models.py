from django.conf import settings
from django.db import models

try:
    from apps.common.models import TimeStampedUUIDModel
except (ImportError, ModuleNotFoundError):
    from ..common.models import TimeStampedUUIDModel

try:
    from apps.properties.models import Property
except (ImportError, ModuleNotFoundError):
    from ..properties.models import Property


class Inquiry(TimeStampedUUIDModel):
    """
    Tenant Screening Inquiry:
    Tenants submit an inquiry with their verified credentials (occupation, workplace, family size).
    Landlords review this in their Tenant Screening Inbox before accepting a chat or call.
    """
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending Review'
        ACCEPTED = 'ACCEPTED', 'Accepted'
        DECLINED = 'DECLINED', 'Declined'

    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='inquiries',
    )
    tenant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='submitted_inquiries',
    )
    message = models.TextField(blank=True, default='')
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )

    # Snapshot of tenant credentials at time of inquiry
    tenant_occupation = models.CharField(max_length=120, blank=True, default='')
    tenant_workplace = models.CharField(max_length=150, blank=True, default='')
    tenant_family_size = models.PositiveSmallIntegerField(default=1)
    tenant_is_nid_verified = models.BooleanField(default=False)
    tenant_rental_rating = models.FloatField(default=5.0)

    objects = models.Manager()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Inquiry by {self.tenant.full_name} for {self.property.title}"


class VisitBooking(TimeStampedUUIDModel):
    """
    Visit Scheduler & Live Video Tour:
    Tenants can book either an in-person viewing slot or a live video walkthrough.
    """
    class BookingType(models.TextChoices):
        IN_PERSON = 'IN_PERSON', 'In-Person Visit'
        VIDEO_TOUR = 'VIDEO_TOUR', 'Live Video Tour'

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        CONFIRMED = 'CONFIRMED', 'Confirmed'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'

    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='visit_bookings',
    )
    tenant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='scheduled_visits',
    )
    booking_type = models.CharField(
        max_length=20,
        choices=BookingType.choices,
        default=BookingType.IN_PERSON,
    )
    scheduled_date = models.DateField()
    time_slot = models.CharField(max_length=50)  # e.g., "10:00 AM - 11:00 AM"
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    video_call_link = models.URLField(blank=True, null=True)
    notes = models.TextField(blank=True, default='')

    objects = models.Manager()

    class Meta:
        ordering = ['scheduled_date', '-created_at']

    def __str__(self):
        return f"{self.booking_type} on {self.scheduled_date} ({self.time_slot}) for {self.property.title}"
