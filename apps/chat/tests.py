from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
try:
    from apps.accounts.models import User
except (ImportError, ModuleNotFoundError):
    from ..accounts.models import User

try:
    from apps.properties.models import Property
except (ImportError, ModuleNotFoundError):
    from ..properties.models import Property

from .models import ChatRoom, ChatMessage


class ChatApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.landlord = User.objects.create_user(phone_number='+8801711002200', full_name='Owner Kamal')
        self.tenant = User.objects.create_user(phone_number='+8801811002200', full_name='Tenant Salman')
        self.prop = Property.objects.create(
            landlord=self.landlord,
            title='1-Bed Bachelor Sublet',
            rent_amount=Decimal('9000.00'),
            security_deposit=Decimal('9000.00'),
            area_neighborhood='Mirpur 2',
            full_address='Mirpur 2, Dhaka',
        )

    def test_create_and_list_chat_rooms(self):
        self.client.force_authenticate(user=self.tenant)
        url = reverse('chat-rooms')
        res = self.client.post(url, {'property_id': str(self.prop.id)}, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        room_id = res.data['id']

        list_res = self.client.get(url, format='json')
        self.assertEqual(list_res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_res.data), 1)

    def test_send_and_read_messages(self):
        room = ChatRoom.objects.create(property=self.prop, landlord=self.landlord, tenant=self.tenant)
        self.client.force_authenticate(user=self.tenant)

        msg_url = reverse('chat-messages', kwargs={'pk': room.id})
        send_res = self.client.post(msg_url, {'message_text': 'Assalamu Alaikum, is the flat vacant?'}, format='json')
        self.assertEqual(send_res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(send_res.data['message_text'], 'Assalamu Alaikum, is the flat vacant?')

        # Landlord reads message
        self.client.force_authenticate(user=self.landlord)
        get_res = self.client.get(msg_url, format='json')
        self.assertEqual(get_res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(get_res.data), 1)

    def test_masked_call_token_generation(self):
        room = ChatRoom.objects.create(property=self.prop, landlord=self.landlord, tenant=self.tenant)
        self.client.force_authenticate(user=self.tenant)

        call_url = reverse('chat-call-token', kwargs={'pk': room.id})
        call_res = self.client.post(call_url, format='json')
        self.assertEqual(call_res.status_code, status.HTTP_200_OK)
        self.assertTrue(call_res.data['success'])
        self.assertIn('agora_rtc_token', call_res.data)
        self.assertIn('channel_name', call_res.data)
        # Verify phone is masked
        self.assertIn('••', call_res.data['receiver_phone_masked'])

    def test_masked_call_session_lifecycle(self):
        room = ChatRoom.objects.create(property=self.prop, landlord=self.landlord, tenant=self.tenant)
        self.client.force_authenticate(user=self.tenant)

        call_url = reverse('chat-call-token', kwargs={'pk': room.id})
        call_res = self.client.post(call_url, format='json')
        self.assertEqual(call_res.status_code, status.HTTP_200_OK)
        session_id = call_res.data['session_id']

        # Update session to ENDED with 120 seconds duration
        update_url = reverse('chat-call-update', kwargs={'pk': session_id})
        update_res = self.client.patch(update_url, {'status': 'ENDED', 'duration_seconds': 120}, format='json')
        self.assertEqual(update_res.status_code, status.HTTP_200_OK)
        self.assertEqual(update_res.data['status'], 'ENDED')
        self.assertEqual(update_res.data['duration_seconds'], 120)

