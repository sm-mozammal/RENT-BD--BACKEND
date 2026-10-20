from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Inquiry, VisitBooking
from .serializers import (
    InquirySerializer,
    InquiryCreateSerializer,
    InquiryStatusUpdateSerializer,
    VisitBookingSerializer,
    VisitBookingCreateSerializer,
    VisitBookingStatusUpdateSerializer,
)


class InquiryCreateView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = InquiryCreateSerializer

    @extend_schema(
        summary="Submit Tenant Inquiry for Property",
        description="Tenant submits an inquiry with automatic snapshot of their verified profile credentials.",
        request=InquiryCreateSerializer,
        responses={201: InquirySerializer},
    )
    def post(self, request):
        serializer = InquiryCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        inquiry = serializer.save()
        response_serializer = InquirySerializer(inquiry, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class LandlordScreeningInboxView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = InquirySerializer

    @extend_schema(
        summary="Tenant Screening Inbox (Landlord)",
        description="Returns all tenant inquiries submitted for properties owned by the current landlord.",
        responses={200: InquirySerializer(many=True)},
    )
    def get(self, request):
        inquiries = Inquiry.objects.filter(
            property__landlord=request.user
        ).select_related('property', 'tenant', 'tenant__tenant_profile')
        serializer = InquirySerializer(inquiries, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class InquiryStatusUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = InquiryStatusUpdateSerializer

    @extend_schema(
        summary="Accept or Decline Tenant Inquiry",
        description="Landlord accepts or declines tenant inquiry. Accepting unlocks chat and masked calling.",
        request=InquiryStatusUpdateSerializer,
        responses={200: InquirySerializer},
    )
    def patch(self, request, pk):
        inquiry = get_object_or_404(Inquiry, pk=pk, property__landlord=request.user)
        serializer = InquiryStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        inquiry.status = serializer.validated_data['status']
        inquiry.save(update_fields=['status'])

        return Response(InquirySerializer(inquiry, context={'request': request}).data, status=status.HTTP_200_OK)


class VisitBookingListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = VisitBookingSerializer

    @extend_schema(
        summary="List Scheduled Visits (In-person & Video Tour)",
        description="Returns scheduled visits for tenant or landlord.",
        responses={200: VisitBookingSerializer(many=True)},
    )
    def get(self, request):
        visits = VisitBooking.objects.filter(
            property__landlord=request.user
        ) | VisitBooking.objects.filter(
            tenant=request.user
        )
        visits = visits.distinct().select_related('property', 'tenant')
        serializer = VisitBookingSerializer(visits, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Schedule In-Person Visit or Live Video Tour",
        request=VisitBookingCreateSerializer,
        responses={201: VisitBookingSerializer},
    )
    def post(self, request):
        serializer = VisitBookingCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        booking = serializer.save()
        return Response(VisitBookingSerializer(booking, context={'request': request}).data, status=status.HTTP_201_CREATED)


class VisitBookingStatusUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = VisitBookingStatusUpdateSerializer

    @extend_schema(
        summary="Update Visit Booking Status (Confirm / Cancel)",
        request=VisitBookingStatusUpdateSerializer,
        responses={200: VisitBookingSerializer},
    )
    def patch(self, request, pk):
        booking = get_object_or_404(VisitBooking, pk=pk)
        if booking.property.landlord != request.user and booking.tenant != request.user:
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = VisitBookingStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if 'status' in serializer.validated_data:
            booking.status = serializer.validated_data['status']
        if 'video_call_link' in serializer.validated_data:
            booking.video_call_link = serializer.validated_data['video_call_link']

        booking.save()
        return Response(VisitBookingSerializer(booking, context={'request': request}).data, status=status.HTTP_200_OK)
