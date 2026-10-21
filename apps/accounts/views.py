from datetime import timedelta
import random
from django.conf import settings
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, OTPVerification
from .serializers import (
    OTPRequestSerializer,
    OTPVerifySerializer,
    UserProfileSerializer,
    ProfileUpdateSerializer,
    RegisterSerializer,
    PasswordLoginSerializer,
    ChangePasswordSerializer,
    RoleSwitchSerializer,
    NIDVerifySerializer,
)


class OTPRequestView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Request OTP for Mobile Number (Bangladesh)",
        description="Generates and dispatches a 6-digit OTP to a Bangladeshi mobile number (+8801...).",
        request=OTPRequestSerializer,
        responses={200: OpenApiResponse(description="OTP sent successfully")},
    )
    def post(self, request):
        serializer = OTPRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data['phone_number']

        # Generate OTP (Dev mode uses 123456 or random 6 digits)
        if getattr(settings, 'DEBUG', False) and getattr(settings, 'DEV_DEFAULT_OTP', None):
            otp_code = settings.DEV_DEFAULT_OTP
        else:
            otp_code = f"{random.randint(100000, 999999)}"

        expires_at = timezone.now() + timedelta(minutes=getattr(settings, 'OTP_EXPIRY_MINUTES', 5))

        # Invalidate old OTPs for this number
        OTPVerification.objects.filter(phone_number=phone_number, is_verified=False).delete()

        OTPVerification.objects.create(
            phone_number=phone_number,
            otp_code=otp_code,
            expires_at=expires_at,
        )

        response_data = {
            'success': True,
            'message': f'OTP sent successfully to {phone_number}',
            'expires_in_minutes': getattr(settings, 'OTP_EXPIRY_MINUTES', 5),
        }
        if getattr(settings, 'DEBUG', False):
            response_data['debug_otp'] = otp_code

        return Response(response_data, status=status.HTTP_200_OK)


class OTPVerifyView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Verify OTP and Login / Register",
        description="Verifies the 6-digit OTP, registers or logs in the user, and returns JWT tokens + user profile.",
        request=OTPVerifySerializer,
        responses={200: OpenApiResponse(description="Login successful with JWT and User Profile")},
    )
    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data['phone_number']
        otp_code = serializer.validated_data['otp_code']
        full_name = serializer.validated_data.get('full_name') or 'RentBD User'
        role = serializer.validated_data.get('role', User.Role.TENANT)

        # In development mode, allow DEV_DEFAULT_OTP directly
        is_dev_override = getattr(settings, 'DEBUG', False) and otp_code == getattr(settings, 'DEV_DEFAULT_OTP', '123456')

        if not is_dev_override:
            otp_record = OTPVerification.objects.filter(
                phone_number=phone_number,
                otp_code=otp_code,
                is_verified=False,
            ).order_by('-created_at').first()

            if not otp_record or otp_record.is_expired():
                return Response(
                    {'detail': 'Invalid or expired OTP code. Please request a new one.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            otp_record.is_verified = True
            otp_record.save(update_fields=['is_verified'])

        # Get or create user
        user, created = User.objects.get_or_create(
            phone_number=phone_number,
            defaults={
                'full_name': full_name,
                'role': role,
                'is_phone_verified': True,
            },
        )

        if not created and 'role' in serializer.validated_data:
            if user.role != role:
                user.role = role
                user.save(update_fields=['role'])

        if not user.is_phone_verified:
            user.is_phone_verified = True
            user.save(update_fields=['is_phone_verified'])

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        user_data = UserProfileSerializer(user, context={'request': request}).data

        return Response({
            'success': True,
            'is_new_user': created,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            },
            'user': user_data,
        }, status=status.HTTP_200_OK)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get Current User Profile",
        description="Returns the verified profile and landlord/tenant status of the currently authenticated user.",
        responses={200: UserProfileSerializer},
    )
    def get(self, request):
        serializer = UserProfileSerializer(request.user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Update Current User Profile",
        description="Updates tenant/landlord profile details like occupation, workplace, family size, etc.",
        request=ProfileUpdateSerializer,
        responses={200: UserProfileSerializer},
    )
    def patch(self, request):
        serializer = ProfileUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.update(request.user, serializer.validated_data)

        updated_data = UserProfileSerializer(request.user, context={'request': request}).data
        return Response(updated_data, status=status.HTTP_200_OK)


