from django.contrib import admin
from apps.inquiries.models import Inquiry, VisitBooking


@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ('property', 'tenant', 'status', 'tenant_occupation', 'tenant_is_nid_verified', 'created_at')
    list_filter = ('status', 'tenant_is_nid_verified')
    search_fields = ('property__title', 'tenant__phone_number', 'tenant__full_name')


@admin.register(VisitBooking)
class VisitBookingAdmin(admin.ModelAdmin):
    list_display = ('property', 'tenant', 'booking_type', 'scheduled_date', 'time_slot', 'status')
    list_filter = ('booking_type', 'status', 'scheduled_date')
    search_fields = ('property__title', 'tenant__phone_number', 'tenant__full_name')
