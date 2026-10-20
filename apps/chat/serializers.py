from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from .models import ChatRoom, ChatMessage, MaskedCallSession
try:
    from apps.common.utils import mask_phone_number
except (ImportError, ModuleNotFoundError):
    from ..common.utils import mask_phone_number


class ChatMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.full_name', read_only=True)
    is_me = serializers.SerializerMethodField()

    class Meta:
        model = ChatMessage
        fields = [
            'id',
            'room',
            'sender',
            'sender_name',
            'message_text',
            'is_read',
            'is_me',
            'created_at',
        ]
        read_only_fields = ['id', 'sender', 'sender_name', 'is_me', 'created_at']

    def get_is_me(self, obj) -> bool:
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.sender == request.user
        return False


class ChatRoomSerializer(serializers.ModelSerializer):
    property_title = serializers.CharField(source='property.title', read_only=True)
    property_rent = serializers.FloatField(source='property.rent_amount', read_only=True)
    other_party_name = serializers.SerializerMethodField()
    other_party_phone_masked = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = [
            'id',
            'property',
            'property_title',
            'property_rent',
            'landlord',
            'tenant',
            'other_party_name',
            'other_party_phone_masked',
            'last_message',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields

    def get_other_party_name(self, obj) -> str:
        request = self.context.get('request')
        if request and request.user == obj.landlord:
            return obj.tenant.full_name
        return obj.landlord.full_name

    def get_other_party_phone_masked(self, obj) -> str:
        request = self.context.get('request')
        if request and request.user == obj.landlord:
            return mask_phone_number(obj.tenant.phone_number)
        return mask_phone_number(obj.landlord.phone_number)

    @extend_schema_field(serializers.DictField)
    def get_last_message(self, obj):
        last = obj.messages.order_by('-created_at').first()
        if last:
            return {
                'text': last.message_text,
                'created_at': last.created_at,
                'sender_name': last.sender.full_name,
            }
        return None


class ChatRoomCreateSerializer(serializers.Serializer):
    property_id = serializers.UUIDField()


class SendMessageSerializer(serializers.Serializer):
    message_text = serializers.CharField(min_length=1)


class MaskedCallSessionUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=MaskedCallSession.Status.choices,
        required=False,
    )
    duration_seconds = serializers.IntegerField(required=False, default=0)
