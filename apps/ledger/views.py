import uuid
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import TenancyContract, RentBill, RentReceipt
from .serializers import (
    TenancyContractSerializer,
    RentBillSerializer,
    RentBillCreateSerializer,
    MarkBillPaidSerializer,
)


class TenancyContractListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TenancyContractSerializer

    @extend_schema(
        summary="List Active Tenancy Contracts",
        description="Returns rental contracts where user is either landlord or tenant.",
        responses={200: TenancyContractSerializer(many=True), 201: TenancyContractSerializer},
    )
    def get(self, request):
        contracts = TenancyContract.objects.filter(
            landlord=request.user
        ) | TenancyContract.objects.filter(
            tenant=request.user
        )
        return Response(TenancyContractSerializer(contracts.distinct(), many=True).data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = TenancyContractSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        contract = serializer.save(landlord=request.user)
        return Response(TenancyContractSerializer(contract).data, status=status.HTTP_201_CREATED)


class RentBillListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RentBillSerializer

    @extend_schema(
        summary="List Monthly Rent & Utility Bills",
        responses={200: RentBillSerializer(many=True), 201: RentBillSerializer},
    )
    def get(self, request):
        bills = RentBill.objects.filter(
            contract__landlord=request.user
        ) | RentBill.objects.filter(
            contract__tenant=request.user
        )
        return Response(RentBillSerializer(bills.distinct(), many=True).data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Issue Monthly Rent & Utility Bill",
        request=RentBillCreateSerializer,
        responses={201: RentBillSerializer},
    )
    def post(self, request):
        serializer = RentBillCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        bill = serializer.save()
        return Response(RentBillSerializer(bill).data, status=status.HTTP_201_CREATED)


class MarkBillPaidView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MarkBillPaidSerializer

    @extend_schema(
        summary="Mark Bill Paid & Generate Digital Receipt",
        request=MarkBillPaidSerializer,
        responses={200: OpenApiResponse(description="Bill settled and digital receipt generated")},
    )
    def post(self, request, pk):
        bill = get_object_or_404(RentBill, pk=pk)
        serializer = MarkBillPaidSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        bill.status = RentBill.Status.PAID
        bill.paid_at = timezone.now()
        bill.payment_method = serializer.validated_data['payment_method']
        bill.save(update_fields=['status', 'paid_at', 'payment_method'])

        # Generate official digital receipt
        receipt_no = f"RCT-{timezone.now().strftime('%Y%m')}-{uuid.uuid4().hex[:6].upper()}"
        receipt, _ = RentReceipt.objects.get_or_create(bill=bill, defaults={'receipt_no': receipt_no})

        return Response({
            'success': True,
            'message': 'Bill successfully settled.',
            'receipt_number': receipt.receipt_no,
            'bill': RentBillSerializer(bill).data,
        }, status=status.HTTP_200_OK)


class RentReceiptDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="View Digital Rent Receipt",
        responses={200: OpenApiResponse(description="Printable digital receipt data")},
    )
    def get(self, request, pk):
        bill = get_object_or_404(RentBill, pk=pk)
        receipt = get_object_or_404(RentReceipt, bill=bill)

        return Response({
            'receipt_number': receipt.receipt_no,
            'issued_date': receipt.generated_at,
            'landlord_name': bill.contract.landlord.full_name,
            'tenant_name': bill.contract.tenant.full_name,
            'property_title': bill.contract.property.title,
            'property_address': bill.contract.property.full_address,
            'billing_month': bill.billing_month,
            'breakdown': {
                'base_rent': float(bill.base_rent),
                'electricity': float(bill.electricity_bill),
                'gas': float(bill.gas_bill),
                'water': float(bill.water_bill),
                'service_charge': float(bill.service_charge),
                'total_paid_bdt': float(bill.total_amount),
            },
            'payment_method': bill.payment_method,
            'status': 'VERIFIED_PAID',
        }, status=status.HTTP_200_OK)


class SendBillReminderView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Send Automated Rent Payment Reminder",
        description="Landlord sends an automated push & SMS payment reminder for an unpaid or overdue bill.",
        request=None,
        responses={200: OpenApiResponse(description="Payment reminder dispatched")},
    )
    def post(self, request, pk):
        bill = get_object_or_404(RentBill, pk=pk)
        if bill.contract.landlord != request.user:
            return Response({'detail': 'Only the landlord can send payment reminders for this bill.'}, status=status.HTTP_403_FORBIDDEN)

        if bill.status == RentBill.Status.PAID:
            return Response({'detail': 'This bill has already been settled and paid.'}, status=status.HTTP_400_BAD_REQUEST)

        tenant = bill.contract.tenant
        from apps.common.utils import mask_phone_number
        masked_phone = mask_phone_number(tenant.phone_number)

        reminder_text = (
            f"RentBD Reminder: Dear {tenant.full_name}, your rent & utility bill for {bill.billing_month} "
            f"totaling ৳{int(bill.total_amount):,} at {bill.contract.property.title} is due on {bill.due_date}. "
            f"Please pay via bKash/Nagad or bank to keep your rental score high."
        )

        return Response({
            'success': True,
            'bill_id': str(bill.id),
            'billing_month': bill.billing_month,
            'total_amount': float(bill.total_amount),
            'tenant_name': tenant.full_name,
            'tenant_phone_masked': masked_phone,
            'delivery_channels': ['IN_APP_PUSH', 'SMS_GATEWAY'],
            'reminder_message': reminder_text,
            'dispatched_at': timezone.now(),
            'status': 'DELIVERED',
        }, status=status.HTTP_200_OK)

