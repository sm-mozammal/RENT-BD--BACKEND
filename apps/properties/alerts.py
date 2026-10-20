from django.utils import timezone
from .models import SavedSearch, SavedSearchAlert


def trigger_saved_search_alerts(property_obj):
    """
    Evaluates newly listed or re-listed properties against all active SavedSearches.
    Creates in-app alerts and updates the search's last_alert_sent_at timestamp.
    """
    if not property_obj.is_available:
        return []

    active_searches = SavedSearch.objects.filter(
        push_alerts_enabled=True,
    ).exclude(user=property_obj.landlord)

    generated_alerts = []
    prop_area = property_obj.area_neighborhood.lower()
    prop_addr = property_obj.full_address.lower()
    prop_title = property_obj.title.lower()

    for search in active_searches:
        # 1. Area check
        if search.area:
            s_area = search.area.strip().lower()
            if s_area not in prop_area and s_area not in prop_addr and s_area not in prop_title:
                continue

        # 2. Tenant Category check
        if search.tenant_category and search.tenant_category.upper() not in ['ANY', '']:
            if property_obj.tenant_category != 'ANY' and property_obj.tenant_category != search.tenant_category.upper():
                continue

        # 3. Rent range check
        if search.min_rent is not None and property_obj.rent_amount < search.min_rent:
            continue
        if search.max_rent is not None and property_obj.rent_amount > search.max_rent:
            continue

        # 4. Bedroom check
        if search.bedrooms is not None and property_obj.bedrooms != search.bedrooms:
            continue

        # Create alert if not already notified
        alert, created = SavedSearchAlert.objects.get_or_create(
            saved_search=search,
            property=property_obj,
            defaults={
                'user': search.user,
                'title': f"Instant Match in {property_obj.area_neighborhood}: ৳{int(property_obj.rent_amount):,}",
                'message': (
                    f"A new {property_obj.bedrooms}-bed flat matching your alert '{search.name}' "
                    f"was just listed at ৳{int(property_obj.rent_amount):,}/mo in {property_obj.area_neighborhood}."
                ),
            }
        )

        if created:
            search.last_alert_sent_at = timezone.now()
            search.save(update_fields=['last_alert_sent_at'])
            generated_alerts.append(alert)

    return generated_alerts
