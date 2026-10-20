from rest_framework import serializers
from .models import AreaInsight


class AreaInsightSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.full_name', read_only=True)

    class Meta:
        model = AreaInsight
        fields = [
            'id',
            'area_name',
            'user_name',
            'waterlogging_risk',
            'gas_supply_reliability',
            'water_quality',
            'night_safety_rating',
            'resident_review',
            'created_at',
        ]
        read_only_fields = ['id', 'user_name', 'created_at']


class AreaInsightSubmitSerializer(serializers.ModelSerializer):
    class Meta:
        model = AreaInsight
        fields = [
            'area_name',
            'waterlogging_risk',
            'gas_supply_reliability',
            'water_quality',
            'night_safety_rating',
            'resident_review',
        ]

    def create(self, validated_data):
        return AreaInsight.objects.create(
            user=self.context['request'].user,
            **validated_data,
        )
