from django.urls import path
from .views import (
    PropertyListCreateView,
    PropertyDetailView,
    PropertyVaultToggleView,
    PropertySaveToggleView,
    SavedPropertiesListView,
    AIListingWriterView,
    AISearchView,
    PropertyPhotoUploadView,
    SavedSearchListCreateView,
    SavedSearchAlertListView,
    SavedSearchAlertMarkReadView,
    PropertyCompareView,
    MoveInCostCalculatorView,
    AIFairRentMeterView,
    AIPhotoClassifierView,
    AIRentAgreementGeneratorView,
    DrawOnMapSearchView,
    CommuteCalculatorView,
    NearbyEssentialsView,
    StreetViewPreviewView,
    ListingAvailabilityConfirmView,
    MonetizationBoostView,
    AffiliatePartnersView,
    BookPartnerServiceView,
    AdminSpamDetectorView,
    DemandSupplyHeatmapView,
)

urlpatterns = [
    # Core Listings & Saved
    path('', PropertyListCreateView.as_view(), name='property-list-create'),
    path('saved/', SavedPropertiesListView.as_view(), name='property-saved-list'),
    path('saved-searches/', SavedSearchListCreateView.as_view(), name='saved-searches'),
    path('saved-searches/alerts/', SavedSearchAlertListView.as_view(), name='saved-search-alerts'),
    path('saved-searches/alerts/<uuid:pk>/read/', SavedSearchAlertMarkReadView.as_view(), name='saved-search-alert-read'),

    # Search & Comparison
    path('ai_search/', AISearchView.as_view(), name='property-ai-search'),
    path('draw-search/', DrawOnMapSearchView.as_view(), name='property-draw-search'),
    path('compare/', PropertyCompareView.as_view(), name='property-compare'),
    path('calculate-move-in/', MoveInCostCalculatorView.as_view(), name='calculate-move-in'),
    path('commute-calculator/', CommuteCalculatorView.as_view(), name='property-commute'),

    # AI Differentiators
    path('ai-generate-description/', AIListingWriterView.as_view(), name='property-ai-desc'),
    path('ai/classify-photo/', AIPhotoClassifierView.as_view(), name='ai-classify-photo'),
    path('ai/generate-agreement/', AIRentAgreementGeneratorView.as_view(), name='ai-generate-agreement'),

    # Services, Analytics & Admin
    path('services/partners/', AffiliatePartnersView.as_view(), name='services-partners'),
    path('services/book/', BookPartnerServiceView.as_view(), name='services-book'),
    path('admin/detect-spam/', AdminSpamDetectorView.as_view(), name='admin-detect-spam'),
    path('analytics/demand-supply-heatmap/', DemandSupplyHeatmapView.as_view(), name='analytics-heatmap'),

    # Specific Property Operations
    path('<uuid:pk>/', PropertyDetailView.as_view(), name='property-detail'),
    path('<uuid:pk>/toggle-vault/', PropertyVaultToggleView.as_view(), name='property-toggle-vault'),
    path('<uuid:pk>/save/', PropertySaveToggleView.as_view(), name='property-toggle-save'),
    path('<uuid:pk>/photos/', PropertyPhotoUploadView.as_view(), name='property-upload-photo'),
    path('<uuid:pk>/fair-rent-meter/', AIFairRentMeterView.as_view(), name='property-fair-rent-meter'),
    path('<uuid:pk>/move-in-cost/', MoveInCostCalculatorView.as_view(), name='property-move-in-cost'),
    path('<uuid:pk>/nearby-essentials/', NearbyEssentialsView.as_view(), name='property-nearby-essentials'),
    path('<uuid:pk>/street-view/', StreetViewPreviewView.as_view(), name='property-street-view'),
    path('<uuid:pk>/confirm-availability/', ListingAvailabilityConfirmView.as_view(), name='property-confirm-availability'),
    path('<uuid:pk>/boost/', MonetizationBoostView.as_view(), name='property-boost'),
]
