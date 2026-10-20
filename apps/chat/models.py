from django.conf import settings
from django.db import models
from django.utils import timezone
try:
    from apps.common.models import TimeStampedUUIDModel
except (ImportError, ModuleNotFoundError):
    from ..common.models import TimeStampedUUIDModel

try:
    from apps.properties.models import Property
except (ImportError, ModuleNotFoundError):
    from ..properties.models import Property


class ChatRoom(TimeStampedUUIDModel):
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='chat_rooms',
    )
    landlord = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='landlord_chats',
    )
    tenant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tenant_chats',
    )
    is_active = models.BooleanField(default=True)

    objects = models.Manager()

    class Meta:
        unique_together = ('property', 'tenant')
        ordering = ['-updated_at']

    def __str__(self):
        return f"Chat between {self.landlord.full_name} and {self.tenant.full_name} for {self.property.title}"


class ChatMessage(TimeStampedUUIDModel):
    room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name='messages',
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages',
    )
    message_text = models.TextField()
    is_read = models.BooleanField(default=False)

    objects = models.Manager()

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Message by {self.sender.full_name} at {self.created_at}"


class MaskedCallSession(TimeStampedUUIDModel):
    class Status(models.TextChoices):
        INITIATED = 'INITIATED', 'Initiated'
        CONNECTED = 'CONNECTED', 'Connected'
        ENDED = 'ENDED', 'Ended'
        MISSED = 'MISSED', 'Missed'

    room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name='call_sessions',
    )
    caller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='initiated_calls',
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_calls',
    )
    channel_name = models.CharField(max_length=120)
    agora_token = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.INITIATED)
    duration_seconds = models.PositiveIntegerField(default=0)

    objects = models.Manager()

    def __str__(self):
        return f"Masked call {self.caller.full_name} -> {self.receiver.full_name} ({self.status})"
