from django.urls import path
from .views import AreaInsightsView, AreaInsightSubmitView

urlpatterns = [
    path('area/', AreaInsightsView.as_view(), name='area-insights'),
    path('submit/', AreaInsightSubmitView.as_view(), name='area-insight-submit'),
]
