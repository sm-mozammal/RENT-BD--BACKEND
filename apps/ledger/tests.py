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

from .models import TenancyContract, RentBill


class LedgerApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.landlord = User.objects.create_user(phone_number='+8801700991122', full_name='Landlord Karim')
        self.tenant = User.objects.create_user(phone_number='+8801800991122', full_name='Tenant Monir')
        self.prop = Property.objects.create(
            landlord=self.landlord,
            title='2-Bed Dhanmondi Flat',
            rent_amount=Decimal('25000.00'),
            security_deposit=Decimal('50000.00'),
            area_neighborhood='Dhanmondi',
            full_address='Road 4, Dhanmondi',
        )

        self.contract = TenancyContract.objects.create(
            property=self.prop,
            landlord=self.landlord,
            tenant=self.tenant,
            agreed_rent=Decimal('25000.00'),
            service_charge=Decimal('3500.00'),
        )

    def test_list_tenancies(self):
        self.client.force_authenticate(user=self.tenant)
        url = reverse('ledger-tenancies')
        res = self.client.get(url, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['property_title'], '2-Bed Dhanmondi Flat')

    def test_create_and_settle_rent_bill(self):
        self.client.force_authenticate(user=self.landlord)
        # 1. Issue bill
        create_url = reverse('ledger-bills')
        payload = {
            'contract': str(self.contract.id),
            'billing_month': 'November 2026',
            'base_rent': 25000.0,
            'electricity_bill': 1500.0,
            'gas_bill': 1080.0,
            'water_bill': 600.0,
            'service_charge': 3500.0,
            'due_date': '2026-11-10',
        }
        create_res = self.client.post(create_url, payload, format='json')
        self.assertEqual(create_res.status_code, status.HTTP_201_CREATED)
        bill_id = create_res.data['id']
        self.assertEqual(create_res.data['total_amount'], '31680.00')

        # 2. Mark Paid
        self.client.force_authenticate(user=self.tenant)
        pay_url = reverse('ledger-mark-paid', kwargs={'pk': bill_id})
        pay_res = self.client.post(pay_url, {'payment_method': 'BKASH'}, format='json')
        self.assertEqual(pay_res.status_code, status.HTTP_200_OK)
        self.assertTrue(pay_res.data['success'])
        self.assertIn('receipt_number', pay_res.data)

        # 3. View Receipt
        receipt_url = reverse('ledger-receipt', kwargs={'pk': bill_id})
        receipt_res = self.client.get(receipt_url, format='json')
        self.assertEqual(receipt_res.status_code, status.HTTP_200_OK)
        self.assertEqual(receipt_res.data['status'], 'VERIFIED_PAID')
        self.assertEqual(receipt_res.data['breakdown']['total_paid_bdt'], 31680.0)

    def test_send_payment_reminder(self):
        bill = RentBill.objects.create(
            contract=self.contract,
            billing_month='December 2026',
            base_rent=Decimal('25000.00'),
            service_charge=Decimal('3500.00'),
            total_amount=Decimal('28500.00'),
            status=RentBill.Status.DUE,
            due_date='2026-12-10',
        )

        self.client.force_authenticate(user=self.landlord)
        url = reverse('ledger-send-reminder', kwargs={'pk': bill.id})
        res = self.client.post(url, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data['success'])
        self.assertIn('reminder_message', res.data)
        self.assertIn('SMS_GATEWAY', res.data['delivery_channels'])

