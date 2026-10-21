from rest_framework import serializers
from .models import User, TenantProfile, LandlordProfile
try:
    from apps.common.utils import is_valid_bangladesh_phone, normalize_bangladesh_phone
except (ImportError, ModuleNotFoundError):
    from ..common.utils import is_valid_bangladesh_phone, normalize_bangladesh_phone


class OTPRequestSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20)

    def validate_phone_number(self, value):
        if not is_valid_bangladesh_phone(value):
            raise serializers.ValidationError(
                'Invalid Bangladesh mobile number. Please use a valid 11-digit number (e.g. 017XXXXXXXX).'
            )
        return normalize_bangladesh_phone(value)


class RoleChoiceField(serializers.ChoiceField):
    """
    Case-insensitive choice field supporting 'tenant', 'TENANT', 'landlord', 'LANDLORD', 'dual', 'DUAL'.
    """
    def to_internal_value(self, data):
        if isinstance(data, str):
            data = data.strip().lower()
        return super().to_internal_value(data)


class OTPVerifySerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20)
    otp_code = serializers.CharField(max_length=6, min_length=4)
    full_name = serializers.CharField(max_length=120, required=False, allow_blank=True)
    role = RoleChoiceField(choices=User.Role.choices, required=False, default=User.Role.TENANT)

    def validate_phone_number(self, value):
        if not is_valid_bangladesh_phone(value):
            raise serializers.ValidationError('Invalid Bangladesh mobile number.')
        return normalize_bangladesh_phone(value)


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Unified User Profile Serializer matching the Flutter UserProfile domain entity.
    Provides both camelCase and snake_case compatibility.
    """
    phoneNumber = serializers.CharField(source='phone_number', read_only=True)
    fullName = serializers.CharField(source='full_name')
    avatarUrl = serializers.SerializerMethodField()
    occupation = serializers.SerializerMethodField()
    workplace = serializers.SerializerMethodField()
    familySize = serializers.SerializerMethodField()
    nidNumber = serializers.SerializerMethodField()
    isNidVerified = serializers.SerializerMethodField()
    rentalRating = serializers.SerializerMethodField()
    completedRentals = serializers.SerializerMethodField()
    isLandlord = serializers.BooleanField(source='is_landlord', read_only=True)
    isTenant = serializers.BooleanField(source='is_tenant', read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'phoneNumber',
            'fullName',
            'email',
            'role',
            'avatarUrl',
            'occupation',
            'workplace',
            'familySize',
            'nidNumber',
            'isNidVerified',
            'rentalRating',
            'completedRentals',
            'isLandlord',
            'isTenant',
            # snake_case versions
            'phone_number',
            'full_name',
            'is_phone_verified',
            'is_staff',
            'is_superuser',
            'is_flagged_broker',
            'date_joined',
        ]
        read_only_fields = ['id', 'phoneNumber', 'phone_number', 'is_phone_verified', 'date_joined']

    def get_avatarUrl(self, obj) -> str:
        try:
            if bool(getattr(obj, 'avatar', None)):
                url = getattr(obj.avatar, 'url', None)
                if url:
                    request = self.context.get('request')
                    return request.build_absolute_uri(url) if request else str(url)
        except (ValueError, AttributeError):
            pass
        return str(getattr(obj, 'avatar_url', '') or '')

    def get_occupation(self, obj) -> str:
        return getattr(getattr(obj, 'tenant_profile', None), 'occupation', '')

    def get_workplace(self, obj) -> str:
        return getattr(getattr(obj, 'tenant_profile', None), 'workplace', '')

    def get_familySize(self, obj) -> int:
        return getattr(getattr(obj, 'tenant_profile', None), 'family_size', 1)

    def get_nidNumber(self, obj) -> str:
        tenant_nid = getattr(getattr(obj, 'tenant_profile', None), 'nid_number', '')
        landlord_nid = getattr(getattr(obj, 'landlord_profile', None), 'nid_number', '')
        return tenant_nid or landlord_nid or ''

    def get_isNidVerified(self, obj) -> bool:
        t_verified = getattr(getattr(obj, 'tenant_profile', None), 'is_nid_verified', False)
        l_verified = getattr(getattr(obj, 'landlord_profile', None), 'is_nid_verified', False)
        return t_verified or l_verified

    def get_rentalRating(self, obj) -> float:
        if obj.is_landlord and hasattr(obj, 'landlord_profile'):
            return obj.landlord_profile.rental_rating
        elif hasattr(obj, 'tenant_profile'):
            return obj.tenant_profile.rental_rating
        return 5.0

    def get_completedRentals(self, obj) -> int:
        if hasattr(obj, 'tenant_profile'):
            return obj.tenant_profile.completed_rentals
        return 0


class ProfileUpdateSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=120, required=False)
    role = RoleChoiceField(choices=User.Role.choices, required=False)
    occupation = serializers.CharField(max_length=120, required=False, allow_blank=True)
    workplace = serializers.CharField(max_length=150, required=False, allow_blank=True)
    family_size = serializers.IntegerField(min_value=1, required=False)
    emergency_contact = serializers.CharField(max_length=20, required=False, allow_blank=True)

    def update(self, instance, validated_data):
        if 'full_name' in validated_data:
            instance.full_name = validated_data['full_name']
        if 'role' in validated_data:
            instance.role = validated_data['role']
        instance.save()

        # Update tenant profile fields
        tenant_profile = getattr(instance, 'tenant_profile', None)
        if tenant_profile:
            if 'occupation' in validated_data:
                tenant_profile.occupation = validated_data['occupation']
            if 'workplace' in validated_data:
                tenant_profile.workplace = validated_data['workplace']
            if 'family_size' in validated_data:
                tenant_profile.family_size = validated_data['family_size']
            if 'emergency_contact' in validated_data:
                tenant_profile.emergency_contact = validated_data['emergency_contact']
            tenant_profile.save()

        return instance


class RegisterSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=120)
    phone_number = serializers.CharField(max_length=20)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(min_length=6, write_only=True)
    role = RoleChoiceField(choices=User.Role.choices, required=False, default=User.Role.TENANT)

    def validate_phone_number(self, value):
        if not is_valid_bangladesh_phone(value):
            raise serializers.ValidationError('Invalid Bangladesh mobile number.')
        normalized = normalize_bangladesh_phone(value)
        if User.objects.filter(phone_number=normalized).exists():
            raise serializers.ValidationError('An account with this mobile number already exists.')
        return normalized


class PasswordLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)
    phone_number = serializers.CharField(max_length=20, required=False, allow_blank=True, allow_null=True)
    password = serializers.CharField(write_only=True)
    role = RoleChoiceField(choices=User.Role.choices, required=False)

    def validate(self, attrs):
        email = attrs.get('email')
        phone_number = attrs.get('phone_number')
        if not email and not phone_number:
            raise serializers.ValidationError('Either email or phone_number must be provided.')
        if phone_number:
            if not is_valid_bangladesh_phone(phone_number):
                raise serializers.ValidationError({'phone_number': 'Invalid Bangladesh mobile number.'})
            attrs['phone_number'] = normalize_bangladesh_phone(phone_number)
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(min_length=6, write_only=True)


class RoleSwitchSerializer(serializers.Serializer):
    role = RoleChoiceField(choices=User.Role.choices)


class NIDVerifySerializer(serializers.Serializer):
    nid_number = serializers.CharField(max_length=50)
    nid_front = serializers.FileField(required=False, allow_null=True)
    nid_back = serializers.FileField(required=False, allow_null=True)
    selfie = serializers.FileField(required=False, allow_null=True)
    nid_front_url = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    nid_back_url = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    selfie_url = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    present_address = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    emergency_contact = serializers.CharField(required=False, allow_null=True, allow_blank=True)
