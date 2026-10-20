from rest_framework import serializers
from .models import Inquiry, VisitBooking
try:
    from apps.properties.models import Property
except (ImportError, ModuleNotFoundError):
    from ..properties.models import Property

try:
    from apps.common.utils import mask_phone_number
except (ImportError, ModuleNotFoundError):
    from ..common.utils import mask_phone_number


class InquirySerializer(serializers.ModelSerializer):
    property_id = serializers.CharField(source='property.id', read_only=True)
    property_title = serializers.CharField(source='property.title', read_only=True)
    tenant_id = serializers.CharField(source='tenant.id', read_only=True)
    tenant_name = serializers.CharField(source='tenant.full_name', read_only=True)
    tenant_phone_masked = serializers.SerializerMethodField()

    class Meta:
        model = Inquiry
        fields = [
            'id',
            'property_id',
            'property_title',
            'tenant_id',
            'tenant_name',
            'tenant_phone_masked',
            'tenant_occupation',
            'tenant_workplace',
            'tenant_family_size',
            'tenant_is_nid_verified',
            'tenant_rental_rating',
            'message',
            'status',
            'created_at',
        ]
        read_only_fields = fields

    def get_tenant_phone_masked(self, obj) -> str:
        if obj.status == Inquiry.Status.ACCEPTED:
            return obj.tenant.phone_number
        return mask_phone_number(obj.tenant.phone_number)


class InquiryCreateSerializer(serializers.Serializer):
    property_id = serializers.UUIDField()
    message = serializers.CharField(required=False, allow_blank=True, default='')

    def create(self, validated_data):
        tenant = self.context['request'].user
        property_obj = Property.objects.get(id=validated_data['property_id'])

        tp = getattr(tenant, 'tenant_profile', None)
        occupation = tp.occupation if tp else ''
        workplace = tp.workplace if tp else ''
        family_size = tp.family_size if tp else 1
        is_nid_verified = tp.is_nid_verified if tp else False
        rental_rating = tp.rental_rating if tp else 5.0

        inquiry = Inquiry.objects.create(
            property=property_obj,
            tenant=tenant,
            message=validated_data.get('message', ''),
            tenant_occupation=occupation,
            tenant_workplace=workplace,
            tenant_family_size=family_size,
            tenant_is_nid_verified=is_nid_verified,
            tenant_rental_rating=rental_rating,
        )
        return inquiry


class InquiryStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=[Inquiry.Status.ACCEPTED, Inquiry.Status.DECLINED])


class VisitBookingSerializer(serializers.ModelSerializer):
    property_id = serializers.CharField(source='property.id', read_only=True)
    property_title = serializers.CharField(source='property.title', read_only=True)
    tenant_name = serializers.CharField(source='tenant.full_name', read_only=True)

    class Meta:
        model = VisitBooking
        fields = [
            'id',
            'property_id',
            'property_title',
            'tenant_name',
            'booking_type',
            'scheduled_date',
            'time_slot',
            'status',
            'video_call_link',
            'notes',
            'created_at',
        ]
        read_only_fields = ['id', 'property_id', 'property_title', 'tenant_name', 'created_at']


class VisitBookingCreateSerializer(serializers.ModelSerializer):
    property_id = serializers.UUIDField()

    class Meta:
        model = VisitBooking
        fields = [
            'property_id',
            'booking_type',
            'scheduled_date',
            'time_slot',
            'notes',
        ]

    def create(self, validated_data):
        property_id = validated_data.pop('property_id')
        property_obj = Property.objects.get(id=property_id)
        tenant = self.context['request'].user

        return VisitBooking.objects.create(
            property=property_obj,
            tenant=tenant,
            **validated_data,
        )


class VisitBookingStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=VisitBooking.Status.choices, required=False)
    video_call_link = serializers.URLField(required=False, allow_blank=True)
