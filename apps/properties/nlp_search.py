import re
from decimal import Decimal
from django.db.models import Q
from .models import Property

BENGLI_DIGIT_MAP = {
    '০': '0', '১': '1', '২': '2', '৩': '3', '৪': '4',
    '৫': '5', '৬': '6', '৭': '7', '৮': '8', '৯': '9',
}

KNOWN_AREAS = [
    # Area name, normalized search term
    ('mirpur 10', 'Mirpur 10'), ('মিরপুর ১০', 'Mirpur 10'),
    ('mirpur 11', 'Mirpur 11'), ('মিরপুর ১১', 'Mirpur 11'),
    ('mirpur 12', 'Mirpur 12'), ('মিরপুর ১২', 'Mirpur 12'),
    ('mirpur 2', 'Mirpur 2'), ('মিরপুর ২', 'Mirpur 2'),
    ('mirpur 1', 'Mirpur 1'), ('মিরপুর ১', 'Mirpur 1'),
    ('mirpur', 'Mirpur'), ('মিরপুর', 'Mirpur'),
    ('uttara sector 4', 'Uttara Sector 4'), ('উত্তরা সেক্টর ৪', 'Uttara Sector 4'),
    ('uttara sector 3', 'Uttara Sector 3'), ('উত্তরা সেক্টর ৩', 'Uttara Sector 3'),
    ('uttara sector 7', 'Uttara Sector 7'), ('উত্তরা সেক্টর ৭', 'Uttara Sector 7'),
    ('uttara', 'Uttara'), ('উত্তরা', 'Uttara'),
    ('dhanmondi', 'Dhanmondi'), ('ধানমন্ডি', 'Dhanmondi'),
    ('gulshan 1', 'Gulshan 1'), ('গুলশান ১', 'Gulshan 1'),
    ('gulshan 2', 'Gulshan 2'), ('গুলশান ২', 'Gulshan 2'),
    ('gulshan', 'Gulshan'), ('গুলশান', 'Gulshan'),
    ('banani', 'Banani'), ('বনানী', 'Banani'),
    ('bashundhara r/a', 'Bashundhara R/A'), ('bashundhara', 'Bashundhara'), ('বসুন্ধরা', 'Bashundhara'),
    ('mohammadpur', 'Mohammadpur'), ('মোহাম্মদপুর', 'Mohammadpur'),
    ('badda', 'Badda'), ('বাড্ডা', 'Badda'),
    ('khilgaon', 'Khilgaon'), ('খিলগাঁও', 'Khilgaon'),
    ('malibagh', 'Malibagh'), ('মালিবাগ', 'Malibagh'),
    ('rampura', 'Rampura'), ('রামপুরা', 'Rampura'),
    ('shantinagar', 'Shantinagar'), ('শান্তিনগর', 'Shantinagar'),
    ('lalmatia', 'Lalmatia'), ('লালমাটিয়া', 'Lalmatia'),
    ('agrabad', 'Agrabad'), ('আগ্রাবাদ', 'Agrabad'),
    ('nasirabad', 'Nasirabad'), ('নাসিরাবাদ', 'Nasirabad'),
    ('zindabazar', 'Zindabazar'), ('জিন্দাবাজার', 'Zindabazar'),
]


def convert_bengali_digits(text: str) -> str:
    """Replaces Bengali numeral characters with standard ASCII digits."""
    for b_digit, a_digit in BENGLI_DIGIT_MAP.items():
        text = text.replace(b_digit, a_digit)
    return text


