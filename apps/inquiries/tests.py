from datetime import date, timedelta
from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

try:
    from apps.accounts.models import User, TenantProfile, LandlordProfile
except (ImportError, ModuleNotFoundError):
    from ..accounts.models import User, TenantProfile, LandlordProfile

from .models import Inquiry, VisitBooking

try:
    from apps.properties.models import Property
except (ImportError, ModuleNotFoundError):
    from ..properties.models import Property


class InquiryAndScreeningTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Landlord
        self.landlord = User.objects.create_user(
            phone_number='+8801711111111',
            full_name='Landlord Kamal',
            role=User.Role.LANDLORD,
        )
        self.landlord_profile = self.landlord.landlord_profile
        self.landlord_profile.is_nid_verified = True
        self.landlord_profile.is_owner_verified = True
        self.landlord_profile.save()

        # Tenant
        self.tenant = User.objects.create_user(
            phone_number='+8801822222222',
            full_name='Tenant Sakib',
            role=User.Role.TENANT,
        )
        self.tenant_profile = self.tenant.tenant_profile
        self.tenant_profile.occupation = 'Software Engineer'
        self.tenant_profile.workplace = 'InnoSpace InfoTech'
        self.tenant_profile.family_size = 3
        self.tenant_profile.is_nid_verified = True
        self.tenant_profile.rental_rating = 4.9
        self.tenant_profile.save()


        # Property
        self.property = Property.objects.create(
            landlord=self.landlord,
            title='2-Bed Family Apartment in Mirpur',
            description='Close to Metro Station Gate 2',
            rent_amount=Decimal('22000.00'),
            security_deposit=Decimal('44000.00'),
            area_neighborhood='Mirpur 10',
            full_address='Section 10, Mirpur, Dhaka',
        )

    def test_tenant_submit_inquiry_with_snapshot(self):
        self.client.force_authenticate(user=self.tenant)
        url = reverse('inquiry-create')
        payload = {
            'property_id': str(self.property.id),
            'message': 'Hello, we are interested in moving in from next month.',
        }
        res = self.client.post(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['tenant_occupation'], 'Software Engineer')
        self.assertEqual(res.data['tenant_workplace'], 'InnoSpace InfoTech')
        self.assertEqual(res.data['tenant_family_size'], 3)
        self.assertTrue(res.data['tenant_is_nid_verified'])

    def test_landlord_screening_inbox(self):
        # Create an inquiry first
        Inquiry.objects.create(
            property=self.property,
            tenant=self.tenant,
            message='Would like to view the flat.',
            tenant_occupation='Software Engineer',
            tenant_workplace='InnoSpace InfoTech',
            tenant_family_size=3,
            tenant_is_nid_verified=True,
            tenant_rental_rating=4.9,
        )

        self.client.force_authenticate(user=self.landlord)
        url = reverse('landlord-inbox')
        res = self.client.get(url, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['tenant_name'], 'Tenant Sakib')
        self.assertEqual(res.data[0]['status'], 'PENDING')

    def test_landlord_accept_inquiry(self):
        inquiry = Inquiry.objects.create(
            property=self.property,
            tenant=self.tenant,
            message='Please accept my inquiry.',
        )

        self.client.force_authenticate(user=self.landlord)
        url = reverse('inquiry-status-update', kwargs={'pk': inquiry.id})
        res = self.client.patch(url, {'status': 'ACCEPTED'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['status'], 'ACCEPTED')

    def test_visit_scheduler_in_person_and_video_tour(self):
        self.client.force_authenticate(user=self.tenant)
        url = reverse('visit-bookings')

        # Schedule live video tour
        payload = {
            'property_id': str(self.property.id),
            'booking_type': 'VIDEO_TOUR',
            'scheduled_date': str(date.today() + timedelta(days=2)),
            'time_slot': '04:00 PM - 05:00 PM',
            'notes': 'Please show balcony and master washroom.',
        }
        res = self.client.post(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['booking_type'], 'VIDEO_TOUR')
        booking_id = res.data['id']

        # Landlord confirms and sets video call link
        self.client.force_authenticate(user=self.landlord)
        status_url = reverse('visit-booking-status', kwargs={'pk': booking_id})
        update_res = self.client.patch(
            status_url,
            {
                'status': 'CONFIRMED',
                'video_call_link': 'https://meet.rentbd.app/room-8821',
            },
            format='json'
        )
        self.assertEqual(update_res.status_code, status.HTTP_200_OK)
        self.assertEqual(update_res.data['status'], 'CONFIRMED')
        self.assertEqual(update_res.data['video_call_link'], 'https://meet.rentbd.app/room-8821')
