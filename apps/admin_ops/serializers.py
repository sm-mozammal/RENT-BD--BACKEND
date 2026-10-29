from decimal import Decimal
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

from apps.accounts.models import User
from apps.properties.models import Property
from apps.ledger.models import RentBill
from .models import NIDVerificationRequest, GeoPhotoVerification, SpamReport


class AdminOverviewStatsSerializer(serializers.Serializer):
    total_users = serializers.IntegerField()
    users_growth_pct = serializers.FloatField()
    active_listings = serializers.IntegerField()
    listings_growth_pct = serializers.FloatField()
    pending_nid_count = serializers.IntegerField()
    pending_geo_count = serializers.IntegerField(required=False)
    pending_spam_count = serializers.IntegerField()
    pending_property_count = serializers.IntegerField(required=False)
    total_revenue_bdt = serializers.DecimalField(max_digits=12, decimal_places=2)
    revenue_growth_pct = serializers.FloatField()
    rent_agreements_generated = serializers.IntegerField()
    average_monthly_rent_bdt = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    fair_rent_breakdown = serializers.DictField()
    category_breakdown = serializers.DictField()
    monthly_revenue_history = serializers.ListField(child=serializers.DictField())
    users_analytics = serializers.DictField(required=False)
    properties_analytics = serializers.DictField(required=False)
    finance_analytics = serializers.DictField(required=False)
    top_demand_supply_areas = serializers.ListField(child=serializers.DictField(), required=False)
    recent_activity = serializers.DictField(required=False)


class AdminDashboardAnalyticsSerializer(AdminOverviewStatsSerializer):
    """Full comprehensive analytics serializer for Admin Dashboard."""
    pass


class NIDVerificationRequestSerializer(serializers.ModelSerializer):
    landlord_id = serializers.CharField(source='landlord.id', read_only=True)
    landlord_name = serializers.CharField(source='landlord.full_name', read_only=True)
    landlord_phone = serializers.CharField(source='landlord.phone_number', read_only=True)
    landlord_email = serializers.CharField(source='landlord.email', read_only=True)
    submitted_at = serializers.DateTimeField(source='created_at', read_only=True)

    class Meta:
        model = NIDVerificationRequest
        fields = [
            'id',
            'landlord_id',
            'landlord_name',
            'landlord_phone',
            'landlord_email',
            'nid_number',
            'nid_type',
            'nid_front_url',
            'nid_back_url',
            'live_selfie_url',
            'ai_face_match_confidence',
            'extracted_data',
            'status',
            'submitted_at',
            'reviewer_notes',
            'rejection_reason',
            'reviewed_by',
            'reviewed_at',
        ]


class NIDApproveSerializer(serializers.Serializer):
    notes = serializers.CharField(required=False, allow_blank=True, default='')


class NIDRejectSerializer(serializers.Serializer):
    reason = serializers.CharField(required=True)


class GeoPhotoVerificationSerializer(serializers.ModelSerializer):
    property_id = serializers.CharField(source='property.id', read_only=True)
    property_title = serializers.CharField(source='property.title', read_only=True)
    property_coordinates = serializers.SerializerMethodField()
    exif_coordinates = serializers.SerializerMethodField()

    class Meta:
        model = GeoPhotoVerification
        fields = [
            'id',
            'property_id',
            'property_title',
            'landlord_name',
            'landlord_phone',
            'photo_url',
            'property_coordinates',
            'exif_coordinates',
            'distance_difference_meters',
            'accuracy_meters',
            'is_camera_live',
            'status',
            'created_at',
        ]

    @extend_schema_field(serializers.DictField)
    def get_property_coordinates(self, obj):
        return {
            'lat': obj.property_lat,
            'lng': obj.property_lng,
            'address': obj.property_address or getattr(obj.property, 'full_address', ''),
        }

    @extend_schema_field(serializers.DictField)
    def get_exif_coordinates(self, obj):
        return {
            'lat': obj.exif_lat,
            'lng': obj.exif_lng,
        }


