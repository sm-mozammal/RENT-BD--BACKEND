from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from apps.accounts.models import User, OTPVerification


class AccountsAuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.valid_phone = '01712345678'
        self.normalized_phone = '+8801712345678'

    def test_otp_request_valid_bangladesh_phone(self):
        url = reverse('otp-request')
        response = self.client.post(url, {'phone_number': self.valid_phone}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertTrue(OTPVerification.objects.filter(phone_number=self.normalized_phone).exists())

    def test_otp_request_invalid_phone(self):
        url = reverse('otp-request')
        response = self.client.post(url, {'phone_number': '12345'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_otp_verify_and_login(self):
        # Request OTP
        self.client.post(reverse('otp-request'), {'phone_number': self.valid_phone}, format='json')
        otp = OTPVerification.objects.filter(phone_number=self.normalized_phone).first().otp_code

        # Verify OTP
        verify_url = reverse('otp-verify')
        verify_res = self.client.post(
            verify_url,
            {
                'phone_number': self.valid_phone,
                'otp_code': otp,
                'full_name': 'Hasan Mahmud',
                'role': 'tenant',
            },
            format='json'
        )
        self.assertEqual(verify_res.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', verify_res.data)
        self.assertIn('access', verify_res.data['tokens'])
        self.assertEqual(verify_res.data['user']['fullName'], 'Hasan Mahmud')
        self.assertEqual(verify_res.data['user']['phoneNumber'], self.normalized_phone)

    def test_profile_update(self):
        user = User.objects.create_user(
            phone_number=self.normalized_phone,
            full_name='Test User',
            role=User.Role.TENANT,
        )
        self.client.force_authenticate(user=user)

        profile_url = reverse('user-profile')
        res = self.client.patch(
            profile_url,
            {
                'occupation': 'Senior Architect',
                'workplace': 'InnoSpace Lab',
                'family_size': 4,
            },
            format='json',
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['occupation'], 'Senior Architect')
        self.assertEqual(res.data['workplace'], 'InnoSpace Lab')
        self.assertEqual(res.data['familySize'], 4)

    def test_register_tenant_and_landlord(self):
        # Register distinct Tenant
        tenant_res = self.client.post(
            reverse('register'),
            {
                'phone_number': '01811112222',
                'full_name': 'Akash Tenant',
                'password': 'SecurePassword123',
                'role': 'tenant',
            },
            format='json',
        )
        self.assertEqual(tenant_res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(tenant_res.data['user']['role'], 'tenant')
        self.assertTrue(tenant_res.data['user']['isTenant'])
        self.assertFalse(tenant_res.data['user']['isLandlord'])

        # Register distinct Landlord
        landlord_res = self.client.post(
            reverse('register'),
            {
                'phone_number': '01933334444',
                'full_name': 'Haji Landlord',
                'password': 'SecurePassword123',
                'role': 'LANDLORD',  # Case-insensitive test
            },
            format='json',
        )
        self.assertEqual(landlord_res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(landlord_res.data['user']['role'], 'landlord')
        self.assertTrue(landlord_res.data['user']['isLandlord'])

    def test_password_login_and_role_switch(self):
        user = User.objects.create_user(
            phone_number='+8801777888999',
            full_name='Dual User',
            password='MyPassword123',
            role=User.Role.TENANT,
        )

        # Login with password
        login_res = self.client.post(
            reverse('password-login'),
            {
                'phone_number': '01777888999',
                'password': 'MyPassword123',
            },
            format='json',
        )
        self.assertEqual(login_res.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', login_res.data)

        # Switch role to Landlord
        self.client.force_authenticate(user=user)
        switch_res = self.client.post(
            reverse('role-switch'),
            {'role': 'landlord'},
            format='json',
        )
        self.assertEqual(switch_res.status_code, status.HTTP_200_OK)
        self.assertEqual(switch_res.data['role'], 'landlord')
        self.assertTrue(switch_res.data['isLandlord'])

