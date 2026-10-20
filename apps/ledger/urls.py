from django.urls import path
from .views import (
    TenancyContractListCreateView,
    RentBillListCreateView,
    MarkBillPaidView,
    RentReceiptDetailView,
    SendBillReminderView,
)

urlpatterns = [
    path('tenancies/', TenancyContractListCreateView.as_view(), name='ledger-tenancies'),
    path('bills/', RentBillListCreateView.as_view(), name='ledger-bills'),
    path('bills/<uuid:pk>/mark-paid/', MarkBillPaidView.as_view(), name='ledger-mark-paid'),
    path('bills/<uuid:pk>/receipt/', RentReceiptDetailView.as_view(), name='ledger-receipt'),
    path('bills/<uuid:pk>/send-reminder/', SendBillReminderView.as_view(), name='ledger-send-reminder'),
]