class GeoPhotoVerifySerializer(serializers.Serializer):
    approved = serializers.BooleanField(required=True)


class AdminPropertySerializer(serializers.ModelSerializer):
    landlord_name = serializers.CharField(source='landlord.full_name', read_only=True)
    landlord_phone = serializers.CharField(source='landlord.phone_number', read_only=True)

    class Meta:
        model = Property
        fields = [
            'id',
            'title',
            'description',
            'property_type',
            'tenant_category',
            'rent_amount',
            'security_deposit',
            'service_charge',
            'area_neighborhood',
            'full_address',
            'bedrooms',
            'bathrooms',
            'balconies',
            'square_feet',
            'floor_level',
            'total_floors',
            'status',
            'fair_price_status',
            'fair_price_percent_diff',
            'has_geo_tagged_photos',
            'is_available',
            'is_featured',
            'landlord_name',
            'landlord_phone',
            'created_at',
        ]


class PropertyStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=['active', 'pending_approval', 'flagged_spam', 'rented', 'rejected']
    )


class SpamReportSerializer(serializers.ModelSerializer):
    property_id = serializers.CharField(source='property.id', read_only=True)
    property_title = serializers.CharField(source='property.title', read_only=True)

    class Meta:
        model = SpamReport
        fields = [
            'id',
            'property_id',
            'property_title',
            'landlord_name',
            'landlord_phone',
            'rent_bdt',
            'average_area_rent',
            'flags',
            'ai_confidence_score',
            'duplicate_match',
            'status',
            'created_at',
        ]


class SpamReportResolveSerializer(serializers.Serializer):
    action = serializers.ChoiceField(
        choices=['listing_banned', 'landlord_blocked', 'false_positive']
    )


class AdminUserSerializer(serializers.ModelSerializer):
    listings_count = serializers.SerializerMethodField()
    nid_status = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'phone_number',
            'full_name',
            'email',
            'role',
            'is_phone_verified',
            'is_staff',
            'is_superuser',
            'is_flagged_broker',
            'date_joined',
            'listings_count',
            'nid_status',
        ]

    def get_listings_count(self, obj) -> int:
        return getattr(obj, 'properties', None).count() if hasattr(obj, 'properties') else 0

    def get_nid_status(self, obj) -> str:
        if hasattr(obj, 'landlord_profile'):
            return 'verified' if obj.landlord_profile.is_nid_verified else 'unverified'
        if hasattr(obj, 'tenant_profile'):
            return 'verified' if obj.tenant_profile.is_nid_verified else 'unverified'
        return 'unverified'


class AdminLedgerSerializer(serializers.ModelSerializer):
    property_id = serializers.CharField(source='contract.property.id', read_only=True)
    property_title = serializers.CharField(source='contract.property.title', read_only=True)
    landlord_name = serializers.CharField(source='contract.landlord.full_name', read_only=True)
    tenant_name = serializers.CharField(source='contract.tenant.full_name', read_only=True)
    month = serializers.CharField(source='billing_month', read_only=True)
    base_rent_bdt = serializers.DecimalField(source='base_rent', max_digits=10, decimal_places=2, read_only=True)
    service_charge_bdt = serializers.DecimalField(source='service_charge', max_digits=10, decimal_places=2, read_only=True)
    total_paid_bdt = serializers.DecimalField(source='total_amount', max_digits=10, decimal_places=2, read_only=True)
    platform_fee_collected = serializers.SerializerMethodField()
    transaction_date = serializers.DateTimeField(source='paid_at', read_only=True)

    class Meta:
        model = RentBill
        fields = [
            'id',
            'property_id',
            'property_title',
            'landlord_name',
            'tenant_name',
            'month',
            'base_rent_bdt',
            'service_charge_bdt',
            'total_paid_bdt',
            'payment_method',
            'platform_fee_collected',
            'transaction_date',
            'status',
        ]

    def get_platform_fee_collected(self, obj) -> float:
        return float(obj.total_amount) * 0.015 if obj.total_amount else 0.0