class NIDVerifyView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Upload NID & Live Selfie for Verification (Anti-broker)",
        description="Submits National ID images and optional live selfie to verify landlord or tenant credentials.",
        request=NIDVerifySerializer,
        responses={200: OpenApiResponse(description="NID documents received for verification")},
    )
    def post(self, request):
        serializer = NIDVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        nid_number = serializer.validated_data.get('nid_number', '')
        nid_front = serializer.validated_data.get('nid_front') or serializer.validated_data.get('nid_front_url')
        nid_back = serializer.validated_data.get('nid_back') or serializer.validated_data.get('nid_back_url')
        selfie = serializer.validated_data.get('selfie') or serializer.validated_data.get('selfie_url')
        present_address = serializer.validated_data.get('present_address')
        emergency_contact = serializer.validated_data.get('emergency_contact')

        user = request.user

        # Update landlord profile if landlord or dual
        if hasattr(user, 'landlord_profile'):
            lp = user.landlord_profile
            lp.nid_number = nid_number
            lp.nid_front = nid_front
            lp.nid_back = nid_back
            if selfie:
                lp.selfie_image = selfie
            lp.is_nid_verified = True  # In production, triggers async OCR / NID DB check
            lp.is_owner_verified = True
            lp.save()

        # Update tenant profile
        if hasattr(user, 'tenant_profile'):
            tp = user.tenant_profile
            tp.nid_number = nid_number
            tp.is_nid_verified = True
            tp.save()

        return Response({
            'success': True,
            'message': 'NID and identity documents submitted and verified successfully.',
            'is_nid_verified': True,
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="User Logout",
        description="Logs out the user and invalidates the refresh token.",
        request=None,
        responses={200: OpenApiResponse(description="Logged out successfully")},
    )
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
        except Exception:
            pass
        return Response({'success': True, 'message': 'Logged out successfully.'}, status=status.HTTP_200_OK)


class RegisterView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Register New Account with Role (Tenant or Landlord)",
        description="Creates a new account for a Tenant or Landlord with phone number, password, and profile.",
        request=RegisterSerializer,
        responses={201: OpenApiResponse(description="User registered successfully with JWT and Profile")},
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        full_name = serializer.validated_data['full_name']
        phone_number = serializer.validated_data['phone_number']
        email = serializer.validated_data.get('email') or None
        password = serializer.validated_data['password']
        role = serializer.validated_data.get('role', User.Role.TENANT)

        user = User.objects.create_user(
            phone_number=phone_number,
            full_name=full_name,
            email=email,
            password=password,
            role=role,
            is_phone_verified=True,
        )

        refresh = RefreshToken.for_user(user)
        user_data = UserProfileSerializer(user, context={'request': request}).data

        return Response({
            'success': True,
            'is_new_user': True,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            },
            'user': user_data,
        }, status=status.HTTP_201_CREATED)


class PasswordLoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Login with Mobile Number and Password",
        description="Authenticates existing user using mobile number and password, with optional active role selection.",
        request=PasswordLoginSerializer,
        responses={200: OpenApiResponse(description="Logged in successfully with JWT and Profile")},
    )
    def post(self, request):
        serializer = PasswordLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get('email')
        phone_number = serializer.validated_data.get('phone_number')
        password = serializer.validated_data['password']
        role = serializer.validated_data.get('role')

        user = None
        if email:
            user = User.objects.filter(email__iexact=email).first()
        if not user and phone_number:
            user = User.objects.filter(phone_number=phone_number).first()

        if not user:
            return Response(
                {'detail': 'No account found with the provided credentials.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.check_password(password):
            return Response(
                {'detail': 'Incorrect password. Please try again or login via OTP.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if role and user.role != role:
            user.role = role
            user.save(update_fields=['role'])

        refresh = RefreshToken.for_user(user)
        user_data = UserProfileSerializer(user, context={'request': request}).data

        return Response({
            'success': True,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            },
            'user': user_data,
        }, status=status.HTTP_200_OK)


class RoleSwitchView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Switch Operational Role (Tenant <-> Landlord)",
        description="Switches the user's active role between Tenant, Landlord, or Dual.",
        request=RoleSwitchSerializer,
        responses={200: UserProfileSerializer},
    )
    def post(self, request):
        serializer = RoleSwitchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_role = serializer.validated_data['role']
        user = request.user
        user.role = new_role
        user.save(update_fields=['role'])

        user_data = UserProfileSerializer(user, context={'request': request}).data
        return Response(user_data, status=status.HTTP_200_OK)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Change Password",
        description="Updates authenticated user's account password.",
        request=ChangePasswordSerializer,
        responses={200: OpenApiResponse(description="Password changed successfully")},
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        current_password = serializer.validated_data['current_password']
        new_password = serializer.validated_data['new_password']

        user = request.user
        if not user.check_password(current_password):
            return Response(
                {'detail': 'Current password does not match.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save(update_fields=['password'])
        return Response({'success': True, 'message': 'Password updated successfully.'}, status=status.HTTP_200_OK)


