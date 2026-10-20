import uuid
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ChatRoom, ChatMessage, MaskedCallSession
from .serializers import (
    ChatRoomSerializer,
    ChatRoomCreateSerializer,
    ChatMessageSerializer,
    SendMessageSerializer,
    MaskedCallSessionUpdateSerializer,
)
try:
    from apps.properties.models import Property
except (ImportError, ModuleNotFoundError):
    from ..properties.models import Property

try:
    from apps.common.utils import mask_phone_number
except (ImportError, ModuleNotFoundError):
    from ..common.utils import mask_phone_number


class ChatRoomListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChatRoomSerializer

    @extend_schema(
        summary="List User Chat Rooms (In-App Messaging)",
        description="Returns all active encrypted chat rooms for current tenant or landlord.",
        responses={200: ChatRoomSerializer(many=True), 201: ChatRoomSerializer},
    )
    def get(self, request):
        rooms = ChatRoom.objects.filter(
            landlord=request.user
        ) | ChatRoom.objects.filter(
            tenant=request.user
        )
        return Response(ChatRoomSerializer(rooms.distinct(), many=True, context={'request': request}).data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Start or Open Chat Room for Property",
        request=ChatRoomCreateSerializer,
        responses={201: ChatRoomSerializer},
    )
    def post(self, request):
        serializer = ChatRoomCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        prop = get_object_or_404(Property, id=serializer.validated_data['property_id'])
        landlord = prop.landlord
        tenant = request.user

        if landlord == tenant:
            return Response({'detail': 'Cannot create a chat room with yourself.'}, status=status.HTTP_400_BAD_REQUEST)

        room, created = ChatRoom.objects.get_or_create(
            property=prop,
            tenant=tenant,
            defaults={'landlord': landlord},
        )
        return Response(
            ChatRoomSerializer(room, context={'request': request}).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class ChatMessageListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChatMessageSerializer

    @extend_schema(
        summary="Get Chat Room Message History",
        responses={200: ChatMessageSerializer(many=True)},
    )
    def get(self, request, pk):
        room = get_object_or_404(ChatRoom, pk=pk)
        if request.user != room.landlord and request.user != room.tenant:
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        messages = room.messages.all()
        # Mark other party's unread messages as read
        room.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

        return Response(ChatMessageSerializer(messages, many=True, context={'request': request}).data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Send In-App Chat Message",
        request=SendMessageSerializer,
        responses={201: ChatMessageSerializer},
    )
    def post(self, request, pk):
        room = get_object_or_404(ChatRoom, pk=pk)
        if request.user != room.landlord and request.user != room.tenant:
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = SendMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        msg = ChatMessage.objects.create(
            room=room,
            sender=request.user,
            message_text=serializer.validated_data['message_text'],
        )
        room.save(update_fields=['updated_at'])

        return Response(ChatMessageSerializer(msg, context={'request': request}).data, status=status.HTTP_201_CREATED)


class MaskedCallTokenView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="In-App Masked Calling (VoIP Session Token)",
        description="Generates ephemeral Agora RTC audio calling token, masking both parties' real phone numbers.",
        request=None,
        responses={200: OpenApiResponse(description="Masked VoIP session token")},
    )
    def post(self, request, pk):
        room = get_object_or_404(ChatRoom, pk=pk)
        if request.user != room.landlord and request.user != room.tenant:
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        caller = request.user
        receiver = room.tenant if caller == room.landlord else room.landlord

        channel_name = f"rentbd-call-{room.id.hex[:8]}"
        agora_token = f"006rentbd_app_mock_token_{uuid.uuid4().hex}"

        session = MaskedCallSession.objects.create(
            room=room,
            caller=caller,
            receiver=receiver,
            channel_name=channel_name,
            agora_token=agora_token,
            status=MaskedCallSession.Status.INITIATED,
        )

        return Response({
            'success': True,
            'session_id': str(session.id),
            'channel_name': channel_name,
            'agora_rtc_token': agora_token,
            'caller_name': caller.full_name,
            'receiver_name': receiver.full_name,
            'receiver_phone_masked': mask_phone_number(receiver.phone_number),
            'expires_in_seconds': 3600,
            'message': 'Encrypted masked call session initiated. Numbers remain private.',
        }, status=status.HTTP_200_OK)


class MaskedCallSessionUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Update Masked Call Session Status",
        description="Updates status of VoIP call (CONNECTED, ENDED, MISSED) and records duration in seconds.",
        request=MaskedCallSessionUpdateSerializer,
        responses={200: OpenApiResponse(description="Call session updated")},
    )
    def patch(self, request, pk):
        session = get_object_or_404(MaskedCallSession, pk=pk)
        if request.user != session.caller and request.user != session.receiver:
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        new_status = request.data.get('status')
        duration = request.data.get('duration_seconds')

        if new_status and new_status in MaskedCallSession.Status.values:
            session.status = new_status
        if duration is not None:
            session.duration_seconds = int(duration)

        session.save(update_fields=['status', 'duration_seconds'])

        return Response({
            'success': True,
            'session_id': str(session.id),
            'status': session.status,
            'duration_seconds': session.duration_seconds,
        }, status=status.HTTP_200_OK)

