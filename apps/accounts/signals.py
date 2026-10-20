from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, TenantProfile, LandlordProfile


@receiver(post_save, sender=User)
def create_user_profiles(sender, instance, created, **kwargs):
    if created:
        TenantProfile.objects.get_or_create(user=instance)
        LandlordProfile.objects.get_or_create(user=instance)
