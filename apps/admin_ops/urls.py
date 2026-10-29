from django.urls import path
from .views import (
    AdminOverviewStatsView,
    AdminDashboardAnalyticsView,
    AdminNIDVerificationListView,
    AdminNIDApproveView,
    AdminNIDRejectView,
    AdminGeoPhotosListView,
    AdminGeoPhotoVerifyView,
    AdminPropertyListView,
    AdminPropertyStatusUpdateView,
    AdminSpamQueueListView,
    AdminSpamQueueResolveView,
    AdminDemandSupplyHeatmapView,
    AdminUserListView,
    AdminUserBanToggleView,
    AdminFinanceLedgerView,
)

urlpatterns = [
    # 8.2 Dashboard Overview & Analytics
    path('overview-stats/', AdminOverviewStatsView.as_view(), name='admin-overview-stats'),
    path('analytics/dashboard/', AdminDashboardAnalyticsView.as_view(), name='admin-dashboard-analytics'),
    path('dashboard/analytics/', AdminDashboardAnalyticsView.as_view(), name='admin-dashboard-analytics-alt'),

    # 8.3 Landlord NID Verification Queue
    path('nid-verifications/', AdminNIDVerificationListView.as_view(), name='admin-nid-verifications'),
    path('nid-verifications/<str:pk>/approve/', AdminNIDApproveView.as_view(), name='admin-nid-approve'),
    path('nid-verifications/<str:pk>/reject/', AdminNIDRejectView.as_view(), name='admin-nid-reject'),

    # 8.4 Geo-Photo Validation Queue
    path('geo-photos/', AdminGeoPhotosListView.as_view(), name='admin-geo-photos'),
    path('geo-photos/<str:pk>/verify/', AdminGeoPhotoVerifyView.as_view(), name='admin-geo-photos-verify'),

    # 8.5 Property Moderation & Status Control
    path('properties/', AdminPropertyListView.as_view(), name='admin-properties'),
    path('properties/<str:pk>/status/', AdminPropertyStatusUpdateView.as_view(), name='admin-properties-status'),

    # 8.6 AI Spam & Duplicate Detector Queue
    path('ai-spam-queue/', AdminSpamQueueListView.as_view(), name='admin-ai-spam-queue'),
    path('ai-spam-queue/<str:pk>/resolve/', AdminSpamQueueResolveView.as_view(), name='admin-ai-spam-resolve'),

    # 8.7 Demand vs. Supply Heatmap Analytics
    path('analytics/demand-supply-heatmap/', AdminDemandSupplyHeatmapView.as_view(), name='admin-analytics-heatmap'),

    # 8.8 User Directory & Anti-Broker Registry
    path('users/', AdminUserListView.as_view(), name='admin-users'),
    path('users/<str:pk>/ban/', AdminUserBanToggleView.as_view(), name='admin-users-ban'),

    # 8.9 Digital Rent & Monetization Revenue Ledger
    path('finance/ledger/', AdminFinanceLedgerView.as_view(), name='admin-finance-ledger'),
]
