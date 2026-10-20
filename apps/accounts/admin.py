from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, TenantProfile, LandlordProfile, OTPVerification


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'full_name', 'role', 'is_phone_verified', 'is_staff', 'date_joined')
    list_filter = ('role', 'is_phone_verified', 'is_staff')
    search_fields = ('phone_number', 'full_name', 'email')
    ordering = ('-date_joined',)


@admin.register(TenantProfile)
class TenantProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'occupation', 'workplace', 'family_size', 'is_nid_verified', 'rental_rating')
    search_fields = ('user__phone_number', 'user__full_name', 'occupation')


@admin.register(LandlordProfile)
class LandlordProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_nid_verified', 'is_owner_verified', 'rental_rating', 'total_listings')
    search_fields = ('user__phone_number', 'user__full_name')


@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'otp_code', 'is_verified', 'expires_at', 'created_at')
    search_fields = ('phone_number',)