def parse_and_filter_natural_query(raw_query: str):
    """
    Parses multilingual English, Bangla, and Banglish natural language / voice prompts
    and returns a filtered Django queryset and a structured metadata dictionary.
    """
    if not raw_query or not raw_query.strip():
        qs = Property.objects.filter(is_available=True)
        return qs, {'original_query': raw_query, 'detected': {}}

    text = convert_bengali_digits(raw_query.lower())

    extracted = {
        'original_query': raw_query,
        'detected_area': None,
        'detected_bedrooms': None,
        'detected_max_rent': None,
        'detected_tenant_category': None,
        'detected_property_type': None,
        'detected_amenities': [],
    }

    # 1. Detect Area
    for pattern, normalized in KNOWN_AREAS:
        if pattern in text:
            extracted['detected_area'] = normalized
            break

    # 2. Detect Bedrooms (e.g. 2-bed, 2 bedroom, 3 bed, ২ রুম, 2 room, 3 bhk)
    bed_match = re.search(r'(\d+)\s*(?:-?\s*bed(?:room)?|bhk|room|রুম|বেড)', text)
    if bed_match:
        extracted['detected_bedrooms'] = int(bed_match.group(1))

    # 3. Detect Tenant Category or Sublet
    if any(k in text for k in ['sublet', 'সাবলেট']):
        extracted['detected_property_type'] = Property.PropertyType.SUBLET
    elif any(k in text for k in ['bachelor', 'ব্যাচেলর', 'mess', 'mes', 'মেস']):
        if 'female' in text or 'মহিলা' in text or 'মেয়ে' in text:
            extracted['detected_tenant_category'] = Property.TenantCategory.BACHELOR_FEMALE
        else:
            extracted['detected_tenant_category'] = Property.TenantCategory.BACHELOR_MALE
    elif any(k in text for k in ['family', 'ফ্যামিলি', 'poribar', 'পরিবার']):
        extracted['detected_tenant_category'] = Property.TenantCategory.FAMILY

    # 4. Detect Maximum Budget (e.g. within 16,000, under 16k, ১৬০০০ টাকা, 18k, 20000 budget)
    # Check "16k" or "20k"
    k_match = re.search(r'(\d+)\s*k\b', text)
    if k_match:
        extracted['detected_max_rent'] = float(k_match.group(1)) * 1000.0
    else:
        # Check standard 4-6 digit budget figures
        rent_match = re.search(r'(?:within|under|below|max|upto|budget|মধ্যে|কম|পর্যন্ত|টাকা|ভাড়া|টাকার)\s*(?:of\s*)?(?:tk|bdt|৳|টাকা)?\s*(\d{4,6})', text)
        if not rent_match:
            rent_match = re.search(r'(\d{4,6})\s*(?:tk|bdt|৳|টাকা)?\s*(?:within|under|below|budget|মধ্যে|কম|পর্যন্ত)', text)
        if not rent_match:
            # Fallback bare number 8000-80000
            bare_numbers = re.findall(r'\b(\d{4,5})\b', text)
            if bare_numbers:
                extracted['detected_max_rent'] = float(bare_numbers[-1])
        else:
            extracted['detected_max_rent'] = float(rent_match.group(1))

    # 5. Detect Amenities
    if any(k in text for k in ['balcony', 'বারান্দা', 'baranda', 'veranda']):
        extracted['detected_amenities'].append('Balcony')
    if any(k in text for k in ['metro', 'মেট্রো', 'mrt']):
        extracted['detected_amenities'].append('Metro Station')
    if any(k in text for k in ['gas', 'গ্যাস', 'line gas', 'লাইন গ্যাস']):
        extracted['detected_amenities'].append('Line Gas')
    if any(k in text for k in ['lift', 'লিফট', 'elevator']):
        extracted['detected_amenities'].append('Lift')

    # Construct Queryset
    queryset = Property.objects.filter(is_available=True).select_related(
        'landlord', 'landlord__landlord_profile'
    ).prefetch_related('images')

    q_filter = Q()

    if extracted['detected_area']:
        area_term = extracted['detected_area']
        area_q = Q(area_neighborhood__icontains=area_term)
        area_q.add(Q(full_address__icontains=area_term), Q.OR)
        area_q.add(Q(title__icontains=area_term), Q.OR)
        q_filter.add(area_q, Q.AND)

    if extracted['detected_bedrooms']:
        q_filter &= Q(bedrooms=extracted['detected_bedrooms'])

    if extracted['detected_property_type']:
        q_filter &= Q(property_type=extracted['detected_property_type'])

    if extracted['detected_tenant_category']:
        q_filter &= Q(
            tenant_category__in=[extracted['detected_tenant_category'], Property.TenantCategory.ANY]
        )

    if extracted['detected_max_rent']:
        q_filter &= Q(rent_amount__lte=Decimal(str(extracted['detected_max_rent'])))

    if 'Balcony' in extracted['detected_amenities']:
        q_filter &= Q(balconies__gte=1)

    if 'Line Gas' in extracted['detected_amenities']:
        q_filter &= Q(gas_supply=Property.GasSupplyType.LINE_GAS)

    if 'Metro Station' in extracted['detected_amenities']:
        metro_q = Q(description__icontains='metro')
        metro_q.add(Q(title__icontains='metro'), Q.OR)
        metro_q.add(Q(area_neighborhood__icontains='mirpur'), Q.OR)
        metro_q.add(Q(area_neighborhood__icontains='uttara'), Q.OR)
        q_filter.add(metro_q, Q.AND)

    results = queryset.filter(q_filter)

    # Fallback keyword match if strict structured filter yielded 0 results
    if not results.exists():
        tokens = [t for t in re.split(r'[\s,.-]+', text) if len(t) > 2]
        fallback_q = Q()
        for token in tokens:
            token_q = Q(area_neighborhood__icontains=token)
            token_q.add(Q(title__icontains=token), Q.OR)
            token_q.add(Q(description__icontains=token), Q.OR)
            fallback_q.add(token_q, Q.OR)
        results = queryset.filter(fallback_q).distinct()

    return results, extracted
