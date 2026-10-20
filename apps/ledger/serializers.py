from decimal import Decimal
from rest_framework import serializers
from .models import TenancyContract, RentBill, RentReceipt
try:
    from apps.properties.models import Property
except (ImportError, ModuleNotFoundError):
    from ..properties.models import Property

try:
    from apps.accounts.models import User
except (ImportError, ModuleNotFoundError):
    from ..accounts.models import User


class TenancyContractSerializer(serializers.ModelSerializer):
    property_title = serializers.CharField(source='property.title', read_only=True)
    landlord_name = serializers.CharField(source='landlord.full_name', read_only=True)
    tenant_name = serializers.CharField(source='tenant.full_name', read_only=True)

    class Meta:
        model = TenancyContract
        fields = [
            'id',
            'property',
            'property_title',
            'landlord_name',
            'tenant_name',
            'agreed_rent',
            'service_charge',
            'start_date',
            'end_date',
            'is_active',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class RentBillSerializer(serializers.ModelSerializer):
    property_title = serializers.CharField(source='contract.property.title', read_only=True)
    tenant_name = serializers.CharField(source='contract.tenant.full_name', read_only=True)
    receipt_no = serializers.CharField(source='receipt.receipt_no', read_only=True, default='')

    class Meta:
        model = RentBill
        fields = [
            'id',
            'contract',
            'property_title',
            'tenant_name',
            'billing_month',
            'base_rent',
            'electricity_bill',
            'gas_bill',
            'water_bill',
            'service_charge',
            'total_amount',
            'status',
            'due_date',
            'paid_at',
            'payment_method',
            'receipt_no',
            'created_at',
        ]
        read_only_fields = ['id', 'total_amount', 'paid_at', 'receipt_no', 'created_at']


class RentBillCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RentBill
        fields = [
            'contract',
            'billing_month',
            'base_rent',
            'electricity_bill',
            'gas_bill',
            'water_bill',
            'service_charge',
            'due_date',
        ]

    def create(self, validated_data):
        base = validated_data.get('base_rent', Decimal('0.00'))
        elec = validated_data.get('electricity_bill', Decimal('0.00'))
        gas = validated_data.get('gas_bill', Decimal('0.00'))
        water = validated_data.get('water_bill', Decimal('0.00'))
        service = validated_data.get('service_charge', Decimal('0.00'))
        total = base + elec + gas + water + service
        return RentBill.objects.create(total_amount=total, **validated_data)


class MarkBillPaidSerializer(serializers.Serializer):
    payment_method = serializers.ChoiceField(choices=['BKASH', 'NAGAD', 'BANK_TRANSFER', 'CASH'], default='BKASH')
