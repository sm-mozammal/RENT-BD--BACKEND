from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.utils import timezone

from apps.accounts.models import User, LandlordProfile
from apps.properties.models import Property
from apps.ledger.models import TenancyContract, RentBill
from apps.admin_ops.models import NIDVerificationRequest, GeoPhotoVerification, SpamReport


class SuperAdminAPITests(APITestCase):
    def setUp(self):
        # 1. Super Admin User
        self.admin_user = User.objects.create_superuser(
            phone_number='+8801700000000',
            full_name='Super Admin (Nafis)',
            password='Admin@RentBD2026',
            email='admin@rentbd.com',
            role=User.Role.ADMIN,
        )

        # 2. Regular Landlord
        self.landlord = User.objects.create_user(
            phone_number='+8801811223344',
            full_name='Tariqul Alam Munna',
            password='Password123!',
            email='tariqul@rentbd.com',
            role=User.Role.LANDLORD,
        )
        self.landlord_profile = self.landlord.landlord_profile
        self.landlord_profile.nid_number = '5928174920'
        self.landlord_profile.save()

        # 3. Regular Tenant
        self.tenant = User.objects.create_user(
            phone_number='+8801911223344',
            full_name='Tanvir Hasan',
            password='Password123!',
            email='tanvir@rentbd.com',
            role=User.Role.TENANT,
        )

        # 4. Property
        self.property = Property.objects.create(
            landlord=self.landlord,
            title='Modern 3-Bed Apartment near Mirpur 10 Metro Station',
            description='Prime location flat with line gas',
            property_type=Property.PropertyType.APARTMENT,
            tenant_category=Property.TenantCategory.FAMILY,
            rent_amount=Decimal('24000.00'),
            security_deposit=Decimal('48000.00'),
            service_charge=Decimal('3500.00'),
            area_neighborhood='Mirpur 10',
            full_address='House 42, Road 7, Block C, Mirpur 10',
            latitude=23.8071,
            longitude=90.3686,
            bedrooms=3,
            bathrooms=3,
            is_available=True,
            status='active',
        )

        # 5. NID Verification Request
        self.nid_req = NIDVerificationRequest.objects.create(
            landlord=self.landlord,
            nid_number='5928174920',
            nid_type='smart_card',
            nid_front_url='https://storage.rentbd.com/nid/front/nid-501-f.jpg',
            nid_back_url='https://storage.rentbd.com/nid/back/nid-501-b.jpg',
            live_selfie_url='https://storage.rentbd.com/nid/selfie/selfie-501.jpg',
            ai_face_match_confidence=94.8,
            extracted_data={
                'name_bangla': 'তারিকুল আলম মুন্না',
                'name_english': 'TARIQUL ALAM MUNNA',
                'father_name': 'MOHAMMAD NURUL ALAM',
                'date_of_birth': '14 May 1985',
                'address': 'Holding 21, Road 4, Sector 7, Uttara, Dhaka-1230',
            },
            status='pending',
        )

        # 6. Geo-Photo Verification
        self.geo_photo = GeoPhotoVerification.objects.create(
            property=self.property,
            landlord_name=self.landlord.full_name,
            landlord_phone=self.landlord.phone_number,
            photo_url='https://storage.rentbd.com/props/prop-1001/geo-01.jpg',
            property_lat=23.8071,
            property_lng=90.3686,
            property_address=self.property.full_address,
            exif_lat=23.80712,
            exif_lng=90.36858,
            distance_difference_meters=4.0,
            accuracy_meters=5.0,
            is_camera_live=True,
            status='pending',
        )

        # 7. Spam Report
        self.spam_report = SpamReport.objects.create(
            property=self.property,
            landlord_name="Shamim 'Media' Dalal",
            landlord_phone='+8801688990011',
            rent_bdt=Decimal('12000.00'),
            average_area_rent=Decimal('68000.00'),
            flags=[
                {'type': 'suspicious_low_rent', 'description': '82% lower than Dhanmondi avg', 'severity': 'critical'},
                {'type': 'duplicate_photo', 'description': 'Perceptual hash match (distance: 2 bits)', 'severity': 'critical'},
            ],
            ai_confidence_score=98.4,
            status='pending_review',
        )

        # 8. Contract and Bill
        self.contract = TenancyContract.objects.create(
            property=self.property,
            landlord=self.landlord,
            tenant=self.tenant,
            agreed_rent=Decimal('24000.00'),
            service_charge=Decimal('3500.00'),
            start_date=timezone.now().date(),
        )
        self.bill = RentBill.objects.create(
            contract=self.contract,
            billing_month='October 2026',
            base_rent=Decimal('24000.00'),
            service_charge=Decimal('3500.00'),
            total_amount=Decimal('27500.00'),
            status=RentBill.Status.PAID,
            due_date=timezone.now().date(),
            paid_at=timezone.now(),
            payment_method='bKash',
        )

    def test_8_1_login_with_email_password_and_role(self):
        url = reverse('password-login')
        payload = {
            'email': 'admin@rentbd.com',
            'password': 'Admin@RentBD2026',
            'role': 'admin',
        }
        res = self.client.post(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data['success'])
        self.assertEqual(res.data['user']['email'], 'admin@rentbd.com')
        self.assertEqual(res.data['user']['role'], 'admin')

    def test_8_1_super_admin_login(self):
        url = reverse('password-login')
        payload = {
            'phone_number': '+8801700000000',
            'password': 'Admin@RentBD2026',
            'role': 'admin',
        }
        res = self.client.post(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data['success'])
        self.assertIn('access', res.data['tokens'])
        self.assertIn('refresh', res.data['tokens'])
        self.assertTrue(res.data['user']['is_staff'])
        self.assertTrue(res.data['user']['is_superuser'])
        self.assertEqual(res.data['user']['role'], 'admin')

    def test_8_2_dashboard_overview_stats(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('admin-overview-stats')
        res = self.client.get(url, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('total_users', res.data)
        self.assertIn('active_listings', res.data)
        self.assertIn('pending_nid_count', res.data)
        self.assertIn('pending_spam_count', res.data)
        self.assertIn('total_revenue_bdt', res.data)
        self.assertIn('fair_rent_breakdown', res.data)
        self.assertIn('category_breakdown', res.data)
        self.assertIn('monthly_revenue_history', res.data)

    def test_dashboard_analytics_api(self):
        # 1. Non-admin forbidden
        self.client.force_authenticate(user=self.tenant)
        url = reverse('admin-dashboard-analytics')
        res_forbidden = self.client.get(url, format='json')
        self.assertEqual(res_forbidden.status_code, status.HTTP_403_FORBIDDEN)

        # 2. Admin access
        self.client.force_authenticate(user=self.admin_user)
        res = self.client.get(url, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Verify Core KPIs
        self.assertIn('total_users', res.data)
        self.assertIn('active_listings', res.data)
        self.assertIn('total_revenue_bdt', res.data)
        self.assertIn('average_monthly_rent_bdt', res.data)
        self.assertIn('pending_nid_count', res.data)
        self.assertIn('pending_geo_count', res.data)
        self.assertIn('pending_spam_count', res.data)
        self.assertIn('pending_property_count', res.data)

        # Verify Detailed Modules
        self.assertIn('users_analytics', res.data)
        self.assertIn('tenants_count', res.data['users_analytics'])
        self.assertIn('landlords_count', res.data['users_analytics'])

        self.assertIn('properties_analytics', res.data)
        self.assertIn('total_properties', res.data['properties_analytics'])
        self.assertIn('active_listings', res.data['properties_analytics'])

        self.assertIn('finance_analytics', res.data)
        self.assertIn('total_revenue_bdt', res.data['finance_analytics'])
        self.assertIn('collection_rate_pct', res.data['finance_analytics'])

        self.assertIn('top_demand_supply_areas', res.data)
        self.assertGreater(len(res.data['top_demand_supply_areas']), 0)

        self.assertIn('recent_activity', res.data)
        self.assertIn('recent_pending_nids', res.data['recent_activity'])
        self.assertIn('recent_pending_properties', res.data['recent_activity'])
        self.assertIn('recent_spam_reports', res.data['recent_activity'])

    def test_8_3_nid_verification_list_and_approve(self):
        self.client.force_authenticate(user=self.admin_user)
        # List
        url = reverse('admin-nid-verifications')
        res = self.client.get(url, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['nid_number'], '5928174920')

        # Approve
        approve_url = reverse('admin-nid-approve', kwargs={'pk': str(self.nid_req.id)})
        app_res = self.client.post(approve_url, {'notes': 'Biometric matched 94.8%.'}, format='json')
        self.assertEqual(app_res.status_code, status.HTTP_200_OK)
        self.assertEqual(app_res.data['status'], 'approved')
        self.landlord_profile.refresh_from_db()
        self.assertTrue(self.landlord_profile.is_nid_verified)
        self.assertTrue(self.landlord_profile.is_owner_verified)

    def test_8_3_nid_verification_reject(self):
        self.client.force_authenticate(user=self.admin_user)
        reject_url = reverse('admin-nid-reject', kwargs={'pk': str(self.nid_req.id)})
        rej_res = self.client.post(reject_url, {'reason': 'Face mismatch.'}, format='json')
        self.assertEqual(rej_res.status_code, status.HTTP_200_OK)
        self.assertEqual(rej_res.data['status'], 'rejected')
        self.landlord_profile.refresh_from_db()
        self.assertFalse(self.landlord_profile.is_nid_verified)

    def test_8_4_geo_photo_verify(self):
        self.client.force_authenticate(user=self.admin_user)
        # List
        list_url = reverse('admin-geo-photos')
        list_res = self.client.get(list_url, format='json')
        self.assertEqual(list_res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_res.data), 1)

        # Verify
        verify_url = reverse('admin-geo-photos-verify', kwargs={'pk': str(self.geo_photo.id)})
        ver_res = self.client.post(verify_url, {'approved': True}, format='json')
        self.assertEqual(ver_res.status_code, status.HTTP_200_OK)
        self.assertEqual(ver_res.data['status'], 'approved')
        self.property.refresh_from_db()
        self.assertTrue(self.property.has_geo_tagged_photos)

    def test_8_5_property_moderation_and_status_patch(self):
        self.client.force_authenticate(user=self.admin_user)
        # List
        list_url = reverse('admin-properties')
        list_res = self.client.get(list_url, format='json')
        self.assertEqual(list_res.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(list_res.data), 1)

        # Patch Status to rented
        patch_url = reverse('admin-properties-status', kwargs={'pk': str(self.property.id)})
        patch_res = self.client.patch(patch_url, {'status': 'rented'}, format='json')
        self.assertEqual(patch_res.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_res.data['status'], 'rented')
        self.property.refresh_from_db()
        self.assertFalse(self.property.is_available)

    def test_8_6_ai_spam_queue_and_resolve(self):
        self.client.force_authenticate(user=self.admin_user)
        # List
        list_url = reverse('admin-ai-spam-queue')
        list_res = self.client.get(list_url, format='json')
        self.assertEqual(list_res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_res.data), 1)

        # Resolve - landlord_blocked
        resolve_url = reverse('admin-ai-spam-resolve', kwargs={'pk': str(self.spam_report.id)})
        res_res = self.client.post(resolve_url, {'action': 'landlord_blocked'}, format='json')
        self.assertEqual(res_res.status_code, status.HTTP_200_OK)
        self.assertEqual(res_res.data['status'], 'landlord_blocked')
        self.property.refresh_from_db()
        self.assertEqual(self.property.status, 'rejected')
        self.landlord.refresh_from_db()
        self.assertTrue(self.landlord.is_flagged_broker)

    def test_8_7_demand_supply_heatmap(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('admin-analytics-heatmap')
        res = self.client.get(url, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(res.data), 5)
        self.assertEqual(res.data[0]['area_id'], 'dhaka-mirpur10')

    def test_8_8_users_list_and_ban_toggle(self):
        self.client.force_authenticate(user=self.admin_user)
        # List
        list_url = reverse('admin-users')
        list_res = self.client.get(list_url, format='json')
        self.assertEqual(list_res.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(list_res.data), 3)

        # Toggle Ban / Broker
        ban_url = reverse('admin-users-ban', kwargs={'pk': str(self.landlord.id)})
        ban_res = self.client.post(ban_url, format='json')
        self.assertEqual(ban_res.status_code, status.HTTP_200_OK)
        self.assertTrue(ban_res.data['is_flagged_broker'])
        self.landlord.refresh_from_db()
        self.assertTrue(self.landlord.is_flagged_broker)

    def test_8_9_finance_ledger(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('admin-finance-ledger')
        res = self.client.get(url, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['payment_method'], 'bKash')

    def test_unauthenticated_and_non_staff_forbidden(self):
        url = reverse('admin-overview-stats')
        # 1. Unauthenticated -> 401
        res = self.client.get(url, format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

        # 2. Regular Tenant -> 403
        self.client.force_authenticate(user=self.tenant)
        res_tenant = self.client.get(url, format='json')
        self.assertEqual(res_tenant.status_code, status.HTTP_403_FORBIDDEN)
