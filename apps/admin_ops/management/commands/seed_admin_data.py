from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.accounts.models import User, LandlordProfile, TenantProfile
from apps.properties.models import Property
from apps.ledger.models import TenancyContract, RentBill
from apps.admin_ops.models import NIDVerificationRequest, GeoPhotoVerification, SpamReport


class Command(BaseCommand):
    help = 'Seeds Super Admin user and initial admin queue items for RentBD'

    def handle(self, *args, **options):
        self.stdout.write('Seeding Super Admin data...')

        # 1. Super Admin
        admin_user, created = User.objects.get_or_create(
            phone_number='+8801700000000',
            defaults={
                'full_name': 'Super Admin (Nafis)',
                'email': 'admin@rentbd.com',
                'role': User.Role.ADMIN,
                'is_staff': True,
                'is_superuser': True,
                'is_phone_verified': True,
            }
        )
        if created:
            admin_user.set_password('Admin@RentBD2026')
            admin_user.save()
            success_style = getattr(self.style, 'SUCCESS', str)
            self.stdout.write(success_style('Created Super Admin user (+8801700000000 / Admin@RentBD2026)'))
        else:
            admin_user.set_password('Admin@RentBD2026')
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.role = User.Role.ADMIN
            admin_user.save()
            self.stdout.write('Updated Super Admin user')

        # 2. Demo Landlord
        landlord, _ = User.objects.get_or_create(
            phone_number='+8801912445566',
            defaults={
                'full_name': 'Tariqul Alam Munna',
                'email': 'tariqul.munna@outlook.com',
                'role': User.Role.LANDLORD,
                'is_phone_verified': True,
            }
        )
        if hasattr(landlord, 'landlord_profile'):
            landlord.landlord_profile.nid_number = '5928174920'
            landlord.landlord_profile.save()

        # 3. Demo Tenant
        tenant, _ = User.objects.get_or_create(
            phone_number='+8801712345678',
            defaults={
                'full_name': 'Rahim Ahmed',
                'email': 'rahim@example.com',
                'role': User.Role.TENANT,
                'is_phone_verified': True,
            }
        )

        # 4. Demo Property
        prop, _ = Property.objects.get_or_create(
            title='Modern 3-Bed Apartment near Mirpur 10 Metro Station',
            defaults={
                'landlord': landlord,
                'description': '3-Bed Flat with line gas and modern elevator',
                'property_type': Property.PropertyType.APARTMENT,
                'tenant_category': Property.TenantCategory.FAMILY,
                'rent_amount': Decimal('24000.00'),
                'security_deposit': Decimal('48000.00'),
                'service_charge': Decimal('3500.00'),
                'area_neighborhood': 'Mirpur 10',
                'full_address': 'House 42, Road 7, Block C, Mirpur 10',
                'latitude': 23.8071,
                'longitude': 90.3686,
                'bedrooms': 3,
                'bathrooms': 3,
                'is_available': True,
                'status': 'active',
            }
        )

        # 5. NID Verification Request
        if not NIDVerificationRequest.objects.filter(nid_number='5928174920').exists():
            NIDVerificationRequest.objects.create(
                landlord=landlord,
                nid_number='5928174920',
                nid_type='smart_card',
                nid_front_url='https://storage.rentbd.com/nid/front/nid-501-f.jpg',
                nid_back_url='https://storage.rentbd.com/nid/back/nid-501-b.jpg',
                live_selfie_url='https://storage.rentbd.com/nid/selfie/selfie-501.jpg',
                ai_face_match_confidence=94.8,
                extracted_data={
                    'name_bangla': 'তারিকুল আলম মুন্না',
                    'name_english': 'TARIQUL ALAM MUNNA',
                    'father_name': 'MOHAMMAD NURUL ALAM',
                    'date_of_birth': '14 May 1985',
                    'address': 'Holding 21, Road 4, Sector 7, Uttara, Dhaka-1230',
                },
                status='pending',
            )
            self.stdout.write('Created NID verification request')

        # 6. Geo-Photo
        if not GeoPhotoVerification.objects.filter(property=prop).exists():
            GeoPhotoVerification.objects.create(
                property=prop,
                landlord_name=landlord.full_name,
                landlord_phone=landlord.phone_number,
                photo_url='https://storage.rentbd.com/props/prop-1001/geo-01.jpg',
                property_lat=23.8071,
                property_lng=90.3686,
                property_address=prop.full_address,
                exif_lat=23.80712,
                exif_lng=90.36858,
                distance_difference_meters=4.0,
                accuracy_meters=5.0,
                is_camera_live=True,
                status='pending',
            )
            self.stdout.write('Created Geo-Photo verification')

        # 7. Spam Report
        if not SpamReport.objects.filter(property=prop).exists():
            SpamReport.objects.create(
                property=prop,
                landlord_name="Shamim 'Media' Dalal",
                landlord_phone='+8801688990011',
                rent_bdt=Decimal('12000.00'),
                average_area_rent=Decimal('68000.00'),
                flags=[
                    {'type': 'suspicious_low_rent', 'description': '82% lower than Dhanmondi avg', 'severity': 'critical'},
                    {'type': 'duplicate_photo', 'description': 'Perceptual hash match (distance: 2 bits)', 'severity': 'critical'},
                ],
                ai_confidence_score=98.4,
                duplicate_match={
                    'original_property_title': 'Luxury Lake-Facing Flat in Gulshan 2',
                    'image_hash_distance': 2,
                    'matched_image_url': 'https://storage.rentbd.com/props/prop-1002/main.jpg',
                    'current_image_url': 'https://storage.rentbd.com/props/prop-1004/main.jpg',
                },
                status='pending_review',
            )
            self.stdout.write('Created AI Spam report')

        # 8. Tenancy & Rent Bill
        contract, _ = TenancyContract.objects.get_or_create(
            property=prop,
            defaults={
                'landlord': landlord,
                'tenant': tenant,
                'agreed_rent': Decimal('24000.00'),
                'service_charge': Decimal('3500.00'),
                'start_date': timezone.now().date(),
            }
        )
        if not RentBill.objects.filter(contract=contract).exists():
            RentBill.objects.create(
                contract=contract,
                billing_month='October 2026',
                base_rent=Decimal('24000.00'),
                service_charge=Decimal('3500.00'),
                total_amount=Decimal('27500.00'),
                status=RentBill.Status.PAID,
                due_date=timezone.now().date(),
                paid_at=timezone.now(),
                payment_method='bKash',
            )
            self.stdout.write('Created sample RentBill')

        success_style = getattr(self.style, 'SUCCESS', str)
        self.stdout.write(success_style('Admin data seeding completed successfully!'))
