from datetime import timedelta
import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.db import models
from django.utils import timezone

from apps.common.models import TimeStampedUUIDModel
from apps.common.utils import normalize_bangladesh_phone


class UserManager(BaseUserManager):
    def create_user(self, phone_number, full_name, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('The phone number must be set')
        phone_number = normalize_bangladesh_phone(phone_number)
        user = self.model(phone_number=phone_number, full_name=full_name, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, full_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_phone_verified', True)
        extra_fields.setdefault('role', User.Role.DUAL)

        if not password:
            raise ValueError('Superusers must have a password.')

        return self.create_user(phone_number, full_name, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, TimeStampedUUIDModel):
    class Role(models.TextChoices):
        TENANT = 'tenant', 'Tenant'
        LANDLORD = 'landlord', 'Landlord'
        DUAL = 'dual', 'Dual (Tenant & Landlord)'
        ADMIN = 'admin', 'Administrator'

    phone_number = models.CharField(max_length=20, unique=True, db_index=True)
    full_name = models.CharField(max_length=120)
    email = models.EmailField(blank=True, null=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.TENANT)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    avatar_url = models.URLField(blank=True, null=True)

    is_phone_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)  # pyrefly: ignore [bad-override-mutable-attribute] # pyrefly: ignore
    is_staff = models.BooleanField(default=False)
    is_flagged_broker = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()
    DoesNotExist = ObjectDoesNotExist
    MultipleObjectsReturned = MultipleObjectsReturned

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['full_name']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.full_name} ({self.phone_number})"

    @property
    def is_landlord(self):
        return self.role in [self.Role.LANDLORD, self.Role.DUAL]

    @property
    def is_tenant(self):
        return self.role in [self.Role.TENANT, self.Role.DUAL]


class TenantProfile(TimeStampedUUIDModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='tenant_profile')
    occupation = models.CharField(max_length=120, blank=True, default='')
    workplace = models.CharField(max_length=150, blank=True, default='')
    family_size = models.PositiveSmallIntegerField(default=1)
    nid_number = models.CharField(max_length=50, blank=True, default='')
    is_nid_verified = models.BooleanField(default=False)
    rental_rating = models.FloatField(default=5.0)
    completed_rentals = models.PositiveIntegerField(default=0)
    emergency_contact = models.CharField(max_length=20, blank=True, default='')

    objects = models.Manager()

    def __str__(self):
        return f"Tenant: {self.user.full_name}"


class LandlordProfile(TimeStampedUUIDModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='landlord_profile')
    nid_number = models.CharField(max_length=50, blank=True, default='')
    nid_front = models.ImageField(upload_to='nid_docs/', blank=True, null=True)
    nid_back = models.ImageField(upload_to='nid_docs/', blank=True, null=True)
    selfie_image = models.ImageField(upload_to='nid_docs/', blank=True, null=True)
    is_nid_verified = models.BooleanField(default=False)
    is_owner_verified = models.BooleanField(default=False)
    rental_rating = models.FloatField(default=4.8)
    total_listings = models.PositiveIntegerField(default=0)

    objects = models.Manager()

    def __str__(self):
        return f"Landlord: {self.user.full_name}"


class OTPVerification(TimeStampedUUIDModel):
    phone_number = models.CharField(max_length=20, db_index=True)
    otp_code = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)
    expires_at = models.DateTimeField()

    objects = models.Manager()

    class Meta:
        indexes = [
            models.Index(fields=['phone_number', 'is_verified', 'expires_at']),
        ]

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"OTP for {self.phone_number}: {self.otp_code}"
