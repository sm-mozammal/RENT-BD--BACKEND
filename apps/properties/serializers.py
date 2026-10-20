from rest_framework import serializers
from .models import Property, PropertyImage, SavedProperty, SavedSearch, SavedSearchAlert


class PropertyImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = PropertyImage
        fields = [
            'id',
            'image_url',
            'room_type',
            'is_geo_tagged',
            'captured_at',
        ]

    def get_image_url(self, obj) -> str:
        try:
            if bool(getattr(obj, 'image', None)):
                url = getattr(obj.image, 'url', None)
                if url:
                    request = self.context.get('request')
                    return request.build_absolute_uri(url) if request else str(url)
        except (ValueError, AttributeError):
            pass
        return str(getattr(obj, 'image_url', '') or '')


class PropertySerializer(serializers.ModelSerializer):
    landlord_id = serializers.CharField(source='landlord.id', read_only=True)
    landlord_name = serializers.CharField(read_only=True)
    landlord_phone_masked = serializers.CharField(read_only=True)
    landlord_is_nid_verified = serializers.BooleanField(read_only=True)
    landlord_rating = serializers.FloatField(read_only=True)
    images = PropertyImageSerializer(many=True, read_only=True)
    alley_width_feet = serializers.FloatField(source='alleyWidthFeet', required=False)
    is_saved = serializers.SerializerMethodField()
    total_move_in_cost = serializers.FloatField(read_only=True)

    class Meta:
        model = Property
        fields = [
            'id',
            'landlord_id',
            'landlord_name',
            'landlord_phone_masked',
            'landlord_is_nid_verified',
            'landlord_rating',
            'title',
            'description',
            'property_type',
            'tenant_category',
            'rent_amount',
            'security_deposit',
            'service_charge',
            'estimated_utilities',
            'bedrooms',
            'bathrooms',
            'balconies',
            'square_feet',
            'floor_level',
            'total_floors',
            'latitude',
            'longitude',
            'area_neighborhood',
            'full_address',
            'images',
            'has_geo_tagged_photos',
            'status',
            'is_available',
            'is_owner_verified',
            'fair_price_status',
            'fair_price_percent_diff',
            'area_average_rent',
            'alley_width_feet',
            'gas_supply',
            'waterlogging_risk',
            'water_quality',
            'night_safety_rating',
            'is_saved',
            'total_move_in_cost',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'landlord_id',
            'landlord_name',
            'landlord_phone_masked',
            'landlord_is_nid_verified',
            'landlord_rating',
            'has_geo_tagged_photos',
            'is_owner_verified',
            'fair_price_status',
            'fair_price_percent_diff',
            'area_average_rent',
            'night_safety_rating',
            'is_saved',
            'total_move_in_cost',
            'created_at',
        ]

    def get_is_saved(self, obj) -> bool:
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return SavedProperty.objects.filter(user=request.user, property=obj).exists()
        return False


class QuickPostSerializer(serializers.ModelSerializer):
    """
    Serializer for the 60-second landlord quick post flow.
    """
    photo_urls = serializers.ListField(
        child=serializers.URLField(),
        required=False,
        default=list,
    )

    class Meta:
        model = Property
        fields = [
            'title',
            'description',
            'property_type',
            'tenant_category',
            'rent_amount',
            'security_deposit',
            'service_charge',
            'estimated_utilities',
            'bedrooms',
            'bathrooms',
            'balconies',
            'square_feet',
            'floor_level',
            'total_floors',
            'latitude',
            'longitude',
            'area_neighborhood',
            'full_address',
            'photo_urls',
        ]

    def create(self, validated_data):
        photo_urls = validated_data.pop('photo_urls', [])
        landlord = self.context['request'].user
        property_obj = Property.objects.create(landlord=landlord, **validated_data)

        for idx, url in enumerate(photo_urls):
            category = PropertyImage.RoomType.LIVING_ROOM
            if idx == 0:
                category = PropertyImage.RoomType.LIVING_ROOM
            elif idx == 1:
                category = PropertyImage.RoomType.BEDROOM
            elif idx == 2:
                category = PropertyImage.RoomType.KITCHEN

            PropertyImage.objects.create(
                property=property_obj,
                image_url=url,
                room_type=category,
                is_geo_tagged=True,
            )

        return property_obj


class AIListingGenerateRequestSerializer(serializers.Serializer):
    bedrooms = serializers.IntegerField(default=2)
    bathrooms = serializers.IntegerField(default=2)
    area = serializers.CharField(default='Mirpur 10')
    tenant_category = serializers.ChoiceField(
        choices=Property.TenantCategory.choices,
        default=Property.TenantCategory.FAMILY,
    )
    amenities = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list,
    )


class PropertyPhotoUploadSerializer(serializers.Serializer):
    image = serializers.ImageField(required=True)
    room_type = serializers.ChoiceField(
        choices=PropertyImage.RoomType.choices,
        default=PropertyImage.RoomType.LIVING_ROOM,
        required=False,
    )


class SavedSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedSearch
        fields = [
            'id',
            'name',
            'area',
            'tenant_category',
            'min_rent',
            'max_rent',
            'bedrooms',
            'push_alerts_enabled',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class SavedSearchAlertSerializer(serializers.ModelSerializer):
    property_id = serializers.UUIDField(source='property.id', read_only=True)
    property_title = serializers.CharField(source='property.title', read_only=True)
    property_rent = serializers.DecimalField(source='property.rent_amount', max_digits=10, decimal_places=2, read_only=True)
    property_area = serializers.CharField(source='property.area_neighborhood', read_only=True)

    class Meta:
        model = SavedSearchAlert
        fields = [
            'id',
            'saved_search',
            'property_id',
            'property_title',
            'property_rent',
            'property_area',
            'title',
            'message',
            'is_read',
            'created_at',
        ]
        read_only_fields = ['id', 'title', 'message', 'created_at']


class PropertyCompareRequestSerializer(serializers.Serializer):
    property_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=2,
        max_length=3,
        help_text="List of 2 to 3 property UUIDs to compare side-by-side"
    )
    destination_lat = serializers.FloatField(required=False, allow_null=True)
    destination_lng = serializers.FloatField(required=False, allow_null=True)
    destination_name = serializers.CharField(required=False, default='Daily Destination')



class MoveInCostCalculatorSerializer(serializers.Serializer):
    property_id = serializers.UUIDField(required=False)
    rent_amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    security_deposit = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    service_charge = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default=3000.0)
    estimated_utilities = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default=2000.0)
    moving_distance_km = serializers.FloatField(default=8.0)
    truck_type = serializers.ChoiceField(
        choices=['PICKUP_SMALL', 'MEDIUM_TRUCK', 'COVERED_VAN'],
        default='PICKUP_SMALL',
    )
    needs_labour = serializers.BooleanField(default=True)


class DrawSearchSerializer(serializers.Serializer):
    polygon = serializers.ListField(
        child=serializers.ListField(child=serializers.FloatField(), min_length=2, max_length=2),
        min_length=3,
        help_text="List of [latitude, longitude] pairs representing the freehand polygon"
    )


class CommuteCalculatorRequestSerializer(serializers.Serializer):
    property_id = serializers.UUIDField()
    destination_lat = serializers.FloatField()
    destination_lng = serializers.FloatField()
    destination_name = serializers.CharField(default='Office / Campus')
    travel_mode = serializers.ChoiceField(
        choices=['METRO_TRANSIT', 'DRIVING', 'WALKING', 'RICKSHAW_CNG'],
        default='METRO_TRANSIT',
    )


class AIPhotoClassifierSerializer(serializers.Serializer):
    image = serializers.ImageField(required=False)
    image_url = serializers.URLField(required=False)


class AIRentAgreementRequestSerializer(serializers.Serializer):
    property_id = serializers.UUIDField()
    tenant_name = serializers.CharField(max_length=120)
    tenant_phone = serializers.CharField(max_length=20)
    tenant_nid = serializers.CharField(max_length=50)
    agreed_rent = serializers.DecimalField(max_digits=10, decimal_places=2)
    security_deposit = serializers.DecimalField(max_digits=10, decimal_places=2)
    start_date = serializers.DateField()
    duration_months = serializers.IntegerField(default=12)
    special_conditions = serializers.CharField(required=False, allow_blank=True, default='')


class ListingAvailabilityConfirmSerializer(serializers.Serializer):
    is_available = serializers.BooleanField(default=True)


class MonetizationBoostSerializer(serializers.Serializer):
    property_id = serializers.UUIDField()
    duration_days = serializers.IntegerField(default=7)
    payment_method = serializers.ChoiceField(choices=['BKASH', 'NAGAD', 'UPAY', 'CARD'], default='BKASH')


class PartnerServiceBookingSerializer(serializers.Serializer):
    service_type = serializers.ChoiceField(
        choices=['PACKERS_MOVERS', 'HOME_CLEANING', 'DEEP_PAINTING', 'ELECTRICIAN_PLUMBER'],
        default='PACKERS_MOVERS',
    )
    property_address = serializers.CharField(max_length=255)
    scheduled_date = serializers.DateField()
    contact_phone = serializers.CharField(max_length=20)
    notes = serializers.CharField(required=False, allow_blank=True, default='')


class SpamDetectorRequestSerializer(serializers.Serializer):
    property_id = serializers.UUIDField(required=False)
    rent_amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default=20000.0)
    title = serializers.CharField(required=False, allow_blank=True, default='')
    description = serializers.CharField(required=False, allow_blank=True, default='')


class AISearchRequestSerializer(serializers.Serializer):
    q = serializers.CharField(required=False, allow_blank=True, default='', help_text="Natural language or voice search query")
    query = serializers.CharField(required=False, allow_blank=True, default='', help_text="Alternative query field")


