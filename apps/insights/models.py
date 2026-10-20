from django.conf import settings
from django.db import models
try:
    from apps.common.models import TimeStampedUUIDModel
except (ImportError, ModuleNotFoundError):
    from ..common.models import TimeStampedUUIDModel


class AreaInsight(TimeStampedUUIDModel):
    class WaterloggingRisk(models.TextChoices):
        NONE = 'NONE', 'No Waterlogging'
        MILD = 'MILD', 'Mild (Drains within 1-2 hours)'
        HIGH = 'HIGH', 'Severe Monsoon Waterlogging'

    class GasSupply(models.TextChoices):
        EXCELLENT = 'EXCELLENT', 'Continuous 24/7 Full Pressure'
        ADEQUATE = 'ADEQUATE', 'Low Pressure during Morning Cooking Hours'
        POOR = 'POOR', 'Severe Gas Shortage (Requires Cylinder)'
        NONE = 'NONE', 'No Line Gas'

    class WaterQuality(models.TextChoices):
        EXCELLENT = 'EXCELLENT', 'Clean WASA Supply'
        ADEQUATE = 'ADEQUATE', 'Adequate (Filter Recommended)'
        IRREGULAR = 'IRREGULAR', 'Irregular / Smelly Water'

    area_name = models.CharField(max_length=120, db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='area_insights',
    )
    waterlogging_risk = models.CharField(
        max_length=20,
        choices=WaterloggingRisk.choices,
        default=WaterloggingRisk.NONE,
    )
    gas_supply_reliability = models.CharField(
        max_length=20,
        choices=GasSupply.choices,
        default=GasSupply.EXCELLENT,
    )
    water_quality = models.CharField(
        max_length=20,
        choices=WaterQuality.choices,
        default=WaterQuality.EXCELLENT,
    )
    night_safety_rating = models.FloatField(default=4.5)
    resident_review = models.TextField(blank=True, default='')

    objects = models.Manager()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Insight for {self.area_name} by {self.user.full_name}"
