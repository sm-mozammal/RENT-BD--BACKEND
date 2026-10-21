# RentBD Mobile & Web API Reference Manual

> **Version:** 1.0.0  
> **Framework:** Django 6.1 + Django REST Framework + SimpleJWT + PostGIS  
> **Swagger UI:** `http://127.0.0.1:8000/api/docs/`  
> **Redoc UI:** `http://127.0.0.1:8000/api/redoc/`  
> **OpenAPI Schema (YAML):** `http://127.0.0.1:8000/api/schema/`

---

## 📑 Table of Contents

1. [Environment & Base URLs](#1-environment--base-urls)
2. [Authentication & JWT Headers](#2-authentication--jwt-headers)
3. [Module 1: Authentication & Account Management (`/api/v1/auth/`)](#module-1-authentication--account-management)
4. [Module 2: Property Listings & Operations (`/api/v1/properties/`)](#module-2-property-listings--operations)
5. [Module 3: AI Intelligence & Differentiators (`/api/v1/properties/ai...`)](#module-3-ai-intelligence--differentiators)
6. [Module 4: GIS, Commute & Geospatial Search (`/api/v1/properties/...`)](#module-4-gis-commute--geospatial-search)
7. [Module 5: Saved Searches & Push Alerts (`/api/v1/properties/saved-searches/`)](#module-5-saved-searches--push-alerts)
8. [Module 6: Affiliate Partner Services (`/api/v1/properties/services/`)](#module-6-affiliate-partner-services)
9. [Module 7: Inquiries & Physical Visit Bookings (`/api/v1/inquiries/`)](#module-7-inquiries--physical-visit-bookings)
10. [Module 8: Crowdsourced Area Insights (`/api/v1/insights/`)](#module-8-crowdsourced-area-insights)
11. [Module 9: Digital Tenancy Ledger & Rent Bills (`/api/v1/ledger/`)](#module-9-digital-tenancy-ledger--rent-bills)
12. [Module 10: In-App Chat & Masked Calling (`/api/v1/chat/`)](#module-10-in-app-chat--masked-calling)
13. [Module 11: Super Admin & Operations Management (`/api/v1/admin/`)](#module-11-super-admin--operations-management)
14. [Complete Master API Audit Matrix (All 67 Endpoints)](#complete-master-api-audit-matrix)

---

## 1. Environment & Base URLs

| Client Environment | Base URL Prefix | Description |
| :--- | :--- | :--- |
| **Android Emulator** | `http://10.0.2.2:8000/api/v1` | Android loopback adapter |
| **iOS Simulator / macOS App** | `http://127.0.0.1:8000/api/v1` | Local loopback interface |
| **Physical Mobile Device (LAN)**| `http://<DEV_PC_LOCAL_IP>:8000/api/v1` | Shared Wi-Fi subnet |
| **Production Server** | `https://api.rentbd.com/api/v1` | Production HTTPS Gateway |

---

## 2. Authentication & JWT Headers

Endpoints marked with **Bearer Token** require the standard HTTP Authorization header:

```http
Authorization: Bearer <access_token>
```

### Lifespans & Policies
- **Access Token:** 7 days
- **Refresh Token:** 60 days (Rotation enabled via `/api/v1/auth/token/refresh/`)
- **Roles:** `tenant`, `landlord`, `admin` (or dual capability with instant switching)

---

## Module 1: Authentication & Account Management

Base URI: `/api/v1/auth/`

### 1.1 Request OTP for Bangladeshi Mobile
* **Route:** `POST /api/v1/auth/otp/request/`
* **Permission:** Public (`AllowAny`)
* **Request Body:**
```json
{
  "phone_number": "+8801712345678"
}
```
* **Response (200 OK):**
```json
{
  "success": true,
  "message": "OTP sent successfully to +8801712345678",
  "expires_in_seconds": 300,
  "dev_otp": "123456"
}
```

---

### 1.2 Verify OTP & Login / Auto-Register
* **Route:** `POST /api/v1/auth/otp/verify/`
* **Permission:** Public (`AllowAny`)
* **Request Body:**
```json
{
  "phone_number": "+8801712345678",
  "otp_code": "123456",
  "full_name": "Rahim Ahmed",
  "role": "tenant"
}
```
* **Response (200 OK):**
```json
{
  "success": true,
  "tokens": {
    "access": "eyJhbGciOiJIUzI1NiIsIn...",
    "refresh": "eyJhbGciOiJIUzI1NiIsIn..."
  },
  "user": {
    "id": "e0b4a72d-8302-4ef8-a55b-f73967dcb638",
    "phoneNumber": "+8801712345678",
    "fullName": "Rahim Ahmed",
    "role": "tenant",
    "isTenant": true,
    "isLandlord": false,
    "isNidVerified": false
  }
}
```

---

### 1.3 Register with Password
* **Route:** `POST /api/v1/auth/register/`
* **Permission:** Public (`AllowAny`)
* **Request Body:**
```json
{
  "phone_number": "+8801811223344",
  "password": "SecurePassword123!",
  "full_name": "Tariqul Alam",
  "role": "landlord",
  "email": "tariqul@example.com"
}
```
* **Response (201 Created):**
```json
{
  "success": true,
  "message": "User registered successfully",
  "tokens": {
    "access": "eyJhbGciOiJIUzI1NiIsIn...",
    "refresh": "eyJhbGciOiJIUzI1NiIsIn..."
  },
  "user": {
    "id": "5f9e17b8-b4b7-4b77-8c3b-d5a23f4625b1",
    "phoneNumber": "+8801811223344",
    "fullName": "Tariqul Alam",
    "role": "landlord",
    "isTenant": false,
    "isLandlord": true
  }
}
```

---

### 1.4 Login with Phone & Password
* **Route:** `POST /api/v1/auth/login/`
* **Permission:** Public (`AllowAny`)
* **Request Body:**
```json
{
  "phone_number": "+8801811223344",
  "password": "SecurePassword123!"
}
```
* **Response (200 OK):**
```json
{
  "success": true,
  "tokens": {
    "access": "eyJhbGciOiJIUzI1NiIsIn...",
    "refresh": "eyJhbGciOiJIUzI1NiIsIn..."
  },
  "user": {
    "id": "5f9e17b8-b4b7-4b77-8c3b-d5a23f4625b1",
    "phoneNumber": "+8801811223344",
    "fullName": "Tariqul Alam",
    "role": "landlord",
    "isTenant": false,
    "isLandlord": true
  }
}
```

---

### 1.5 Refresh JWT Session Token
* **Route:** `POST /api/v1/auth/token/refresh/`
* **Permission:** Public (`AllowAny`)
* **Request Body:**
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsIn..."
}
```
* **Response (200 OK):**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsIn...new_access_token...",
  "refresh": "eyJhbGciOiJIUzI1NiIsIn...new_rotated_refresh_token..."
}
```

---

### 1.6 Switch Active User Role (Tenant <-> Landlord)
* **Route:** `POST /api/v1/auth/role/switch/`
* **Permission:** Bearer Token
* **Request Body:**
```json
{
  "role": "landlord"
}
```
* **Response (200 OK):**
```json
{
  "success": true,
  "role": "landlord",
  "isTenant": false,
  "isLandlord": true
}
```

---

### 1.7 Change Password
* **Route:** `POST /api/v1/auth/change-password/`
* **Permission:** Bearer Token
* **Request Body:**
```json
{
  "old_password": "OldPassword123!",
  "new_password": "NewSecurePassword456!"
}
```
* **Response (200 OK):**
```json
{
  "success": true,
  "message": "Password changed successfully."
}
```

---

### 1.8 Logout & Blacklist Token
* **Route:** `POST /api/v1/auth/logout/`
* **Permission:** Bearer Token
* **Request Body:**
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsIn..."
}
```
* **Response (200 OK):**
```json
{
  "success": true,
  "message": "Logged out successfully."
}
```

---

### 1.9 User Profile (Get & Update)
* **Route:** `GET /api/v1/auth/profile/` | `PATCH /api/v1/auth/profile/`
* **Permission:** Bearer Token
* **PATCH Request Body:**
```json
{
  "full_name": "Rahim Ahmed",
  "email": "rahim@example.com",
  "occupation": "Software Engineer",
  "workplace": "Brain Station 23",
  "family_size": 3,
  "emergency_contact": "+8801912345678"
}
```
* **Response (200 OK):**
```json
{
  "id": "e0b4a72d-8302-4ef8-a55b-f73967dcb638",
  "phoneNumber": "+8801712345678",
  "fullName": "Rahim Ahmed",
  "role": "tenant",
  "occupation": "Software Engineer",
  "workplace": "Brain Station 23",
  "familySize": 3,
  "isNidVerified": false
}
```

---

### 1.10 Landlord NID Verification Submission
* **Route:** `POST /api/v1/auth/nid-verify/`
* **Permission:** Bearer Token (Landlord)
* **Request Body (Multipart Form or JSON):**
```json
{
  "nid_number": "19901234567890123",
  "date_of_birth": "1990-05-14",
  "full_name_bangla": "রহিম আহমেদ"
}
```
* **Response (200 OK):**
```json
{
  "success": true,
  "message": "NID verification submitted for review.",
  "is_nid_verified": true
}
```

---

## Module 2: Property Listings & Operations

Base URI: `/api/v1/properties/`

### 2.1 List & Filter Properties / Create Listing
* **Route:** `GET /api/v1/properties/` | `POST /api/v1/properties/`
* **Permission:** `GET` Public | `POST` Landlord
* **GET Query Parameters:**
  - `city` (e.g., `Dhaka`)
  - `area` (e.g., `Mirpur 10`)
  - `property_type` (`APARTMENT`, `SUBLET`, `COMMERCIAL`, `ROOM`, `HOSTEL`)
  - `tenant_category` (`FAMILY`, `BACHELOR_MALE`, `BACHELOR_FEMALE`, `ANY`)
  - `min_rent`, `max_rent`
  - `bedrooms`, `bathrooms`
  - `has_gas_cylinder`, `has_line_gas`, `has_generator`, `has_lift`
  - `page`, `page_size`
* **POST Request Body:**
```json
{
  "title": "Modern 3-Bed Apartment near Metro Station",
  "description": "Well-ventilated flat with line gas and dedicated parking.",
  "property_type": "APARTMENT",
  "tenant_category": "FAMILY",
  "rent_amount": "24000.00",
  "security_deposit": "48000.00",
  "service_charge": "3500.00",
  "area_neighborhood": "Mirpur 10",
  "full_address": "House 42, Road 7, Block C, Mirpur 10, Dhaka",
  "latitude": 23.8071,
  "longitude": 90.3686,
  "bedrooms": 3,
  "bathrooms": 3,
  "balconies": 2,
  "square_feet": 1250,
  "floor_level": 4,
  "has_lift": true,
  "has_generator": true,
  "has_line_gas": true
}
```
* **Response (201 Created):**
```json
{
  "id": "84a4a584-6fb0-4e36-b6b6-8bb09825b741",
  "title": "Modern 3-Bed Apartment near Metro Station",
  "rent_amount": "24000.00",
  "security_deposit": "48000.00",
  "status": "active",
  "is_available": true,
  "fair_price_status": "FAIR_PRICE",
  "created_at": "2026-10-21T18:00:00Z"
}
```

---

### 2.2 Property Details, Partial Update & Delete
* **Route:** `GET /api/v1/properties/<uuid:id>/` | `PATCH /api/v1/properties/<uuid:id>/` | `DELETE /api/v1/properties/<uuid:id>/`
* **Permission:** `GET` Public | `PATCH`, `DELETE` Owner Landlord
* **Response (200 OK):**
```json
{
  "id": "84a4a584-6fb0-4e36-b6b6-8bb09825b741",
  "title": "Modern 3-Bed Apartment near Metro Station",
  "description": "Well-ventilated flat with line gas and dedicated parking.",
  "property_type": "APARTMENT",
  "tenant_category": "FAMILY",
  "rent_amount": "24000.00",
  "security_deposit": "48000.00",
  "service_charge": "3500.00",
  "total_monthly_est": "27500.00",
  "area_neighborhood": "Mirpur 10",
  "full_address": "House 42, Road 7, Block C, Mirpur 10, Dhaka",
  "latitude": 23.8071,
  "longitude": 90.3686,
  "bedrooms": 3,
  "bathrooms": 3,
  "balconies": 2,
  "square_feet": 1250,
  "is_vaulted": false,
  "fair_price_status": "FAIR_PRICE",
  "photos": [],
  "landlord": {
    "id": "5f9e17b8-b4b7-4b77-8c3b-d5a23f4625b1",
    "name": "Tariqul Alam",
    "is_nid_verified": true,
    "phone": "+8801811223344"
  }
}
```

---

### 2.3 Toggle Off-Market Digital Vault
* **Route:** `POST /api/v1/properties/<uuid:id>/toggle-vault/`
* **Permission:** Owner Landlord
* **Request Body:** `{}`
* **Response (200 OK):**
```json
{
  "id": "84a4a584-6fb0-4e36-b6b6-8bb09825b741",
  "is_vaulted": true,
  "message": "Property moved to off-market digital vault."
}
```

---

### 2.4 Save / Bookmark Property Toggle
* **Route:** `POST /api/v1/properties/<uuid:id>/save/`
* **Permission:** Bearer Token
* **Request Body:** `{}`
* **Response (200 OK):**
```json
{
  "success": true,
  "is_saved": true,
  "property_id": "84a4a584-6fb0-4e36-b6b6-8bb09825b741"
}
```

---

### 2.5 List Saved / Bookmarked Properties
* **Route:** `GET /api/v1/properties/saved/`
* **Permission:** Bearer Token
* **Response (200 OK):** List of saved Property objects.

---

### 2.6 Upload Property Photos with EXIF Geo-Extraction
* **Route:** `POST /api/v1/properties/<uuid:id>/photos/`
* **Permission:** Owner Landlord
* **Content-Type:** `multipart/form-data`
* **Form Fields:**
  - `image`: binary image file (JPEG/PNG)
  - `tag`: `BEDROOM`, `LIVING`, `KITCHEN`, `BATHROOM`, `BUILDING_EXTERIOR`, `BALCONY`
* **Response (201 Created):**
```json
{
  "id": "d13ab024-e133-4f92-9988-cb732b145112",
  "image": "http://127.0.0.1:8000/media/property_photos/mirpur_balcony.jpg",
  "tag": "BALCONY",
  "is_cover": false,
  "has_exif_gps": true,
  "extracted_latitude": 23.80712,
  "extracted_longitude": 90.36865
}
```

---

### 2.7 15-Day Cycle Availability Confirmation
* **Route:** `POST /api/v1/properties/<uuid:id>/confirm-availability/`
* **Permission:** Owner Landlord
* **Response (200 OK):**
```json
{
  "success": true,
  "property_id": "84a4a584-6fb0-4e36-b6b6-8bb09825b741",
  "message": "Listing availability confirmed and 15-day cycle refreshed.",
  "availability_confirmed_at": "2026-10-21T18:30:00Z"
}
```

---

### 2.8 Monetization Boost Listing
* **Route:** `POST /api/v1/properties/<uuid:id>/boost/`
* **Permission:** Owner Landlord
* **Request Body:**
```json
{
  "tier": "featured_7d",
  "payment_method": "bkash"
}
```
* **Response (200 OK):**
```json
{
  "success": true,
  "property_id": "84a4a584-6fb0-4e36-b6b6-8bb09825b741",
  "is_featured": true,
  "featured_until": "2026-10-28T18:30:00Z",
  "transaction_id": "TRX-BKASH-883921"
}
```

---

## Module 3: AI Intelligence & Differentiators

Base URI: `/api/v1/properties/`

### 3.1 AI Natural Language Search (Bangla & English)
* **Route:** `GET /api/v1/properties/ai_search/`
* **Permission:** Public
* **Query Parameters:** `q` (e.g., `3 bed near mirpur 10 metro station line gas under 25k`)
* **Response (200 OK):**
```json
{
  "query": "3 bed near mirpur 10 metro station line gas under 25k",
  "parsed_criteria": {
    "bedrooms": 3,
    "area": "Mirpur 10",
    "max_rent": 25000,
    "has_line_gas": true
  },
  "results_count": 8,
  "results": [...]
}
```

---

### 3.2 AI Listing Writer (Bengali & English Description Generator)
* **Route:** `POST /api/v1/properties/ai-generate-description/`
* **Permission:** Bearer Token
* **Request Body:**
```json
{
  "area": "Mirpur 10",
  "bedrooms": 3,
  "bathrooms": 3,
  "rent": 24000,
  "features": ["Near metro station", "Line gas", "Lift & Generator"],
  "language": "bn"
}
```
* **Response (200 OK):**
```json
{
  "success": true,
  "description": "মিরপুর ১০ মেট্রো স্টেশনের একদম সন্নিকটে মনোরম ৩ বেডরুমের ফ্ল্যাট ভাড়া...",
  "suggested_tags": ["Mirpur 10", "Metro Nearby", "Line Gas", "Family Flat"]
}
```

---

### 3.3 AI Photo Room Classifier
* **Route:** `POST /api/v1/properties/ai/classify-photo/`
* **Permission:** Public
* **Request Body (Multipart Form):**
  - `photo`: binary image
* **Response (200 OK):**
```json
{
  "suggested_category": "BEDROOM",
  "confidence_score": 0.94,
  "features_detected": ["bed", "wardrobe", "window", "tiled_floor"]
}
```

---

### 3.4 AI Fair-Rent Value Meter
* **Route:** `GET /api/v1/properties/<uuid:id>/fair-rent-meter/`
* **Permission:** Public
* **Response (200 OK):**
```json
{
  "property_id": "84a4a584-6fb0-4e36-b6b6-8bb09825b741",
  "asking_rent": 24000.0,
  "fair_market_rent": 23500.0,
  "variance_percentage": 2.1,
  "status": "FAIR_PRICE",
  "explanation": "Rent is within 2.1% of similar 3-bed apartments in Mirpur 10 with line gas.",
  "confidence_score": 0.91
}
```

---

### 3.5 AI Rent Agreement PDF Generator
* **Route:** `POST /api/v1/properties/ai/generate-agreement/`
* **Permission:** Bearer Token
* **Request Body:**
```json
{
  "property_id": "84a4a584-6fb0-4e36-b6b6-8bb09825b741",
  "tenant_id": "e0b4a72d-8302-4ef8-a55b-f73967dcb638",
  "monthly_rent": 24000,
  "security_deposit": 48000,
  "duration_months": 12,
  "start_date": "2026-11-01"
}
```
* **Response (200 OK):**
```json
{
  "success": true,
  "contract_id": "78ffbc10-d881-42ab-b19b-cba019284192",
  "pdf_download_url": "http://127.0.0.1:8000/media/agreements/contract_78ffbc10.pdf",
  "clauses_count": 14
}
```

---

### 3.6 Move-In Total Upfront Cost Calculator
* **Route:** `POST /api/v1/properties/calculate-move-in/` | `POST /api/v1/properties/<uuid:id>/move-in-cost/`
* **Permission:** Public
* **Request Body (General):**
```json
{
  "monthly_rent": 24000,
  "security_deposit_months": 2,
  "service_charge": 3500,
  "moving_truck_needed": true,
  "cleaning_needed": true
}
```
* **Response (200 OK):**
```json
{
  "breakdown": {
    "first_month_rent": 24000.0,
    "security_deposit": 48000.0,
    "service_charge": 3500.0,
    "estimated_shifting": 6000.0,
    "deep_cleaning": 2500.0,
    "platform_convenience_fee": 0.0
  },
  "total_upfront_bdt": 84000.0
}
```

---

### 3.7 Compare 2 to 4 Properties
* **Route:** `POST /api/v1/properties/compare/`
* **Permission:** Public
* **Request Body:**
```json
{
  "property_ids": [
    "84a4a584-6fb0-4e36-b6b6-8bb09825b741",
    "91b3b123-4410-41ab-a12b-ffa019283011"
  ]
}
```
* **Response (200 OK):** Side-by-side metric comparison object.

---

### 3.8 AI Anti-Broker Duplicate & Spam Detector
* **Route:** `POST /api/v1/properties/admin/detect-spam/`
* **Permission:** Public / Staff
* **Request Body:**
```json
{
  "title": "Flat for rent in Dhanmondi",
  "description": "Call broker immediately 01700000000",
  "phone_number": "01700000000"
}
```
* **Response (200 OK):**
```json
{
  "is_spam": true,
  "risk_score": 0.88,
  "triggers": ["Multiple phone numbers in description", "Broker keyword pattern detected"]
}
```

---

## Module 4: GIS, Commute & Geospatial Search

Base URI: `/api/v1/properties/`

### 4.1 Draw-on-Map Polygon Search
* **Route:** `POST /api/v1/properties/draw-search/`
* **Permission:** Public
* **Request Body:**
```json
{
  "polygon_coordinates": [
    {"lat": 23.8050, "lng": 90.3650},
    {"lat": 23.8120, "lng": 90.3650},
    {"lat": 23.8120, "lng": 90.3750},
    {"lat": 23.8050, "lng": 90.3750},
    {"lat": 23.8050, "lng": 90.3650}
  ]
}
```
* **Response (200 OK):** List of properties physically located inside the custom polygon boundary.

---

### 4.2 Office Commute Duration Calculator
* **Route:** `POST /api/v1/properties/commute-calculator/`
* **Permission:** Public
* **Request Body:**
```json
{
  "property_latitude": 23.8071,
  "property_longitude": 90.3686,
  "destination_latitude": 23.7465,
  "destination_longitude": 90.3760,
  "transit_mode": "metro_and_walk"
}
```
* **Response (200 OK):**
```json
{
  "commute_time_minutes": 26,
  "distance_km": 8.4,
  "route_summary": "Walk 350m to Mirpur 10 Station -> MRT Line 6 to Karwan Bazar -> Walk 500m",
  "peak_traffic_multiplier": 1.2
}
```

---

### 4.3 Nearby Essentials Radar (Bazaar, Metro, School, Hospital)
* **Route:** `GET /api/v1/properties/<uuid:id>/nearby-essentials/`
* **Permission:** Public
* **Response (200 OK):**
```json
{
  "metro_stations": [{"name": "Mirpur 10 Metro Station", "distance_meters": 350}],
  "kitchen_markets": [{"name": "Mirpur 10 Kacha Bazaar", "distance_meters": 450}],
  "hospitals": [{"name": "Al Helal Specialized Hospital", "distance_meters": 600}],
  "schools": [{"name": "Monipur High School", "distance_meters": 800}]
}
```

---

### 4.4 Street View Simulation
* **Route:** `GET /api/v1/properties/<uuid:id>/street-view/`
* **Permission:** Public
* **Response (200 OK):**
```json
{
  "property_id": "84a4a584-6fb0-4e36-b6b6-8bb09825b741",
  "street_view_available": true,
  "panorama_url": "https://maps.googleapis.com/maps/api/streetview?...",
  "heading": 180,
  "pitch": 0
}
```

---

### 4.5 Demand vs Supply Heatmap Geospatial Telemetry
* **Route:** `GET /api/v1/properties/analytics/demand-supply-heatmap/`
* **Permission:** Public
* **Response (200 OK):** GeoJSON array of Dhaka/Chittagong hubs with rental search density vs listing supply ratios.

---

## Module 5: Saved Searches & Push Alerts

Base URI: `/api/v1/properties/saved-searches/`

### 5.1 List & Create Saved Search Triggers
* **Route:** `GET /api/v1/properties/saved-searches/` | `POST /api/v1/properties/saved-searches/`
* **Permission:** Bearer Token
* **POST Request Body:**
```json
{
  "title": "Mirpur 10 Family 3-Bed",
  "area": "Mirpur 10",
  "max_rent": 25000,
  "bedrooms": 3,
  "has_line_gas": true,
  "notify_email": true,
  "notify_push": true
}
```
* **Response (201 Created):**
```json
{
  "id": "e45b0a11-8012-429a-99ab-66a012948111",
  "title": "Mirpur 10 Family 3-Bed",
  "is_active": true,
  "created_at": "2026-10-21T18:00:00Z"
}
```

---

### 5.2 List Unread Saved Search Instant Alerts
* **Route:** `GET /api/v1/properties/saved-searches/alerts/`
* **Permission:** Bearer Token
* **Response (200 OK):** List of matching property alerts triggered for user's saved searches.

---

### 5.3 Mark Saved Search Alert as Read
* **Route:** `PATCH /api/v1/properties/saved-searches/alerts/<uuid:id>/read/`
* **Permission:** Bearer Token
* **Request Body:** `{}`
* **Response (200 OK):**
```json
{
  "id": "alert-uuid",
  "is_read": true
}
```

---

## Module 6: Affiliate Partner Services

Base URI: `/api/v1/properties/services/`

### 6.1 List Verified Moving & Home Care Partners
* **Route:** `GET /api/v1/properties/services/partners/`
* **Permission:** Public
* **Query Parameters:** `service_type` (`moving_truck`, `deep_cleaning`, `pest_control`, `painting`)
* **Response (200 OK):**
```json
[
  {
    "id": "truck-lagbe",
    "name": "Truck Lagbe",
    "service_type": "moving_truck",
    "rating": 4.8,
    "discount_code": "RENTBD10",
    "discount_pct": 10
  }
]
```

---

### 6.2 Book Partner Service
* **Route:** `POST /api/v1/properties/services/book/`
* **Permission:** Bearer Token
* **Request Body:**
```json
{
  "partner_id": "truck-lagbe",
  "preferred_date": "2026-11-01",
  "from_address": "Dhanmondi 27",
  "to_address": "Mirpur 10",
  "contact_phone": "+8801712345678"
}
```
* **Response (201 Created):**
```json
{
  "success": true,
  "booking_reference": "SRV-TL-99214",
  "status": "CONFIRMED"
}
```

---

## Module 7: Inquiries & Physical Visit Bookings

Base URI: `/api/v1/inquiries/`

### 7.1 Submit Verified Tenant Inquiry
* **Route:** `POST /api/v1/inquiries/`
* **Permission:** Bearer Token (Tenant)
* **Request Body:**
```json
{
  "property": "84a4a584-6fb0-4e36-b6b6-8bb09825b741",
  "proposed_rent": "23500.00",
  "tenant_occupation": "Software Architect",
  "tenant_workplace": "Brain Station 23",
  "family_members_count": 3,
  "message": "We are a small family looking to move in from 1st November."
}
```
* **Response (201 Created):**
```json
{
  "id": "inquiry-uuid",
  "status": "PENDING",
  "created_at": "2026-10-21T18:00:00Z"
}
```

---

### 7.2 Landlord Tenant KYC Screening Inbox
* **Route:** `GET /api/v1/inquiries/landlord-inbox/`
* **Permission:** Landlord
* **Response (200 OK):** List of inquiries with applicant full name, employer, occupation, family size, and NID verified badge.

---

### 7.3 Update Inquiry Status (Approve / Reject)
* **Route:** `PATCH /api/v1/inquiries/<uuid:id>/status/`
* **Permission:** Landlord
* **Request Body:**
```json
{
  "status": "APPROVED",
  "rejection_reason": ""
}
```
* **Response (200 OK):** Updated inquiry object.

---

### 7.4 Physical Flat Visit Booking (List & Create)
* **Route:** `GET /api/v1/inquiries/visits/` | `POST /api/v1/inquiries/visits/`
* **Permission:** Bearer Token
* **POST Request Body:**
```json
{
  "property": "84a4a584-6fb0-4e36-b6b6-8bb09825b741",
  "scheduled_date": "2026-10-25",
  "scheduled_time_slot": "AFTERNOON_4_6PM",
  "notes": "Will come with my spouse"
}
```
* **Response (201 Created):**
```json
{
  "id": "visit-uuid",
  "status": "SCHEDULED",
  "scheduled_date": "2026-10-25",
  "scheduled_time_slot": "AFTERNOON_4_6PM"
}
```

---

### 7.5 Update Visit Booking Status (Accept / Reschedule / Cancel)
* **Route:** `PATCH /api/v1/inquiries/visits/<uuid:id>/status/`
* **Permission:** Bearer Token (Landlord or Tenant)
* **Request Body:**
```json
{
  "status": "COMPLETED"
}
```
* **Response (200 OK):** Updated visit booking record.

---

## Module 8: Crowdsourced Area Insights

Base URI: `/api/v1/insights/`

### 8.1 Fetch Aggregated Area Insights
* **Route:** `GET /api/v1/insights/area/`
* **Permission:** Public
* **Query Parameters:** `area_name` (e.g., `Mirpur 10`)
* **Response (200 OK):**
```json
{
  "area_name": "Mirpur 10",
  "total_reviews": 48,
  "gas_supply_score": 4.2,
  "water_quality_score": 3.9,
  "waterlogging_monsoon_score": 4.6,
  "safety_score_night": 4.1,
  "internet_isp_coverage": ["Carnival", "Link3", "Dot Internet"],
  "recent_resident_tips": [
    "Line gas pressure stays strong even during morning cooking hours.",
    "Road 7 does not submerge during heavy monsoon downpours."
  ]
}
```

---

### 8.2 Submit Resident Area Review
* **Route:** `POST /api/v1/insights/submit/`
* **Permission:** Bearer Token
* **Request Body:**
```json
{
  "area_name": "Mirpur 10",
  "gas_rating": 5,
  "water_rating": 4,
  "waterlogging_rating": 5,
  "night_safety_rating": 4,
  "comments": "Very quiet residential block near metro station."
}
```
* **Response (201 Created):**
```json
{
  "success": true,
  "message": "Resident insight recorded. Thank you for helping renters!"
}
```

---

## Module 9: Digital Tenancy Ledger & Rent Bills

Base URI: `/api/v1/ledger/`

### 9.1 Active Tenancies (List & Create Contract)
* **Route:** `GET /api/v1/ledger/tenancies/` | `POST /api/v1/ledger/tenancies/`
* **Permission:** Bearer Token
* **POST Request Body:**
```json
{
  "property": "84a4a584-6fb0-4e36-b6b6-8bb09825b741",
  "tenant": "e0b4a72d-8302-4ef8-a55b-f73967dcb638",
  "start_date": "2026-11-01",
  "end_date": "2027-10-31",
  "monthly_rent": "24000.00",
  "security_deposit": "48000.00",
  "service_charge": "3500.00"
}
```
* **Response (201 Created):**
```json
{
  "id": "tenancy-uuid",
  "status": "ACTIVE",
  "monthly_rent": "24000.00"
}
```

---

### 9.2 Monthly Rent Bills (List & Issue Bill)
* **Route:** `GET /api/v1/ledger/bills/` | `POST /api/v1/ledger/bills/`
* **Permission:** `GET` Bearer | `POST` Landlord
* **POST Request Body:**
```json
{
  "contract": "tenancy-uuid",
  "billing_month": "2026-11-01",
  "rent_amount": "24000.00",
  "service_charge": "3500.00",
  "electricity_bill": "1850.00",
  "gas_bill": "1080.00",
  "water_bill": "600.00",
  "due_date": "2026-11-10"
}
```
* **Response (201 Created):**
```json
{
  "id": "bill-uuid",
  "total_amount": "31030.00",
  "status": "UNPAID",
  "due_date": "2026-11-10"
}
```

---

### 9.3 Mark Rent Bill Paid
* **Route:** `POST /api/v1/ledger/bills/<uuid:id>/mark-paid/`
* **Permission:** Landlord
* **Request Body:**
```json
{
  "payment_method": "bkash",
  "transaction_id": "TRX99214A"
}
```
* **Response (200 OK):**
```json
{
  "id": "bill-uuid",
  "status": "PAID",
  "paid_at": "2026-11-05T10:00:00Z",
  "receipt_number": "REC-2026-11-0012"
}
```

---

### 9.4 Official Digital Rent Receipt Detail
* **Route:** `GET /api/v1/ledger/bills/<uuid:id>/receipt/`
* **Permission:** Bearer Token (Landlord or Tenant)
* **Response (200 OK):**
```json
{
  "receipt_number": "REC-2026-11-0012",
  "tenant_name": "Rahim Ahmed",
  "landlord_name": "Tariqul Alam",
  "property_address": "House 42, Road 7, Mirpur 10",
  "month": "November 2026",
  "total_paid_bdt": "31030.00",
  "paid_date": "2026-11-05",
  "is_official": true
}
```

---

### 9.5 Send SMS/Push Rent Reminder
* **Route:** `POST /api/v1/ledger/bills/<uuid:id>/send-reminder/`
* **Permission:** Landlord
* **Response (200 OK):**
```json
{
  "success": true,
  "message": "Rent reminder sent to tenant."
}
```

---

## Module 10: In-App Chat & Masked Calling

Base URI: `/api/v1/chat/`

### 10.1 Chat Rooms (List & Create)
* **Route:** `GET /api/v1/chat/rooms/` | `POST /api/v1/chat/rooms/`
* **Permission:** Bearer Token
* **POST Request Body:**
```json
{
  "property_id": "84a4a584-6fb0-4e36-b6b6-8bb09825b741",
  "recipient_id": "5f9e17b8-b4b7-4b77-8c3b-d5a23f4625b1"
}
```
* **Response (201 Created):**
```json
{
  "id": "room-uuid",
  "property": "84a4a584-6fb0-4e36-b6b6-8bb09825b741",
  "created_at": "2026-10-21T18:00:00Z"
}
```

---

### 10.2 Chat Messages (List & Send)
* **Route:** `GET /api/v1/chat/rooms/<uuid:id>/messages/` | `POST /api/v1/chat/rooms/<uuid:id>/messages/`
* **Permission:** Bearer Token (Room Member)
* **POST Request Body:**
```json
{
  "message": "Hello, is the flat still available for viewing this Friday?"
}
```
* **Response (201 Created):**
```json
{
  "id": "msg-uuid",
  "sender_id": "e0b4a72d-8302-4ef8-a55b-f73967dcb638",
  "message": "Hello, is the flat still available for viewing this Friday?",
  "created_at": "2026-10-21T18:05:00Z"
}
```

---

### 10.3 Masked VoIP Call Token (Agora RTC)
* **Route:** `POST /api/v1/chat/rooms/<uuid:id>/call-token/`
* **Permission:** Bearer Token (Room Member)
* **Response (200 OK):**
```json
{
  "session_id": "call-session-uuid",
  "agora_rtc_token": "006rentbd_app_mock_token_8892...",
  "channel_name": "rentbd-call-room-uuid",
  "caller_name": "Rahim Ahmed",
  "receiver_masked_phone": "+880 18•• ••••44",
  "expires_in_seconds": 3600
}
```

---

### 10.4 Update Masked Call Session
* **Route:** `PATCH /api/v1/chat/calls/<uuid:id>/`
* **Permission:** Bearer Token
* **Request Body:**
```json
{
  "status": "ENDED",
  "duration_seconds": 185
}
```
* **Response (200 OK):**
```json
{
  "session_id": "call-session-uuid",
  "status": "ENDED",
  "duration_seconds": 185
}
```

---

## Module 11: Super Admin & Operations Management

Base URI: `/api/v1/admin/`  
**Permission:** Super Admin or Staff (`IsSuperAdminOrStaff`)

### 11.1 Dashboard Overview & Analytics Aggregates
* **Route:** `GET /api/v1/admin/overview-stats/`
* **Permission:** SuperAdmin / Staff
* **Response (200 OK):**
```json
{
  "total_users": 18450,
  "users_growth_pct": 14.8,
  "active_listings": 3280,
  "listings_growth_pct": 22.4,
  "pending_nid_count": 38,
  "pending_spam_count": 14,
  "total_revenue_bdt": "4825000.00",
  "revenue_growth_pct": 18.2,
  "rent_agreements_generated": 1420,
  "fair_rent_breakdown": {
    "fair_price": 2180,
    "great_deal": 760,
    "overpriced": 340
  },
  "category_breakdown": {
    "family": 1940,
    "bachelor": 980,
    "sublet": 360
  },
  "monthly_revenue_history": [
    {"month": "May 2026", "revenue": 3100000, "listings": 2100},
    {"month": "Oct 2026", "revenue": 4825000, "listings": 3280}
  ]
}
```

---

### 11.2 Landlord NID Verification Queue
* **Route:** `GET /api/v1/admin/nid-verifications/`
* **Permission:** SuperAdmin / Staff
* **Query Parameters:** `status` (`pending`, `approved`, `rejected`)
* **Response (200 OK):** Array of verification requests with submitted NID photo, biometrics, and landlord details.

---

### 11.3 Approve Landlord NID Verification
* **Route:** `POST /api/v1/admin/nid-verifications/<str:id>/approve/`
* **Permission:** SuperAdmin / Staff
* **Request Body:**
```json
{
  "notes": "Verified via biometric face match and utility bill cross-check."
}
```
* **Response (200 OK):**
```json
{
  "id": "nid-req-uuid",
  "status": "approved",
  "reviewed_by": "Super Admin (Nafis)",
  "reviewed_at": "2026-10-21T18:10:00Z"
}
```

---

### 11.4 Reject Landlord NID Verification / Flag Broker
* **Route:** `POST /api/v1/admin/nid-verifications/<str:id>/reject/`
* **Permission:** SuperAdmin / Staff
* **Request Body:**
```json
{
  "reason": "Utility bill name mismatch; suspected sub-broker."
}
```
* **Response (200 OK):**
```json
{
  "id": "nid-req-uuid",
  "status": "rejected",
  "rejection_reason": "Utility bill name mismatch; suspected sub-broker."
}
```

---

### 11.5 Geo-Photo Verification Queue
* **Route:** `GET /api/v1/admin/geo-photos/`
* **Permission:** SuperAdmin / Staff
* **Response (200 OK):** List of property photos with extracted GPS coordinates vs property coordinates.

---

### 11.6 Verify Geo-Photo Coordinates
* **Route:** `POST /api/v1/admin/geo-photos/<str:id>/verify/`
* **Permission:** SuperAdmin / Staff
* **Request Body:**
```json
{
  "approved": true
}
```
* **Response (200 OK):**
```json
{
  "id": "geo-photo-uuid",
  "status": "approved"
}
```

---

### 11.7 Admin Property Moderation List
* **Route:** `GET /api/v1/admin/properties/`
* **Permission:** SuperAdmin / Staff
* **Query Parameters:** `status` (`pending`, `active`, `rejected`, `rented`), `category` (`family`, `bachelor`, `sublet`)
* **Response (200 OK):** List of all properties with landlord details and moderation flags.

---

### 11.8 Update Property Moderation Status
* **Route:** `PATCH /api/v1/admin/properties/<str:id>/status/`
* **Permission:** SuperAdmin / Staff
* **Request Body:**
```json
{
  "status": "active"
}
```
* **Response (200 OK):** Updated property object.

---

### 11.9 AI Spam & Duplicate Detector Queue
* **Route:** `GET /api/v1/admin/ai-spam-queue/`
* **Permission:** SuperAdmin / Staff
* **Response (200 OK):** List of flagged duplicate or broker-spammed listings with similarity scores and original property links.

---

### 11.10 Resolve AI Spam Report
* **Route:** `POST /api/v1/admin/ai-spam-queue/<str:id>/resolve/`
* **Permission:** SuperAdmin / Staff
* **Request Body:**
```json
{
  "action": "listing_banned"
}
```
*`action` choices: `listing_banned`, `landlord_blocked`, `false_positive`*
* **Response (200 OK):**
```json
{
  "id": "spam-report-uuid",
  "status": "listing_banned"
}
```

---

### 11.11 Admin Demand vs Supply Heatmap Telemetry
* **Route:** `GET /api/v1/admin/analytics/demand-supply-heatmap/`
* **Permission:** SuperAdmin / Staff
* **Response (200 OK):** High-precision geospatial market density points for Mirpur, Dhanmondi, Gulshan, Uttara, Bashundhara, etc.

---

### 11.12 Admin User Directory & Search
* **Route:** `GET /api/v1/admin/users/`
* **Permission:** SuperAdmin / Staff
* **Query Parameters:** `role` (`tenant`, `landlord`, `admin`), `search` (phone, name, email)
* **Response (200 OK):** User directory list.

---

### 11.13 Toggle User Ban & Flag Broker
* **Route:** `POST /api/v1/admin/users/<str:id>/ban/`
* **Permission:** SuperAdmin / Staff
* **Request Body:** `{}`
* **Response (200 OK):**
```json
{
  "id": "user-uuid",
  "is_flagged_broker": true
}
```

---

### 11.14 Admin Digital Rent & Monetization Revenue Ledger
* **Route:** `GET /api/v1/admin/finance/ledger/`
* **Permission:** SuperAdmin / Staff
* **Response (200 OK):** Complete transaction records of rent bills, monetization boosts, and partner commissions.

---

## Complete Master API Audit Matrix

| # | HTTP Method | Endpoint URI | View Class | Module | Auth Requirement |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `POST` | `/api/v1/auth/otp/request/` | `OTPRequestView` | Accounts | Public |
| 2 | `POST` | `/api/v1/auth/otp/verify/` | `OTPVerifyView` | Accounts | Public |
| 3 | `POST` | `/api/v1/auth/register/` | `RegisterView` | Accounts | Public |
| 4 | `POST` | `/api/v1/auth/login/` | `PasswordLoginView` | Accounts | Public |
| 5 | `POST` | `/api/v1/auth/token/refresh/` | `TokenRefreshView` | Accounts | Public |
| 6 | `POST` | `/api/v1/auth/role/switch/` | `RoleSwitchView` | Accounts | Bearer Token |
| 7 | `POST` | `/api/v1/auth/change-password/` | `ChangePasswordView` | Accounts | Bearer Token |
| 8 | `POST` | `/api/v1/auth/logout/` | `LogoutView` | Accounts | Bearer Token |
| 9 | `GET`, `PATCH` | `/api/v1/auth/profile/` | `UserProfileView` | Accounts | Bearer Token |
| 10 | `POST` | `/api/v1/auth/nid-verify/` | `NIDVerifyView` | Accounts | Landlord Bearer |
| 11 | `GET`, `POST` | `/api/v1/properties/` | `PropertyListCreateView` | Properties | Public (GET) / Landlord (POST) |
| 12 | `GET`, `PATCH`, `DELETE` | `/api/v1/properties/<uuid:pk>/` | `PropertyDetailView` | Properties | Public (GET) / Owner Landlord |
| 13 | `POST` | `/api/v1/properties/<uuid:pk>/toggle-vault/` | `PropertyVaultToggleView` | Properties | Owner Landlord |
| 14 | `POST` | `/api/v1/properties/<uuid:pk>/save/` | `PropertySaveToggleView` | Properties | Bearer Token |
| 15 | `GET` | `/api/v1/properties/saved/` | `SavedPropertiesListView` | Properties | Bearer Token |
| 16 | `POST` | `/api/v1/properties/<uuid:pk>/photos/` | `PropertyPhotoUploadView` | Properties | Owner Landlord |
| 17 | `POST` | `/api/v1/properties/<uuid:pk>/confirm-availability/` | `ListingAvailabilityConfirmView` | Properties | Owner Landlord |
| 18 | `POST` | `/api/v1/properties/<uuid:pk>/boost/` | `MonetizationBoostView` | Properties | Owner Landlord |
| 19 | `GET`, `POST` | `/api/v1/properties/saved-searches/` | `SavedSearchListCreateView` | Properties | Bearer Token |
| 20 | `GET` | `/api/v1/properties/saved-searches/alerts/` | `SavedSearchAlertListView` | Properties | Bearer Token |
| 21 | `PATCH` | `/api/v1/properties/saved-searches/alerts/<uuid:pk>/read/` | `SavedSearchAlertMarkReadView` | Properties | Bearer Token |
| 22 | `GET` | `/api/v1/properties/ai_search/` | `AISearchView` | Properties AI | Public |
| 23 | `POST` | `/api/v1/properties/draw-search/` | `DrawOnMapSearchView` | Properties GIS | Public |
| 24 | `POST` | `/api/v1/properties/compare/` | `PropertyCompareView` | Properties | Public |
| 25 | `POST` | `/api/v1/properties/calculate-move-in/` | `MoveInCostCalculatorView` | Properties | Public |
| 26 | `POST` | `/api/v1/properties/<uuid:pk>/move-in-cost/` | `MoveInCostCalculatorView` | Properties | Public |
| 27 | `GET` | `/api/v1/properties/<uuid:pk>/fair-rent-meter/` | `AIFairRentMeterView` | Properties AI | Public |
| 28 | `POST` | `/api/v1/properties/ai/classify-photo/` | `AIPhotoClassifierView` | Properties AI | Public |
| 29 | `POST` | `/api/v1/properties/ai-generate-description/` | `AIListingWriterView` | Properties AI | Bearer Token |
| 30 | `POST` | `/api/v1/properties/ai/generate-agreement/` | `AIRentAgreementGeneratorView` | Properties AI | Bearer Token |
| 31 | `POST` | `/api/v1/properties/commute-calculator/` | `CommuteCalculatorView` | Properties GIS | Public |
| 32 | `GET` | `/api/v1/properties/<uuid:pk>/nearby-essentials/` | `NearbyEssentialsView` | Properties GIS | Public |
| 33 | `GET` | `/api/v1/properties/<uuid:pk>/street-view/` | `StreetViewPreviewView` | Properties GIS | Public |
| 34 | `GET` | `/api/v1/properties/services/partners/` | `AffiliatePartnersView` | Services | Public |
| 35 | `POST` | `/api/v1/properties/services/book/` | `BookPartnerServiceView` | Services | Bearer Token |
| 36 | `POST` | `/api/v1/properties/admin/detect-spam/` | `AdminSpamDetectorView` | Admin AI | Public / Staff |
| 37 | `GET` | `/api/v1/properties/analytics/demand-supply-heatmap/` | `DemandSupplyHeatmapView` | Analytics | Public |
| 38 | `POST` | `/api/v1/inquiries/` | `InquiryCreateView` | Inquiries | Tenant Bearer |
| 39 | `GET` | `/api/v1/inquiries/landlord-inbox/` | `LandlordScreeningInboxView` | Inquiries | Landlord Bearer |
| 40 | `PATCH` | `/api/v1/inquiries/<uuid:pk>/status/` | `InquiryStatusUpdateView` | Inquiries | Landlord Bearer |
| 41 | `GET`, `POST` | `/api/v1/inquiries/visits/` | `VisitBookingListCreateView` | Inquiries | Bearer Token |
| 42 | `PATCH` | `/api/v1/inquiries/visits/<uuid:pk>/status/` | `VisitBookingStatusUpdateView` | Inquiries | Bearer Token |
| 43 | `GET` | `/api/v1/insights/area/` | `AreaInsightsView` | Insights | Public |
| 44 | `POST` | `/api/v1/insights/submit/` | `AreaInsightSubmitView` | Insights | Bearer Token |
| 45 | `GET`, `POST` | `/api/v1/ledger/tenancies/` | `TenancyContractListCreateView` | Ledger | Bearer Token |
| 46 | `GET`, `POST` | `/api/v1/ledger/bills/` | `RentBillListCreateView` | Ledger | Bearer (GET) / Landlord (POST) |
| 47 | `POST` | `/api/v1/ledger/bills/<uuid:pk>/mark-paid/` | `MarkBillPaidView` | Ledger | Landlord Bearer |
| 48 | `GET` | `/api/v1/ledger/bills/<uuid:pk>/receipt/` | `RentReceiptDetailView` | Ledger | Bearer Token |
| 49 | `POST` | `/api/v1/ledger/bills/<uuid:pk>/send-reminder/` | `SendBillReminderView` | Ledger | Landlord Bearer |
| 50 | `GET`, `POST` | `/api/v1/chat/rooms/` | `ChatRoomListCreateView` | Chat | Bearer Token |
| 51 | `GET`, `POST` | `/api/v1/chat/rooms/<uuid:pk>/messages/` | `ChatMessageListCreateView` | Chat | Room Participant Bearer |
| 52 | `POST` | `/api/v1/chat/rooms/<uuid:pk>/call-token/` | `MaskedCallTokenView` | Chat VoIP | Room Participant Bearer |
| 53 | `PATCH` | `/api/v1/chat/calls/<uuid:pk>/` | `MaskedCallSessionUpdateView` | Chat VoIP | Call Participant Bearer |
| 54 | `GET` | `/api/v1/admin/overview-stats/` | `AdminOverviewStatsView` | Admin | SuperAdmin / Staff |
| 55 | `GET` | `/api/v1/admin/nid-verifications/` | `AdminNIDVerificationListView` | Admin | SuperAdmin / Staff |
| 56 | `POST` | `/api/v1/admin/nid-verifications/<str:pk>/approve/` | `AdminNIDApproveView` | Admin | SuperAdmin / Staff |
| 57 | `POST` | `/api/v1/admin/nid-verifications/<str:pk>/reject/` | `AdminNIDRejectView` | Admin | SuperAdmin / Staff |
| 58 | `GET` | `/api/v1/admin/geo-photos/` | `AdminGeoPhotosListView` | Admin | SuperAdmin / Staff |
| 59 | `POST` | `/api/v1/admin/geo-photos/<str:pk>/verify/` | `AdminGeoPhotoVerifyView` | Admin | SuperAdmin / Staff |
| 60 | `GET` | `/api/v1/admin/properties/` | `AdminPropertyListView` | Admin | SuperAdmin / Staff |
| 61 | `PATCH` | `/api/v1/admin/properties/<str:pk>/status/` | `AdminPropertyStatusUpdateView` | Admin | SuperAdmin / Staff |
| 62 | `GET` | `/api/v1/admin/ai-spam-queue/` | `AdminSpamQueueListView` | Admin | SuperAdmin / Staff |
| 63 | `POST` | `/api/v1/admin/ai-spam-queue/<str:pk>/resolve/` | `AdminSpamQueueResolveView` | Admin | SuperAdmin / Staff |
| 64 | `GET` | `/api/v1/admin/analytics/demand-supply-heatmap/` | `AdminDemandSupplyHeatmapView` | Admin | SuperAdmin / Staff |
| 65 | `GET` | `/api/v1/admin/users/` | `AdminUserListView` | Admin | SuperAdmin / Staff |
| 66 | `POST` | `/api/v1/admin/users/<str:pk>/ban/` | `AdminUserBanToggleView` | Admin | SuperAdmin / Staff |
| 67 | `GET` | `/api/v1/admin/finance/ledger/` | `AdminFinanceLedgerView` | Admin | SuperAdmin / Staff |
