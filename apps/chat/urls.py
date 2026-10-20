from django.urls import path
from .views import (
    ChatRoomListCreateView,
    ChatMessageListCreateView,
    MaskedCallTokenView,
    MaskedCallSessionUpdateView,
)

urlpatterns = [
    path('rooms/', ChatRoomListCreateView.as_view(), name='chat-rooms'),
    path('rooms/<uuid:pk>/messages/', ChatMessageListCreateView.as_view(), name='chat-messages'),
    path('rooms/<uuid:pk>/call-token/', MaskedCallTokenView.as_view(), name='chat-call-token'),
    path('calls/<uuid:pk>/', MaskedCallSessionUpdateView.as_view(), name='chat-call-update'),
]

