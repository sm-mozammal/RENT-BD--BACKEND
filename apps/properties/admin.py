from django.contrib import admin
from .models import Property, PropertyImage, SavedProperty


class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'area_neighborhood',
        'tenant_category',
        'property_type',
        'rent_amount',
        'is_available',
        'is_owner_verified',
        'created_at',
    )
    list_filter = ('tenant_category', 'property_type', 'is_available', 'fair_price_status', 'area_neighborhood')
    search_fields = ('title', 'area_neighborhood', 'full_address', 'landlord__phone_number', 'landlord__full_name')
    inlines = [PropertyImageInline]


@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = ('property', 'room_type', 'is_geo_tagged', 'captured_at')
    list_filter = ('room_type', 'is_geo_tagged')


@admin.register(SavedProperty)
class SavedPropertyAdmin(admin.ModelAdmin):
    list_display = ('user', 'property', 'created_at')
