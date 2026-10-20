from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
try:
    from apps.accounts.models import User
except (ImportError, ModuleNotFoundError):
    from ..accounts.models import User
from .models import AreaInsight


class InsightsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            phone_number='+8801700112233',
            full_name='Resident Rafiq',
        )

    def test_get_area_insights(self):
        AreaInsight.objects.create(
            area_name='Mirpur 10',
            user=self.user,
            waterlogging_risk=AreaInsight.WaterloggingRisk.NONE,
            gas_supply_reliability=AreaInsight.GasSupply.EXCELLENT,
            water_quality=AreaInsight.WaterQuality.EXCELLENT,
            night_safety_rating=4.8,
            resident_review='Very peaceful neighborhood with zero waterlogging.',
        )
        url = reverse('area-insights')
        res = self.client.get(url, {'area': 'Mirpur 10'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['area_name'], 'Mirpur 10')
        self.assertIn('aggregate_metrics', res.data)
        self.assertEqual(len(res.data['recent_reviews']), 1)

    def test_submit_area_insight(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('area-insight-submit')
        payload = {
            'area_name': 'Uttara Sector 4',
            'waterlogging_risk': 'NONE',
            'gas_supply_reliability': 'EXCELLENT',
            'water_quality': 'EXCELLENT',
            'night_safety_rating': 4.9,
            'resident_review': 'Safe for families, active security guards at every gate.',
        }
        res = self.client.post(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['area_name'], 'Uttara Sector 4')
