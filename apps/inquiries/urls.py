from django.urls import path
from .views import (
    InquiryCreateView,
    LandlordScreeningInboxView,
    InquiryStatusUpdateView,
    VisitBookingListCreateView,
    VisitBookingStatusUpdateView,
)

urlpatterns = [
    path('', InquiryCreateView.as_view(), name='inquiry-create'),
    path('landlord-inbox/', LandlordScreeningInboxView.as_view(), name='landlord-inbox'),
    path('<uuid:pk>/status/', InquiryStatusUpdateView.as_view(), name='inquiry-status-update'),
    path('visits/', VisitBookingListCreateView.as_view(), name='visit-bookings'),
    path('visits/<uuid:pk>/status/', VisitBookingStatusUpdateView.as_view(), name='visit-booking-status'),
]
