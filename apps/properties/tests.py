from decimal import Decimal
from typing import Any
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient as _DRFAPIClient
try:
    from apps.accounts.models import User
except ImportError:
    from ..accounts.models import User
from .models import Property


class APIClient:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._client = _DRFAPIClient(*args, **kwargs)

    def force_authenticate(self, *args: Any, **kwargs: Any) -> Any:
        return self._client.force_authenticate(*args, **kwargs)

    def get(self, *args: Any, **kwargs: Any) -> Any:
        return self._client.get(*args, **kwargs)

    def post(self, *args: Any, **kwargs: Any) -> Any:
        return self._client.post(*args, **kwargs)

    def put(self, *args: Any, **kwargs: Any) -> Any:
        return self._client.put(*args, **kwargs)

    def patch(self, *args: Any, **kwargs: Any) -> Any:
        return self._client.patch(*args, **kwargs)

    def delete(self, *args: Any, **kwargs: Any) -> Any:
        return self._client.delete(*args, **kwargs)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._client, name)


class PropertyApiTests(TestCase):
    client: Any

    def setUp(self):
        self.client = APIClient()
        self.landlord = User.objects.create_user(
            phone_number='+8801700000001',
            full_name='Landlord Kabir',
            role=User.Role.LANDLORD,
        )
        self.landlord.landlord_profile.is_nid_verified = True
        self.landlord.landlord_profile.save(update_fields=['is_nid_verified'])
        self.tenant = User.objects.create_user(
            phone_number='+8801800000002',
            full_name='Tenant Rahim',
            role=User.Role.TENANT,
        )

        self.prop1 = Property.objects.create(
            landlord=self.landlord,
            title='2-Bed Bachelor Mirpur',
            description='Close to metro',
            tenant_category=Property.TenantCategory.BACHELOR_MALE,
            rent_amount=Decimal('15000.00'),
            security_deposit=Decimal('30000.00'),
            service_charge=Decimal('2000.00'),
            estimated_utilities=Decimal('1500.00'),
            area_neighborhood='Mirpur 10',
            full_address='Mirpur 10, Dhaka',
            is_available=True,
        )

        self.prop2 = Property.objects.create(
            landlord=self.landlord,
            title='3-Bed Family Uttara',
            description='Near park',
            tenant_category=Property.TenantCategory.FAMILY,
            rent_amount=Decimal('30000.00'),
            security_deposit=Decimal('60000.00'),
            area_neighborhood='Uttara Sector 4',
            full_address='Sector 4, Uttara, Dhaka',
            is_available=True,
        )

    def test_list_properties_with_bachelor_switch(self):
        url = reverse('property-list-create')
        res = self.client.get(url, {'tenant_category': 'bachelor'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Should only return bachelor friendly listings
        titles = [p['title'] for p in res.data]
        self.assertIn('2-Bed Bachelor Mirpur', titles)
        self.assertNotIn('3-Bed Family Uttara', titles)

    def test_list_properties_with_family_switch(self):
        url = reverse('property-list-create')
        res = self.client.get(url, {'tenant_category': 'family'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        titles = [p['title'] for p in res.data]
        self.assertIn('3-Bed Family Uttara', titles)
        self.assertNotIn('2-Bed Bachelor Mirpur', titles)

    def test_quick_post_property(self):
        self.client.force_authenticate(user=self.landlord)
        url = reverse('property-list-create')
        payload = {
            'title': 'New 2-Bed Flat',
            'description': 'Brand new',
            'property_type': 'APARTMENT',
            'tenant_category': 'FAMILY',
            'rent_amount': 22000.0,
            'security_deposit': 44000.0,
            'service_charge': 3000.0,
            'estimated_utilities': 2000.0,
            'bedrooms': 2,
            'bathrooms': 2,
            'balconies': 1,
            'square_feet': 1000,
            'floor_level': 3,
            'total_floors': 6,
            'latitude': 23.8103,
            'longitude': 90.4125,
            'area_neighborhood': 'Banani',
            'full_address': 'Road 11, Banani, Dhaka',
            'photo_urls': [
                'https://example.com/photo1.jpg',
                'https://example.com/photo2.jpg',
            ]
        }
        res = self.client.post(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['title'], 'New 2-Bed Flat')
        self.assertEqual(len(res.data['images']), 2)

    def test_quick_post_unverified_landlord_rejected(self):
        unverified_landlord = User.objects.create_user(
            phone_number='+8801700000099',
            full_name='Unverified Landlord',
            role=User.Role.LANDLORD,
        )
        unverified_landlord.landlord_profile.is_nid_verified = False
        unverified_landlord.landlord_profile.save(update_fields=['is_nid_verified'])

        self.client.force_authenticate(user=unverified_landlord)
        url = reverse('property-list-create')
        payload = {
            'title': 'Unverified Listing',
            'tenant_category': 'FAMILY',
            'rent_amount': 25000.0,
            'area_neighborhood': 'Dhanmondi',
            'full_address': 'Road 27, Dhanmondi, Dhaka',
        }
        res = self.client.post(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(res.data.get('kyc_required'))
        self.assertIn('NID verification (KYC) is required', res.data.get('detail', ''))

    def test_property_vault_toggle(self):
        self.client.force_authenticate(user=self.landlord)
        url = reverse('property-toggle-vault', kwargs={'pk': self.prop1.id})

        # Mark as Rented (stored in Vault)
        res = self.client.post(url, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertFalse(res.data['is_available'])

        # 1-Tap Re-publish
        res2 = self.client.post(url, format='json')
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        self.assertTrue(res2.data['is_available'])

    def test_property_vault_toggle_unverified_landlord_rejected(self):
        unverified_landlord = User.objects.create_user(
            phone_number='+8801700000088',
            full_name='Unverified Landlord 2',
            role=User.Role.LANDLORD,
        )
        unverified_landlord.landlord_profile.is_nid_verified = False
        unverified_landlord.landlord_profile.save(update_fields=['is_nid_verified'])

        prop = Property.objects.create(
            landlord=unverified_landlord,
            title='Vaulted Flat',
            tenant_category=Property.TenantCategory.FAMILY,
            rent_amount=Decimal('20000.00'),
            security_deposit=Decimal('40000.00'),
            area_neighborhood='Dhanmondi',
            full_address='Road 27, Dhanmondi, Dhaka',
            is_available=False,
        )

        self.client.force_authenticate(user=unverified_landlord)
        url = reverse('property-toggle-vault', kwargs={'pk': prop.id})
        res = self.client.post(url, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(res.data.get('kyc_required'))

    def test_move_in_cost_calculation(self):
        url = reverse('property-detail', kwargs={'pk': self.prop1.id})
        res = self.client.get(url, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # 15000 + 30000 + 2000 + 1500 = 48500
        self.assertEqual(res.data['total_move_in_cost'], 48500.0)

    def test_ai_listing_writer(self):
        url = reverse('property-ai-desc')
        payload = {
            'bedrooms': 3,
            'bathrooms': 3,
            'area': 'Gulshan 2',
            'tenant_category': 'FAMILY',
        }
        res = self.client.post(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('3-Bed Family-Friendly Modern Flat in Gulshan 2', res.data['title'])

    def test_compare_properties(self):
        url = reverse('property-compare')
        res = self.client.post(url, {'property_ids': [str(self.prop1.id), str(self.prop2.id)]}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['count'], 2)
        self.assertIn('comparison', res.data)
        self.assertIn('rent_amount', res.data['comparison'])

    def test_move_in_calculator_endpoint(self):
        url = reverse('calculate-move-in')
        payload = {
            'property_id': str(self.prop1.id),
            'moving_distance_km': 10.0,
            'truck_type': 'PICKUP_SMALL',
            'needs_labour': True,
        }
        res = self.client.post(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('total_upfront_cash_required', res.data)
        self.assertGreater(res.data['total_upfront_cash_required'], 40000.0)

    def test_fair_rent_meter(self):
        url = reverse('property-fair-rent-meter', kwargs={'pk': self.prop1.id})
        res = self.client.get(url, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('fair_price_status', res.data)
        self.assertIn('ai_verdict', res.data)

    def test_ai_photo_classifier(self):
        url = reverse('ai-classify-photo')
        res = self.client.post(url, {'image_url': 'https://example.com/bedroom.jpg'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data['success'])
        self.assertIn('detected_room_type', res.data)

    def test_ai_rent_agreement(self):
        self.client.force_authenticate(user=self.tenant)
        url = reverse('ai-generate-agreement')
        payload = {
            'property_id': str(self.prop1.id),
            'tenant_name': 'Tanvir Ahmed',
            'tenant_phone': '+8801912345678',
            'tenant_nid': '19922692018899',
            'agreed_rent': 16000.0,
            'security_deposit': 32000.0,
            'start_date': '2026-11-01',
            'duration_months': 12,
        }
        res = self.client.post(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data['ready_for_pdf_print'])
        self.assertIn('HOUSE RENTAL AGREEMENT', res.data['contract_markdown'])

    def test_draw_on_map_search(self):
        url = reverse('property-draw-search')
        # Polygon surrounding Mirpur 10 (approx lat: 23.80 - 23.82, lng: 90.35 - 90.38)
        polygon = [
            [23.8000, 90.3500],
            [23.8200, 90.3500],
            [23.8200, 90.3800],
            [23.8000, 90.3800],
        ]
        res = self.client.post(url, {'polygon': polygon}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Should return Mirpur property (lat 23.8103, lng 90.4125 is prop1 lat 23.8069, lng 90.3686)

    def test_commute_calculator(self):
        url = reverse('property-commute')
        payload = {
            'property_id': str(self.prop1.id),
            'destination_lat': 23.7937,
            'destination_lng': 90.4066,
            'destination_name': 'Banani Office',
            'travel_mode': 'METRO_TRANSIT',
        }
        res = self.client.post(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('estimated_time_minutes', res.data)
        self.assertIn('modes_breakdown', res.data)

    def test_nearby_essentials(self):
        url = reverse('property-nearby-essentials', kwargs={'pk': self.prop1.id})
        res = self.client.get(url, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('essentials', res.data)
        self.assertGreater(len(res.data['essentials']), 0)

    def test_street_view_preview(self):
        url = reverse('property-street-view', kwargs={'pk': self.prop1.id})
        res = self.client.get(url, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('alley_width_feet', res.data)
        self.assertIn('vehicle_accessibility', res.data)

    def test_saved_searches(self):
        self.client.force_authenticate(user=self.tenant)
        url = reverse('saved-searches')
        # Create saved search
        payload = {
            'name': 'Uttara Budget Flats',
            'area': 'Uttara',
            'min_rent': 10000.0,
            'max_rent': 20000.0,
            'push_alerts_enabled': True,
        }
        create_res = self.client.post(url, payload, format='json')
        self.assertEqual(create_res.status_code, status.HTTP_201_CREATED)

        # List saved searches
        list_res = self.client.get(url, format='json')
        self.assertEqual(list_res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_res.data), 1)

    def test_confirm_availability(self):
        self.client.force_authenticate(user=self.landlord)
        url = reverse('property-confirm-availability', kwargs={'pk': self.prop1.id})
        res = self.client.post(url, {'is_available': True}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data['is_available'])

    def test_monetization_boost(self):
        self.client.force_authenticate(user=self.landlord)
        url = reverse('property-boost', kwargs={'pk': self.prop1.id})
        res = self.client.post(url, {'duration_days': 7, 'payment_method': 'BKASH'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data['is_featured'])

    def test_affiliate_partners(self):
        url = reverse('services-partners')
        res = self.client.get(url, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('partners', res.data)

    def test_admin_spam_detector(self):
        url = reverse('admin-detect-spam')
        payload = {
            'rent_amount': 1500.0,
            'title': 'Full Luxury 3-Bed Flat',
            'description': 'Call now with 50% commission broker fee',
        }
        res = self.client.post(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data['is_flagged_as_spam'])

    def test_demand_supply_heatmap(self):
        url = reverse('analytics-heatmap')
        res = self.client.get(url, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('heatmap', res.data)

    def test_dedicated_sublet_switch_filter(self):
        # Create a sublet listing
        Property.objects.create(
            landlord=self.landlord,
            title='Single Room Sublet in Dhanmondi',
            property_type=Property.PropertyType.SUBLET,
            rent_amount=Decimal('8000.00'),
            security_deposit=Decimal('8000.00'),
            area_neighborhood='Dhanmondi',
            full_address='Road 27, Dhanmondi',
            is_available=True,
        )
        url = reverse('property-list-create')
        res = self.client.get(url, {'tenant_category': 'sublet'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        titles = [p['title'] for p in res.data]
        self.assertIn('Single Room Sublet in Dhanmondi', titles)
        self.assertNotIn('2-Bed Bachelor Mirpur', titles)

    def test_compare_with_commute_destination(self):
        url = reverse('property-compare')
        payload = {
            'property_ids': [str(self.prop1.id), str(self.prop2.id)],
            'destination_lat': 23.7937,
            'destination_lng': 90.4066,
            'destination_name': 'Banani Headquarters',
        }
        res = self.client.post(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('commute_distance', res.data['comparison'])
        self.assertIn('estimated_commute_time', res.data['comparison'])
        self.assertEqual(res.data['destination'], 'Banani Headquarters')

    def test_saved_search_instant_alert_trigger(self):
        # 1. Tenant saves a search for Banani under 25,000 BDT
        self.client.force_authenticate(user=self.tenant)
        create_search_url = reverse('saved-searches')
        search_res = self.client.post(create_search_url, {
            'name': 'Banani Alert',
            'area': 'Banani',
            'max_rent': 25000.0,
            'push_alerts_enabled': True,
        }, format='json')
        self.assertEqual(search_res.status_code, status.HTTP_201_CREATED)

        # 2. Landlord posts a matching flat in Banani for 22,000 BDT
        self.client.force_authenticate(user=self.landlord)
        post_url = reverse('property-list-create')
        post_res = self.client.post(post_url, {
            'title': 'New 2-Bed in Banani',
            'rent_amount': 22000.0,
            'security_deposit': 44000.0,
            'area_neighborhood': 'Banani Road 11',
            'full_address': 'Road 11, Banani, Dhaka',
            'bedrooms': 2,
        }, format='json')
        self.assertEqual(post_res.status_code, status.HTTP_201_CREATED)

        # 3. Tenant checks instant alerts endpoint
        self.client.force_authenticate(user=self.tenant)
        alerts_url = reverse('saved-search-alerts')
        alerts_res = self.client.get(alerts_url, format='json')
        self.assertEqual(alerts_res.status_code, status.HTTP_200_OK)
        self.assertGreater(len(alerts_res.data), 0)
        self.assertIn('Banani', alerts_res.data[0]['title'])

    def test_multilingual_natural_language_search(self):
        url = reverse('property-ai-search')
        # Bengali voice search query
        res = self.client.get(url, {'q': 'মিরপুর ১০ এ ২ রুমের বাসা ১৬০০০ টাকার মধ্যে'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        titles = [p['title'] for p in res.data]
        self.assertIn('2-Bed Bachelor Mirpur', titles)


