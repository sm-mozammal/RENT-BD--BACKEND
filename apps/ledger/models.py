from decimal import Decimal
from django.conf import settings
from django.db import models
from django.utils import timezone
try:
    from apps.common.models import TimeStampedUUIDModel
except (ImportError, ModuleNotFoundError):
    from ..common.models import TimeStampedUUIDModel

try:
    from apps.properties.models import Property
except (ImportError, ModuleNotFoundError):
    from ..properties.models import Property


class TenancyContract(TimeStampedUUIDModel):
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='contracts',
    )
    landlord = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='landlord_tenancies',
    )
    tenant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tenant_tenancies',
    )
    agreed_rent = models.DecimalField(max_digits=10, decimal_places=2)
    service_charge = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('3000.00'))
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    objects = models.Manager()

    def __str__(self):
        return f"Tenancy: {self.tenant.full_name} in {self.property.title}"


class RentBill(TimeStampedUUIDModel):
    class Status(models.TextChoices):
        DUE = 'DUE', 'Payment Due'
        PAID = 'PAID', 'Settled & Paid'
        OVERDUE = 'OVERDUE', 'Overdue'

    contract = models.ForeignKey(
        TenancyContract,
        on_delete=models.CASCADE,
        related_name='bills',
    )
    billing_month = models.CharField(max_length=50)  # e.g. "October 2026"
    base_rent = models.DecimalField(max_digits=10, decimal_places=2)
    electricity_bill = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    gas_bill = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    water_bill = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    service_charge = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DUE)
    due_date = models.DateField()
    paid_at = models.DateTimeField(null=True, blank=True)
    payment_method = models.CharField(max_length=50, blank=True, default='')

    objects = models.Manager()

    def __str__(self):
        return f"Bill {self.billing_month} - {self.contract.property.title} (৳{self.total_amount})"


class RentReceipt(TimeStampedUUIDModel):
    bill = models.OneToOneField(
        RentBill,
        on_delete=models.CASCADE,
        related_name='receipt',
    )
    receipt_no = models.CharField(max_length=50, unique=True)
    generated_at = models.DateTimeField(default=timezone.now)

    objects = models.Manager()

    def __str__(self):
        return f"Receipt #{self.receipt_no}"
