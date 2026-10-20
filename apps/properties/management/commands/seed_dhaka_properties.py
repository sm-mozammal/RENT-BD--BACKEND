from decimal import Decimal
from typing import Any
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.accounts.models import User
from apps.properties.models import Property, PropertyImage


class Command(BaseCommand):
    help = 'Seeds database with realistic Dhaka property listings matching Flutter app mock data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding Dhaka rental properties...')

        # 1. Create Verified Landlord 1
        landlord1, _ = User.objects.get_or_create(
            phone_number='+8801711223344',
            defaults={
                'full_name': 'Engr. Farhan Kabir',
                'role': User.Role.LANDLORD,
                'is_phone_verified': True,
            }
        )
        if hasattr(landlord1, 'landlord_profile'):
            lp = landlord1.landlord_profile
            lp.is_nid_verified = True
            lp.is_owner_verified = True
            lp.rental_rating = 4.9
            lp.save()

        # 2. Create Verified Landlord 2
        landlord2, _ = User.objects.get_or_create(
            phone_number='+8801822334455',
            defaults={
                'full_name': 'Dr. Shahriar Rahman',
                'role': User.Role.LANDLORD,
                'is_phone_verified': True,
            }
        )
        if hasattr(landlord2, 'landlord_profile'):
            lp2 = landlord2.landlord_profile
            lp2.is_nid_verified = True
            lp2.is_owner_verified = True
            lp2.rental_rating = 4.8
            lp2.save()

        # 3. Create Demo Tenant User
        tenant1, _ = User.objects.get_or_create(
            phone_number='+8801912345678',
            defaults={
                'full_name': 'Tanvir Ahmed',
                'role': User.Role.TENANT,
                'is_phone_verified': True,
            }
        )
        if hasattr(tenant1, 'tenant_profile'):
            tp = tenant1.tenant_profile
            tp.occupation = 'Software Engineer'
            tp.workplace = 'InnoSpace Infotech, Banani'
            tp.family_size = 3
            tp.is_nid_verified = True
            tp.rental_rating = 5.0
            tp.save()

        # Properties data
        properties_data = [
            {
                'landlord': landlord1,
                'title': '2-Bed Modern Flat near Mirpur 10 Metro Station',
                'description': 'South-facing apartment with immense natural ventilation and two spacious balconies. Located just a 3-minute walk from Mirpur 10 Metro Gate 2. Bachelor-friendly with 24/7 building security and separate sub-meter electricity.',
                'property_type': Property.PropertyType.APARTMENT,
                'tenant_category': Property.TenantCategory.BACHELOR_MALE,
                'rent_amount': Decimal('16500.00'),
                'security_deposit': Decimal('33000.00'),
                'service_charge': Decimal('2500.00'),
                'estimated_utilities': Decimal('1800.00'),
                'bedrooms': 2,
                'bathrooms': 2,
                'balconies': 2,
                'square_feet': 920,
                'floor_level': 4,
                'total_floors': 7,
                'latitude': 23.8069,
                'longitude': 90.3686,
                'area_neighborhood': 'Mirpur 10',
                'full_address': 'Road 14, Block C, Mirpur 10, Dhaka',
                'has_geo_tagged_photos': True,
                'is_available': True,
                'is_owner_verified': True,
                'fair_price_status': Property.FairPriceStatus.GREAT_DEAL,
                'fair_price_percent_diff': -8.5,
                'area_average_rent': Decimal('18000.00'),
                'alleyWidthFeet': 22.0,
                'gas_supply': Property.GasSupplyType.LINE_GAS,
                'waterlogging_risk': Property.WaterloggingRisk.NONE,
                'water_quality': Property.WaterQuality.EXCELLENT,
                'night_safety_rating': 4.8,
                'photos': [
                    ('https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=800', PropertyImage.RoomType.LIVING_ROOM),
                    ('https://images.unsplash.com/photo-1598928506311-c55ded91a20c?w=800', PropertyImage.RoomType.BEDROOM),
                    ('https://images.unsplash.com/photo-1556911220-e15b29be8c8f?w=800', PropertyImage.RoomType.KITCHEN),
                    ('https://images.unsplash.com/photo-1584622650111-993a426fbf0a?w=800', PropertyImage.RoomType.WASHROOM),
                ],
            },
            {
                'landlord': landlord2,
                'title': 'Spacious 3-Bed Family Apartment overlooking Park',
                'description': 'Ideal family home in quiet residential Sector 4 Uttara. Double lift, standby full generator backup, CCTV surveillance, dedicated car parking slot on ground floor, and active Titas line gas connection.',
                'property_type': Property.PropertyType.APARTMENT,
                'tenant_category': Property.TenantCategory.FAMILY,
                'rent_amount': Decimal('28000.00'),
                'security_deposit': Decimal('56000.00'),
                'service_charge': Decimal('4000.00'),
                'estimated_utilities': Decimal('2500.00'),
                'bedrooms': 3,
                'bathrooms': 3,
                'balconies': 3,
                'square_feet': 1450,
                'floor_level': 5,
                'total_floors': 9,
                'latitude': 23.8681,
                'longitude': 90.3984,
                'area_neighborhood': 'Uttara Sector 4',
                'full_address': 'Road 7, Sector 4, Uttara, Dhaka',
                'has_geo_tagged_photos': True,
                'is_available': True,
                'is_owner_verified': True,
                'fair_price_status': Property.FairPriceStatus.FAIR_PRICE,
                'fair_price_percent_diff': 1.2,
                'area_average_rent': Decimal('27500.00'),
                'alleyWidthFeet': 30.0,
                'gas_supply': Property.GasSupplyType.LINE_GAS,
                'waterlogging_risk': Property.WaterloggingRisk.NONE,
                'water_quality': Property.WaterQuality.EXCELLENT,
                'night_safety_rating': 4.9,
                'photos': [
                    ('https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=800', PropertyImage.RoomType.LIVING_ROOM),
                    ('https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800', PropertyImage.RoomType.BEDROOM),
                    ('https://images.unsplash.com/photo-1484154218962-a197022b5858?w=800', PropertyImage.RoomType.KITCHEN),
                ],
            },
            {
                'landlord': landlord1,
                'title': 'Premium 3-Bed Lakeview Flat in Dhanmondi',
                'description': 'Prestigious lakeside address in Dhanmondi 8/A. Granite countertops, master bath tub, south-east corner unit with unhindered breeze. 2 high speed passenger elevators.',
                'property_type': Property.PropertyType.APARTMENT,
                'tenant_category': Property.TenantCategory.FAMILY,
                'rent_amount': Decimal('38000.00'),
                'security_deposit': Decimal('76000.00'),
                'service_charge': Decimal('5000.00'),
                'estimated_utilities': Decimal('3000.00'),
                'bedrooms': 3,
                'bathrooms': 3,
                'balconies': 2,
                'square_feet': 1600,
                'floor_level': 6,
                'total_floors': 12,
                'latitude': 23.7461,
                'longitude': 90.3742,
                'area_neighborhood': 'Dhanmondi',
                'full_address': 'Road 8/A, Dhanmondi, Dhaka',
                'has_geo_tagged_photos': True,
                'is_available': True,
                'is_owner_verified': True,
                'fair_price_status': Property.FairPriceStatus.OVERPRICED,
                'fair_price_percent_diff': 11.5,
                'area_average_rent': Decimal('34000.00'),
                'alleyWidthFeet': 25.0,
                'gas_supply': Property.GasSupplyType.LINE_GAS,
                'waterlogging_risk': Property.WaterloggingRisk.MILD,
                'water_quality': Property.WaterQuality.EXCELLENT,
                'night_safety_rating': 4.7,
                'photos': [
                    ('https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=800', PropertyImage.RoomType.LIVING_ROOM),
                    ('https://images.unsplash.com/photo-1616486338812-3dadae4b4ace?w=800', PropertyImage.RoomType.BEDROOM),
                ],
            },
            {
                'landlord': landlord2,
                'title': 'Female Student Single Room Sublet near NSU & IUB',
                'description': 'Furnished single master bed sublet with attached bath and balcony for female university student. Includes shared high-speed WiFi, microwave, refrigerator, and maid service.',
                'property_type': Property.PropertyType.SUBLET,
                'tenant_category': Property.TenantCategory.BACHELOR_FEMALE,
                'rent_amount': Decimal('8500.00'),
                'security_deposit': Decimal('8500.00'),
                'service_charge': Decimal('1000.00'),
                'estimated_utilities': Decimal('800.00'),
                'bedrooms': 1,
                'bathrooms': 1,
                'balconies': 1,
                'square_feet': 280,
                'floor_level': 3,
                'total_floors': 6,
                'latitude': 23.8156,
                'longitude': 90.4267,
                'area_neighborhood': 'Bashundhara R/A',
                'full_address': 'Block C, Bashundhara R/A, Dhaka',
                'has_geo_tagged_photos': True,
                'is_available': True,
                'is_owner_verified': True,
                'fair_price_status': Property.FairPriceStatus.GREAT_DEAL,
                'fair_price_percent_diff': -10.0,
                'area_average_rent': Decimal('9500.00'),
                'alleyWidthFeet': 20.0,
                'gas_supply': Property.GasSupplyType.CYLINDER,
                'waterlogging_risk': Property.WaterloggingRisk.NONE,
                'water_quality': Property.WaterQuality.EXCELLENT,
                'night_safety_rating': 4.9,
                'photos': [
                    ('https://images.unsplash.com/photo-1598928506311-c55ded91a20c?w=800', PropertyImage.RoomType.BEDROOM),
                    ('https://images.unsplash.com/photo-1584622650111-993a426fbf0a?w=800', PropertyImage.RoomType.WASHROOM),
                ],
            },
        ]

        for p_data in properties_data:
            photos_raw = p_data.pop('photos')
            photos: list[Any] = photos_raw if isinstance(photos_raw, list) else []
            prop, created = Property.objects.update_or_create(
                title=p_data['title'],
                defaults=p_data,
            )
            if created or not prop.images.exists():
                for p_url, r_type in photos:
                    PropertyImage.objects.create(
                        property=prop,
                        image_url=p_url,
                        room_type=r_type,
                        is_geo_tagged=True,
                        captured_at=timezone.now(),
                    )
            success_style = getattr(self.style, 'SUCCESS', str)
            self.stdout.write(success_style(f"Saved property: {prop.title}"))

        success_style = getattr(self.style, 'SUCCESS', str)
        self.stdout.write(success_style('Successfully seeded Dhaka rental properties!'))
