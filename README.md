# RentBD Complete REST API Documentation

Comprehensive API Reference for RentBD backend (Django REST Framework + MySQL/MariaDB + PostGIS). Covers all **67 endpoints** implemented across all 7 applications for Android, iOS (Flutter), and Web.

> 📖 **Full Endpoint Reference Manual:** See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for detailed JSON payloads, parameters, and sample responses for all endpoints.

---

## 📑 Table of Contents
1. [Base URLs & Environment Setup](#-base-urls--environment-setup)
2. [Interactive API Explorers (Swagger & Redoc)](#-interactive-api-explorers-swagger--redoc)
3. [Authentication & Bearer Token Guide](#-authentication--bearer-token-guide)
4. [Standard HTTP Status Codes & Envelopes](#-standard-http-status-codes--envelopes)
5. [Module 1: Authentication & User Accounts (`/api/v1/auth/`)](#1-authentication--user-accounts)
6. [Module 2: Property Listings & Operations (`/api/v1/properties/`)](#2-property-listings--operations)
7. [Module 3: AI & Location Intelligence (`/api/v1/properties/`)](#3-ai--location-intelligence)
8. [Module 4: Affiliate Services, Analytics & Admin (`/api/v1/properties/`)](#4-affiliate-services-analytics--admin)
9. [Module 5: Inquiries & Visit Bookings (`/api/v1/inquiries/`)](#5-inquiries--visit-bookings)
10. [Module 6: Crowdsourced Area Insights (`/api/v1/insights/`)](#6-crowdsourced-area-insights)
11. [Module 7: Digital Rent & Utility Ledger (`/api/v1/ledger/`)](#7-digital-rent--utility-ledger)
12. [Module 8: In-App Chat & Masked Calling (`/api/v1/chat/`)](#8-in-app-chat--masked-calling)
13. [Module 9: Super Admin & Operations Management (`/api/v1/admin/`)](#9-super-admin--operations-management)
14. [Complete 67-Endpoint Master Audit Matrix](#-complete-67-endpoint-master-audit-matrix)

---

## 🌐 Base URLs & Environment Setup

| Client Environment | Base URL | Description |
| :--- | :--- | :--- |
| **Android Emulator** | `http://10.0.2.2:8000/api/v1` | Points to host loopback adapter |
| **iOS Simulator / macOS Desktop** | `http://127.0.0.1:8000/api/v1` | Local loopback |
| **Physical Phone (LAN Wi-Fi)** | `http://<YOUR_LOCAL_IP>:8000/api/v1` | Connect phone & dev PC to same Wi-Fi |
| **Production Server** | `https://api.rentbd.com/api/v1` | SSL/TLS secured production gateway |

---

## 📚 Interactive API Explorers (Swagger & Redoc)

When the development server is running (`python manage.py runserver 0.0.0.0:8000`):
- **Interactive Swagger UI:** [http://127.0.0.1:8000/api/docs/](http://127.0.0.1:8000/api/docs/)
- **Redoc Visual Schema:** [http://127.0.0.1:8000/api/redoc/](http://127.0.0.1:8000/api/redoc/)
- **OpenAPI 3.0 Schema (YAML):** [http://127.0.0.1:8000/api/schema/](http://127.0.0.1:8000/api/schema/)

---

## 🔐 Authentication & Bearer Token Guide

All protected endpoints require an `Authorization` header containing a valid JWT token:

```http
Authorization: Bearer <access_token>
```

### JWT Lifespans
- **Access Token:** 60 minutes
- **Refresh Token:** 7 days

### Role Permissions
- `tenant`: Browse properties, submit inquiries, book visits, calculate move-in costs, save searches, view rent bills & receipts.
- `landlord`: Publish flats, manage vault, view tenant KYC screening inboxes, issue rent bills, mark bills paid, and send reminders.
- `dual`: Can act as both Tenant and Landlord. Toggle active mode instantly via `/api/v1/auth/role/switch/`.

---

## 🚦 Standard HTTP Status Codes & Envelopes

| Code | Meaning | Typical Usage |
| :--- | :--- | :--- |
| `200 OK` | Success | Reading data, successful toggle, status update |
| `201 Created` | Resource Created | Listing published, booking created, bill issued |
| `204 No Content`| Successfully Deleted | Property or image deleted |
| `400 Bad Request`| Validation Error | Missing fields, invalid Bangladeshi phone format |
| `401 Unauthorized`| Authentication Required| Missing, invalid, or expired Bearer token |
| `403 Forbidden` | Access Denied | Tenant accessing landlord inbox or modifying someone else's bill |
| `404 Not Found` | Not Found | Requested property, room, or bill ID does not exist |

---

# 1. Authentication & User Accounts

### 1.1 Request OTP (Bangladeshi Mobile)
- **Method:** `POST`
- **Endpoint:** `/api/v1/auth/otp/request/`
- **Auth:** Public (`AllowAny`)
- **Headers:** `Content-Type: application/json`

#### Request Body
```json
{
  "phone_number": "+8801712345678"
}
```
#### Response (200 OK)
```json
{
  "success": true,
  "message": "OTP sent successfully to +8801712345678",
  "expires_in_seconds": 300,
  "dev_otp": "123456"
}
```

---

### 1.2 Verify OTP & Login
- **Method:** `POST`
- **Endpoint:** `/api/v1/auth/otp/verify/`
- **Auth:** Public (`AllowAny`)
- **Headers:** `Content-Type: application/json`

#### Request Body
```json
{
  "phone_number": "+8801712345678",
  "otp_code": "123456",
  "role": "tenant"
}
```
#### Response (200 OK)
```json
{
  "success": true,
  "message": "OTP verified successfully.",
  "tokens": {
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI...",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI..."
  },
  "user": {
    "id": "c1f73620-8bfa-48b2-b43e-f1cf6c2323a1",
    "phone_number": "+8801712345678",
    "full_name": "Rahim Ahmed",
    "role": "tenant",
    "is_phone_verified": true,
    "tenant_profile": {
      "occupation": "Software Engineer",
      "workplace": "Brain Station 23",
      "family_members_count": 3
    }
  }
}
```

---

### 1.3 Register with Password
- **Method:** `POST`
- **Endpoint:** `/api/v1/auth/register/`
- **Auth:** Public (`AllowAny`)

#### Request Body
```json
{
  "phone_number": "+8801812345678",
  "full_name": "Kamal Hossain",
  "password": "SecurePassword123!",
  "role": "landlord"
}
```
#### Response (201 Created)
Returns JWT tokens and user profile object.

---

### 1.4 Login with Password
- **Method:** `POST`
- **Endpoint:** `/api/v1/auth/login/`
- **Auth:** Public (`AllowAny`)

#### Request Body
```json
{
  "phone_number": "+8801812345678",
  "password": "SecurePassword123!",
  "role": "landlord"
}
```
#### Response (200 OK)
Returns JWT tokens and user profile object.

---

### 1.5 Refresh JWT Session Token
- **Method:** `POST`
- **Endpoint:** `/api/v1/auth/token/refresh/`
- **Auth:** Public (`AllowAny`)

#### Request Body
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```
#### Response (200 OK)
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...new_access_token...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...new_rotated_refresh..."
}
```

---

### 1.6 Switch Role (Tenant / Landlord / Dual)
- **Method:** `POST`
- **Endpoint:** `/api/v1/auth/role/switch/`
- **Auth:** Bearer Token (`IsAuthenticated`)

#### Request Body
```json
{
  "role": "landlord"
}
```
#### Response (200 OK)
```json
{
  "success": true,
  "message": "Role successfully updated to landlord.",
  "role": "landlord"
}
```

---

### 1.7 Change Account Password
- **Method:** `POST`
- **Endpoint:** `/api/v1/auth/change-password/`
- **Auth:** Bearer Token (`IsAuthenticated`)

#### Request Body
```json
{
  "current_password": "OldPassword123!",
  "new_password": "NewSecurePassword456!"
}
```
#### Response (200 OK)
```json
{
  "success": true,
  "message": "Password updated successfully."
}
```
#### Error (400 Bad Request)
```json
{
  "detail": "Current password does not match."
}
```

---

### 1.8 User Profile (Fetch & Update)
- **Method:** `GET` / `PATCH`
- **Endpoint:** `/api/v1/auth/profile/`
- **Auth:** Bearer Token (`IsAuthenticated`)

#### PATCH Request Body
```json
{
  "full_name": "Rahim Ahmed Chowdhury",
  "email": "rahim.chowdhury@example.com",
  "tenant_profile": {
    "occupation": "Lead Engineer",
    "workplace": "Brain Station 23",
    "family_members_count": 3
  }
}
```
#### Response (200 OK)
Returns complete updated user profile and nested KYC details.

---

### 1.9 NID Identity Verification (KYC / Anti-Broker)
- **Method:** `POST`
- **Endpoint:** `/api/v1/auth/nid-verify/`
- **Auth:** Bearer Token (`IsAuthenticated`)
- **Headers:** `Content-Type: multipart/form-data`

#### Form Parameters
- `nid_number` (string): 10 or 17 digit NID number (e.g. `"19922692019000123"`)
- `nid_front_image` (file): Front image of National ID card
- `nid_back_image` (file): Back image of National ID card
- `selfie_image` (file): Front-facing live selfie

#### Response (200 OK)
```json
{
  "success": true,
  "message": "NID verification submitted successfully. Status: verified.",
  "nid_status": "verified",
  "nid_number": "19922692019000123"
}
```

---

### 1.10 Logout
- **Method:** `POST`
- **Endpoint:** `/api/v1/auth/logout/`
- **Auth:** Bearer Token (`IsAuthenticated`)

#### Request Body
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI..."
}
```
#### Response (200 OK)
```json
{
  "detail": "Successfully logged out."
}
```

---

# 2. Property Listings & Operations

### 2.1 List & Filter Properties
- **Method:** `GET`
- **Endpoint:** `/api/v1/properties/`
- **Auth:** Optional / Bearer Token
- **Landlord Scope:** When called by an authenticated Landlord (`role == 'landlord'`), the endpoint automatically returns **only the properties created by that landlord**. (Pass `?all=true` to view public marketplace listings).

#### Query Parameters
- `vault` (boolean): If `true`, returns landlord's off-market/rented listings.
- `my_properties` (boolean): Explicitly filters to own listings regardless of role.
- `all` (boolean): Bypasses landlord auto-filter to view all public listings.
- `search` (string): Text query across title, description, and address
- `area` (string): `mirpur_10`, `uttara`, `dhanmondi`, `gulshan_1`, `bashundhara_ra`
- `property_type` (string): `family`, `bachelor`, `sublet`, `hostel`, `office`, `shop`
- `tenant_category` (string): `family`, `bachelor_male`, `bachelor_female`, `any`
- `min_rent` / `max_rent` (integer): Rent range in BDT
- `bedrooms` / `bathrooms` (integer): Exact room counts
- `has_gas`, `has_generator`, `has_lift`, `has_parking` (boolean): Utility filters
- `waterlogging_risk` (string): `none`, `low`, `moderate`, `high`
- `water_quality` (string): `drinkable_filtered`, `iron_free`, `needs_boiling`, `poor`

#### Response (200 OK)
```json
{
  "count": 28,
  "next": "http://127.0.0.1:8000/api/v1/properties/?page=2",
  "previous": null,
  "results": [
    {
      "id": "4b7e8d02-15d9-4cf5-992a-fa13de5518b2",
      "title": "Modern 3-BHK Flat in Bashundhara R/A Block D",
      "property_type": "family",
      "tenant_category": "family",
      "rent": 35000,
      "service_charge": 5000,
      "security_deposit": 70000,
      "bedrooms": 3,
      "bathrooms": 3,
      "size_sqft": 1650,
      "area": "bashundhara_ra",
      "address": "House 12, Road 4, Block D, Bashundhara R/A, Dhaka",
      "latitude": 23.8151,
      "longitude": 90.4255,
      "has_gas": true,
      "has_generator": true,
      "has_lift": true,
      "is_vault": false,
      "is_featured": true,
      "is_saved": false,
      "landlord": {
        "id": "a90f3411-9fa2-47e1-884c-3e61c304859a",
        "full_name": "Kamal Hossain",
        "is_nid_verified": true
      }
    }
  ]
}
```

---

### 2.2 Create Property Listing (60-Second Quick Post)
- **Method:** `POST`
- **Endpoint:** `/api/v1/properties/`
- **Auth:** Bearer Token (`IsAuthenticated` - Landlord)

#### Request Body
```json
{
  "title": "Sunlit 2-BHK Flat near Mirpur 10 Metro",
  "description": "3 mins walk from Metro Pillar 240. Titas pipeline gas.",
  "property_type": "family",
  "tenant_category": "family",
  "rent": 22000,
  "service_charge": 3000,
  "security_deposit": 44000,
  "bedrooms": 2,
  "bathrooms": 2,
  "size_sqft": 1100,
  "area": "mirpur_10",
  "address": "House 45, Road 2, Block C, Mirpur 10, Dhaka",
  "latitude": 23.8069,
  "longitude": 90.3687,
  "has_gas": true,
  "has_generator": true,
  "has_lift": true
}
```
#### Response (201 Created)
Returns complete created property object with assigned UUID (`status: "pending_approval"`, `is_available: false`).

> [!NOTE]
> **Admin Verification Workflow:** When a regular landlord posts a listing, it is created with `status: "pending_approval"` and `is_available: false`. Landlords can immediately view their own pending listings under `GET /api/v1/properties/`, but public marketplace users and tenants cannot view the property until an admin approves it (`status = "active"`). Listings posted by SuperAdmins or Staff are immediately activated.

---

### 2.3 Property Details, Update & Delete
- **Endpoints:**
  - `GET /api/v1/properties/<uuid:pk>/` (Public)
  - `PATCH /api/v1/properties/<uuid:pk>/` (Owner Landlord only)
  - `DELETE /api/v1/properties/<uuid:pk>/` (Owner Landlord only)

---

### 2.4 One-Tap Re-Listing (Property Vault)
Hides a rented flat into the landlord's private Vault. 11 months later, re-activate with 1 tap.
- **Method:** `POST`
- **Endpoint:** `/api/v1/properties/<uuid:pk>/toggle-vault/`
- **Auth:** Bearer Token (Owner Landlord)

#### Response (200 OK)
```json
{
  "success": true,
  "is_vault": true,
  "status": "rented",
  "message": "Property moved to Vault (hidden from public searches)."
}
```

---

### 2.5 Toggle Wishlist Bookmark
- **Method:** `POST`
- **Endpoint:** `/api/v1/properties/<uuid:pk>/save/`
- **Auth:** Bearer Token (`IsAuthenticated`)

#### Response (200 OK)
```json
{
  "success": true,
  "is_saved": true,
  "message": "Property saved to your wishlist."
}
```

---

### 2.6 Saved Properties Wishlist
- **Method:** `GET`
- **Endpoint:** `/api/v1/properties/saved/`
- **Auth:** Bearer Token (`IsAuthenticated`)

#### Response (200 OK)
Returns array of properties bookmarked by the current user.

---

### 2.7 Upload Photos with Server-Verified GPS EXIF
- **Method:** `POST`
- **Endpoint:** `/api/v1/properties/<uuid:pk>/photos/`
- **Auth:** Bearer Token (Owner Landlord)
- **Headers:** `Content-Type: multipart/form-data`

#### Form Parameters
- `image` (file): Flat photo
- `category` (string): `living`, `bedroom`, `kitchen`, `washroom`, `balcony`, `exterior`
- `is_primary` (boolean): `true` / `false`
- `latitude` (float, optional): Live camera GPS latitude
- `longitude` (float, optional): Live camera GPS longitude

#### Response (201 Created)
```json
{
  "id": "7fa12...-uuid",
  "image": "http://127.0.0.1:8000/media/properties/bedroom_1.jpg",
  "category": "bedroom",
  "is_primary": false,
  "is_verified_geotag": true
}
```

---

### 2.8 15-Day Availability Re-Verification
- **Method:** `POST`
- **Endpoint:** `/api/v1/properties/<uuid:pk>/confirm-availability/`
- **Auth:** Bearer Token (Owner Landlord)

#### Response (200 OK)
```json
{
  "success": true,
  "last_confirmed_available": "2026-10-21T00:00:00Z",
  "message": "Listing availability re-verified. Timer reset for 15 days."
}
```

---

### 2.9 Listing Featured Boost (bKash / Nagad Monetization)
- **Method:** `POST`
- **Endpoint:** `/api/v1/properties/<uuid:pk>/boost/`
- **Auth:** Bearer Token (Owner Landlord)

#### Request Body
```json
{
  "boost_duration_days": 7,
  "payment_method": "BKASH"
}
```
#### Response (200 OK)
```json
{
  "success": true,
  "property_id": "4b7e8d02-15d9-4cf5-992a-fa13de5518b2",
  "is_featured": true,
  "boost_duration_days": 7,
  "fee_bdt": 1050.0,
  "payment_status": "PAID_SUCCESSFUL",
  "payment_method": "BKASH",
  "message": "Listing successfully boosted to top of search for 7 days!"
}
```

---

### 2.10 Saved Searches & Alerts
- **Method:** `GET` / `POST`
- **Endpoint:** `/api/v1/properties/saved-searches/`
- **Auth:** Bearer Token (`IsAuthenticated`)

#### POST Request Body
```json
{
  "title": "Mirpur 10 Bachelor under 15k",
  "area_neighborhood": "Mirpur 10",
  "max_rent": 15000,
  "property_type": "BACHELOR",
  "tenant_category": "BACHELOR_MALE",
  "min_bedrooms": 2
}
```
#### Response (201 Created)
Returns saved search filter record with alert notification enabled.

---

### 2.11 Saved Search Notifications
- **Method:** `GET`
- **Endpoint:** `/api/v1/properties/saved-searches/alerts/`
- **Auth:** Bearer Token (`IsAuthenticated`)

#### Response (200 OK)
Returns notifications of newly listed properties that matched user's saved searches.

---

### 2.12 Mark Alert as Read
- **Method:** `PATCH`
- **Endpoint:** `/api/v1/properties/saved-searches/alerts/<uuid:pk>/read/`
- **Auth:** Bearer Token (`IsAuthenticated`)

#### Response (200 OK)
```json
{
  "success": true,
  "is_read": true
}
```

---

# 3. AI & Location Intelligence

### 3.1 AI Voice & Natural Language Search (Bangla / Banglish)
- **Method:** `GET`
- **Endpoint:** `/api/v1/properties/ai_search/`
- **Query Parameter:** `?q=mirpur 10 e 2 bed bachelor gas ache 15000 takar moddhe`

#### Response (200 OK)
```json
{
  "query": "mirpur 10 e 2 bed bachelor gas ache 15000 takar moddhe",
  "interpreted_filters": {
    "area": "mirpur_10",
    "bedrooms": 2,
    "max_rent": 15000,
    "tenant_category": "bachelor",
    "has_gas": true
  },
  "count": 3,
  "results": [ ... ]
}
```

---

### 3.2 Draw-on-Map Custom Polygon Search
- **Method:** `POST`
- **Endpoint:** `/api/v1/properties/draw-search/`
- **Headers:** `Content-Type: application/json`

#### Request Body
```json
{
  "polygon": [
    {"latitude": 23.8100, "longitude": 90.4100},
    {"latitude": 23.8250, "longitude": 90.4100},
    {"latitude": 23.8250, "longitude": 90.4350},
    {"latitude": 23.8100, "longitude": 90.4350}
  ]
}
```
#### Response (200 OK)
Returns all properties located inside the user-drawn freehand boundary.

---

### 3.3 Property Side-by-Side Comparison
- **Method:** `POST`
- **Endpoint:** `/api/v1/properties/compare/`

#### Request Body
```json
{
  "property_ids": [
    "4b7e8d02-15d9-4cf5-992a-fa13de5518b2",
    "8c919a11-201a-42c2-ba0e-3fa12e551101"
  ]
}
```
#### Response (200 OK)
Returns structured matrix comparing rent, sqft, gas, lift, generator, and security deposit.

---

### 3.4 Move-In Cash Calculator
- **Method:** `POST`
- **Endpoints:**
  - `/api/v1/properties/calculate-move-in/` (Generic estimator)
  - `/api/v1/properties/<uuid:pk>/move-in-cost/` (Per-property estimator)

#### Request Body
```json
{
  "property_id": "4b7e8d02-15d9-4cf5-992a-fa13de5518b2",
  "truck_type": "MEDIUM_TRUCK",
  "moving_distance_km": 10,
  "needs_labour": true
}
```
#### Response (200 OK)
```json
{
  "currency": "BDT",
  "first_month_rent": 35000.0,
  "security_deposit_advance": 70000.0,
  "service_charge": 5000.0,
  "estimated_utilities": 2500.0,
  "moving_and_labour_estimate": 7600.0,
  "total_upfront_cash_required": 120100.0
}
```

---

### 3.5 AI Fair Rent Meter
- **Method:** `GET`
- **Endpoint:** `/api/v1/properties/<uuid:pk>/fair-rent-meter/`

#### Response (200 OK)
```json
{
  "property_id": "4b7e8d02-15d9-4cf5-992a-fa13de5518b2",
  "current_rent": 35000,
  "area_average_rent": 38500,
  "verdict": "Fair Price",
  "percentage_difference": -9.09,
  "rating_score": 4.5,
  "insight": "This flat is priced 9% below the Bashundhara R/A 3-bedroom average."
}
```

---

### 3.6 AI Photo Classifier & Quality Checker
- **Method:** `POST`
- **Endpoint:** `/api/v1/properties/ai/classify-photo/`
- **Headers:** `Content-Type: multipart/form-data`

#### Form Parameters
- `image` (file): Flat photo file

#### Response (200 OK)
```json
{
  "detected_room_type": "BEDROOM",
  "clarity_rating": "High Resolution (1920x1080)",
  "exposure_assessment": "Balanced Natural Sunlight",
  "needs_enhancement": false,
  "recommended_brightness_boost": 0
}
```

---

### 3.7 AI Listing Description Writer
- **Method:** `POST`
- **Endpoint:** `/api/v1/properties/ai-generate-description/`
- **Auth:** Bearer Token (`IsAuthenticated`)

#### Request Body
```json
{
  "area": "Uttara Sector 11",
  "bedrooms": 3,
  "bathrooms": 3,
  "size_sqft": 1500,
  "key_features": ["South facing", "Lift", "Generator", "Titas Line Gas"]
}
```
#### Response (200 OK)
```json
{
  "generated_title": "Luxurious 3-BHK Apartment with Titas Gas in Uttara Sector 11",
  "generated_description": "Welcome to this sunlit 1500 sqft apartment in Uttara Sector 11..."
}
```

---

### 3.8 AI Legal Rent Agreement (ভাড়া চুক্তিপত্র)
- **Method:** `POST`
- **Endpoint:** `/api/v1/properties/ai/generate-agreement/`
- **Auth:** Bearer Token (`IsAuthenticated`)

#### Request Body
```json
{
  "property_id": "4b7e8d02-15d9-4cf5-992a-fa13de5518b2",
  "landlord_name": "Kamal Hossain",
  "tenant_name": "Rahim Ahmed",
  "monthly_rent": 35000,
  "security_deposit": 70000,
  "start_date": "2026-11-01",
  "contract_duration_months": 12,
  "utilities_clause": "Tenant pays monthly electricity tokens directly."
}
```
#### Response (200 OK)
Returns complete bilingual Markdown legal contract conforming to Bangladesh tenancy laws.

---

### 3.9 Commute & Metro Station Calculator
- **Method:** `POST`
- **Endpoint:** `/api/v1/properties/commute-calculator/`

#### Request Body
```json
{
  "property_id": "4b7e8d02-15d9-4cf5-992a-fa13de5518b2",
  "destination_area": "motijheel",
  "commute_mode": "metro"
}
```
#### Response (200 OK)
```json
{
  "commute_time_minutes": 32,
  "mode": "metro",
  "nearest_station": "Kuril Metro Link",
  "station_distance_meters": 800,
  "traffic_delay_peak_hours_minutes": 10
}
```

---

### 3.10 500m Walkability Essentials Layer
- **Method:** `GET`
- **Endpoint:** `/api/v1/properties/<uuid:pk>/nearby-essentials/`

#### Response (200 OK)
```json
{
  "metro_stations": [{"name": "Mirpur 10 Metro Station", "distance_meters": 320}],
  "bus_stops": [{"name": "Mirpur 10 Golchokkor", "distance_meters": 180}],
  "mosques": [{"name": "Baitul Falah Jame Masjid", "distance_meters": 120}],
  "bazaars": [{"name": "Mirpur 10 Kacha Bazaar", "distance_meters": 450}]
}
```

---

### 3.11 Street View & Alley Width Check
- **Method:** `GET`
- **Endpoint:** `/api/v1/properties/<uuid:pk>/street-view/`

#### Response (200 OK)
```json
{
  "road_width_ft": 25,
  "street_view_available": true,
  "alley_type": "Main Access Road",
  "vehicle_passable": ["Sedan", "SUV", "Moving Truck (3 Ton)"]
}
```

---

# 4. Affiliate Services, Analytics & Admin

### 4.1 Affiliate Service Partners Catalog
- **Method:** `GET`
- **Endpoint:** `/api/v1/properties/services/partners/`
- **Auth:** Public (`AllowAny`)

#### Response (200 OK)
```json
{
  "partners": [
    {
      "id": "partner-mover-01",
      "name": "Dhaka City Packers & Movers Ltd.",
      "service_type": "PACKERS_MOVERS",
      "rating": 4.9,
      "starting_price_bdt": 3500,
      "contact": "+8801700998877"
    },
    {
      "id": "partner-clean-02",
      "name": "ShineBD Professional Home Cleaning",
      "service_type": "HOME_CLEANING",
      "rating": 4.8,
      "starting_price_bdt": 1500,
      "contact": "+8801811223344"
    }
  ]
}
```

---

### 4.2 Book Partner Moving/Cleaning Service
- **Method:** `POST`
- **Endpoint:** `/api/v1/properties/services/book/`
- **Auth:** Bearer Token (`IsAuthenticated`)

#### Request Body
```json
{
  "service_type": "PACKERS_MOVERS",
  "scheduled_date": "2026-11-01",
  "pickup_address": "House 45, Road 2, Mirpur 10, Dhaka",
  "destination_address": "House 12, Road 4, Bashundhara R/A, Dhaka",
  "contact_phone": "+8801712345678"
}
```
#### Response (201 Created)
```json
{
  "success": true,
  "booking_id": "BK-RENTBD-8841",
  "service_type": "PACKERS_MOVERS",
  "scheduled_date": "2026-11-01",
  "status": "CONFIRMED",
  "message": "Partner dispatched. Our moving coordinator will call you within 30 minutes."
}
```

---

### 4.3 AI Spam & Duplicate Detector (Admin / Anti-Broker)
- **Method:** `POST`
- **Endpoint:** `/api/v1/properties/admin/detect-spam/`
- **Auth:** Public / Staff

#### Request Body
```json
{
  "title": "2 bed flat for rent",
  "description": "50% media fee required upon booking. Broker charge applicable.",
  "rent_amount": 2500
}
```
#### Response (200 OK)
```json
{
  "is_flagged_as_spam": true,
  "spam_score": 0.90,
  "checks": {
    "unusually_low_scam_pricing": true,
    "unauthorized_broker_keywords": true
  }
}
```

---

### 4.4 Demand vs. Supply Neighborhood Heatmap
- **Method:** `GET`
- **Endpoint:** `/api/v1/properties/analytics/demand-supply-heatmap/`
- **Auth:** Public (`AllowAny`)

#### Response (200 OK)
```json
{
  "total_areas": 8,
  "heatmap": [
    {
      "area": "Mirpur 10",
      "latitude": 23.8069,
      "longitude": 90.3687,
      "search_demand_index": 88,
      "active_listings_count": 14,
      "pressure_ratio": 6.28,
      "market_state": "High Tenant Demand"
    }
  ]
}
```

---

# 5. Inquiries & Visit Bookings

### 5.1 Submit Tenant Inquiry
- **Method:** `POST`
- **Endpoint:** `/api/v1/inquiries/`
- **Auth:** Bearer Token (Tenant)

#### Request Body
```json
{
  "property_id": "4b7e8d02-15d9-4cf5-992a-fa13de5518b2",
  "message": "Assalamu Alaikum. Is this flat available for family occupancy starting November 1st?"
}
```
#### Response (201 Created)
Returns created inquiry with initial status `PENDING`.

---

### 5.2 Landlord Tenant-Screening Inbox
- **Method:** `GET`
- **Endpoint:** `/api/v1/inquiries/landlord-inbox/`
- **Auth:** Bearer Token (Landlord)

#### Response (200 OK)
Returns array of incoming tenant inquiries with verified credentials (NID verification status, workplace, occupation, family size).

---

### 5.3 Accept / Reject Inquiry
- **Method:** `PATCH`
- **Endpoint:** `/api/v1/inquiries/<uuid:pk>/status/`
- **Auth:** Bearer Token (Owner Landlord)

#### Request Body
```json
{
  "status": "ACCEPTED"
}
```
*Choices: `PENDING`, `ACCEPTED`, `REJECTED`, `EXPIRED`*

#### Response (200 OK)
Returns updated inquiry. Accepting unlocks encrypted chat and masked VoIP calling.

---

### 5.4 List & Schedule Property Visits
- **Method:** `GET` / `POST`
- **Endpoint:** `/api/v1/inquiries/visits/`
- **Auth:** Bearer Token (`IsAuthenticated`)

#### POST Request Body
```json
{
  "property_id": "4b7e8d02-15d9-4cf5-992a-fa13de5518b2",
  "visit_type": "IN_PERSON",
  "scheduled_at": "2026-10-25T16:00:00Z",
  "notes": "Will come with my family to inspect."
}
```
*`visit_type` choices: `IN_PERSON`, `LIVE_VIDEO_TOUR`*

#### Response (201 Created)
Returns visit booking record with status `REQUESTED`.

---

### 5.5 Update Visit Booking Status
- **Method:** `PATCH`
- **Endpoint:** `/api/v1/inquiries/visits/<uuid:pk>/status/`
- **Auth:** Bearer Token (Landlord or Tenant)

#### Request Body
```json
{
  "status": "CONFIRMED",
  "video_call_link": "https://meet.google.com/xyz-abc"
}
```
*`status` choices: `REQUESTED`, `CONFIRMED`, `COMPLETED`, `CANCELLED`*

#### Response (200 OK)
Returns updated visit booking.

---

# 6. Crowdsourced Area Insights

### 6.1 Fetch Neighborhood Insights
- **Method:** `GET`
- **Endpoint:** `/api/v1/insights/area/`
- **Query Parameter:** `?area=mirpur_10`

#### Response (200 OK)
```json
{
  "area": "mirpur_10",
  "waterlogging_summary": "low",
  "gas_pressure_avg": 4.2,
  "water_quality_summary": "drinkable_filtered",
  "safety_rating_avg": 4.5,
  "total_reviews": 38,
  "resident_reviews": [ ... ]
}
```

---

### 6.2 Submit Resident Insight
- **Method:** `POST`
- **Endpoint:** `/api/v1/insights/submit/`
- **Auth:** Bearer Token (`IsAuthenticated`)

#### Request Body
```json
{
  "area_neighborhood": "Mirpur 10",
  "waterlogging_severity": "LOW",
  "gas_pressure_rating": 4,
  "safety_rating": 5,
  "wasa_water_quality": "IRON_FREE",
  "review_text": "Road 14 has zero waterlogging even during heavy monsoon rains."
}
```
#### Response (201 Created)
Returns created review record.

---

# 7. Digital Rent & Utility Ledger

### 7.1 List & Create Tenancy Contracts
- **Method:** `GET` / `POST`
- **Endpoint:** `/api/v1/ledger/tenancies/`
- **Auth:** Bearer Token (Landlord or Tenant)

#### POST Request Body
```json
{
  "property": "4b7e8d02-15d9-4cf5-992a-fa13de5518b2",
  "tenant_phone": "+8801712345678",
  "flat_number": "4B",
  "monthly_rent": 25000,
  "service_charge": 3500,
  "security_deposit": 50000,
  "contract_start_date": "2026-11-01",
  "contract_end_date": "2027-10-31"
}
```
#### Response (201 Created)
Returns created tenancy contract object with contract UUID.

---

### 7.2 List & Issue Rent Bills
- **Method:** `GET` / `POST`
- **Endpoint:** `/api/v1/ledger/bills/`
- **Auth:** Bearer Token (Landlord or Tenant)

#### POST Request Body
```json
{
  "contract": "contract-uuid",
  "billing_month": "November 2026",
  "rent_amount": 25000,
  "electricity_bill": 1800,
  "gas_bill": 1080,
  "water_bill": 500,
  "service_charge": 3500,
  "due_date": "2026-11-10"
}
```
#### Response (201 Created)
```json
{
  "id": "bill-uuid",
  "billing_month": "November 2026",
  "total_amount": 31880,
  "status": "UNPAID",
  "due_date": "2026-11-10"
}
```

---

### 7.3 Mark Bill as Paid (Issue Digital Receipt)
- **Method:** `POST`
- **Endpoint:** `/api/v1/ledger/bills/<uuid:pk>/mark-paid/`
- **Auth:** Bearer Token (Landlord)

#### Request Body
```json
{
  "payment_method": "BKASH",
  "transaction_id": "BK89239102"
}
```
#### Response (200 OK)
```json
{
  "success": true,
  "status": "PAID",
  "paid_at": "2026-10-21T00:00:00Z",
  "receipt_number": "REC-202611-4B92",
  "message": "Bill marked as paid and digital receipt generated."
}
```

---

### 7.4 Fetch Digital Rent Receipt
- **Method:** `GET`
- **Endpoint:** `/api/v1/ledger/bills/<uuid:pk>/receipt/`
- **Auth:** Bearer Token (Contract Landlord or Tenant)

#### Response (200 OK)
```json
{
  "receipt_number": "REC-202611-4B92",
  "property_title": "Modern 3-BHK Flat in Bashundhara R/A Block D",
  "flat_number": "4B",
  "tenant_name": "Rahim Ahmed",
  "landlord_name": "Kamal Hossain",
  "billing_month": "November 2026",
  "total_paid": 31880,
  "payment_method": "bKash",
  "transaction_id": "BK89239102",
  "paid_at": "2026-10-21T00:00:00Z",
  "digital_signature_hash": "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
}
```

---

### 7.5 Send Rent Payment Reminder
- **Method:** `POST`
- **Endpoint:** `/api/v1/ledger/bills/<uuid:pk>/send-reminder/`
- **Auth:** Bearer Token (Landlord)

#### Response (200 OK)
```json
{
  "success": true,
  "bill_id": "bill-uuid",
  "billing_month": "November 2026",
  "total_amount": 31880.0,
  "tenant_name": "Rahim Ahmed",
  "tenant_phone_masked": "+880 17•• ••••78",
  "delivery_channels": ["IN_APP_PUSH", "SMS_GATEWAY"],
  "status": "DELIVERED"
}
```

---

# 8. In-App Chat & Masked Calling

### 8.1 List & Create Chat Rooms
- **Method:** `GET` / `POST`
- **Endpoint:** `/api/v1/chat/rooms/`
- **Auth:** Bearer Token (`IsAuthenticated`)

#### POST Request Body
```json
{
  "property_id": "4b7e8d02-15d9-4cf5-992a-fa13de5518b2",
  "recipient_id": "a90f3411-9fa2-47e1-884c-3e61c304859a"
}
```
#### Response (200 OK / 201 Created)
Returns chat room object with room UUID.

---

### 8.2 Get & Send Chat Messages
- **Method:** `GET` / `POST`
- **Endpoint:** `/api/v1/chat/rooms/<uuid:pk>/messages/`
- **Auth:** Bearer Token (Room Participant)

#### POST Request Body
```json
{
  "message_text": "Hello, is the flat available for viewing tomorrow afternoon?"
}
```
#### Response (201 Created)
```json
{
  "id": "msg-uuid",
  "sender_id": "c1f73620-8bfa-48b2-b43e-f1cf6c2323a1",
  "sender_name": "Rahim Ahmed",
  "message_text": "Hello, is the flat available for viewing tomorrow afternoon?",
  "created_at": "2026-10-21T00:00:00Z"
}
```

---

### 8.3 Initiate Masked VoIP Calling (Agora RTC Token)
- **Method:** `POST`
- **Endpoint:** `/api/v1/chat/rooms/<uuid:pk>/call-token/`
- **Auth:** Bearer Token (Room Participant)

#### Response (200 OK)
```json
{
  "success": true,
  "session_id": "call-session-uuid",
  "channel_name": "rentbd-call-e30f9a",
  "agora_rtc_token": "006rentbd_app_mock_token_8892...",
  "caller_name": "Rahim Ahmed",
  "receiver_name": "Kamal Hossain",
  "receiver_phone_masked": "+880 18•• ••••78",
  "expires_in_seconds": 3600
}
```

---

### 8.4 Update Masked Call Session Status
- **Method:** `PATCH`
- **Endpoint:** `/api/v1/chat/calls/<uuid:pk>/`
- **Auth:** Bearer Token (Caller or Receiver)

#### Request Body
```json
{
  "status": "ENDED",
  "duration_seconds": 185
}
```
*`status` choices: `INITIATED`, `RINGING`, `CONNECTED`, `ENDED`, `MISSED`, `REJECTED`*

#### Response (200 OK)
```json
{
  "success": true,
  "session_id": "call-session-uuid",
  "status": "ENDED",
  "duration_seconds": 185
}
```

---

---

# 9. Super Admin & Operations Management

All administrative endpoints are rooted at `/api/v1/admin/` and require superuser or staff authentication (`IsSuperAdminOrStaff`).

### 9.1 Platform Overview & Complete Analytics Dashboard
- **Method:** `GET`
- **Endpoint:** `/api/v1/admin/analytics/dashboard/` (or `/api/v1/admin/overview-stats/`)
- **Auth:** SuperAdmin / Staff
- **Response (200 OK):** Comprehensive dashboard analytics:
  - **Core KPIs:** `total_users`, `active_listings`, `total_revenue_bdt`, `average_monthly_rent_bdt`, `rent_agreements_generated`
  - **Queue Counters:** `pending_nid_count`, `pending_geo_count`, `pending_spam_count`, `pending_property_count`
  - **Modular Breakdowns:** `users_analytics`, `properties_analytics`, `finance_analytics`
  - **Distributions:** `category_breakdown` (family, bachelor, sublet, hostel, duplex), `fair_rent_breakdown` (fair_price, great_deal, overpriced)
  - **Geospatial Telemetry:** `top_demand_supply_areas` (market pressure and search ratios)
  - **Trends:** `monthly_revenue_history` (multi-month trend with listings and new user growth)
  - **Activity Feed:** `recent_activity` (latest pending NIDs, pending properties, and spam flags)

---

### 9.2 Landlord NID Verification Queue
- **Method:** `GET`
- **Endpoint:** `/api/v1/admin/nid-verifications/`
- **Auth:** SuperAdmin / Staff
- **Query Params:** `status` (`pending`, `approved`, `rejected`)
- **Response (200 OK):** List of verification requests with submitted NID images, biometrics, and landlord details.

---

### 9.3 Approve Landlord NID Verification
- **Method:** `POST`
- **Endpoint:** `/api/v1/admin/nid-verifications/<str:pk>/approve/`
- **Auth:** SuperAdmin / Staff
- **Request Body:**
```json
{
  "notes": "Verified via biometric face match and utility bill cross-check."
}
```
- **Response (200 OK):** Verification approval record.

---

### 9.4 Reject Landlord NID / Flag Broker
- **Method:** `POST`
- **Endpoint:** `/api/v1/admin/nid-verifications/<str:pk>/reject/`
- **Auth:** SuperAdmin / Staff
- **Request Body:**
```json
{
  "reason": "Utility bill name mismatch; suspected sub-broker."
}
```
- **Response (200 OK):** Rejection record with audit trail.

---

### 9.5 Geo-Photo Validation Queue
- **Method:** `GET`
- **Endpoint:** `/api/v1/admin/geo-photos/`
- **Auth:** SuperAdmin / Staff
- **Response (200 OK):** List of photos with extracted EXIF GPS vs property registered location.

---

### 9.6 Verify Geo-Photo Coordinates
- **Method:** `POST`
- **Endpoint:** `/api/v1/admin/geo-photos/<str:pk>/verify/`
- **Auth:** SuperAdmin / Staff
- **Request Body:**
```json
{
  "approved": true
}
```
- **Response (200 OK):** Approval status and updates property `has_geo_tagged_photos`.

---

### 9.7 Property Moderation Queue
- **Method:** `GET`
- **Endpoint:** `/api/v1/admin/properties/`
- **Auth:** SuperAdmin / Staff
- **Query Params:** `status`, `category`
- **Response (200 OK):** All listings with status and landlord history.

---

### 9.8 Update Property Moderation Status
- **Method:** `PATCH`
- **Endpoint:** `/api/v1/admin/properties/<str:pk>/status/`
- **Auth:** SuperAdmin / Staff
- **Request Body:**
```json
{
  "status": "active"
}
```
- **Response (200 OK):** Updated property record.
- **Admin Verification Workflow:**
  - Transitioning to `status: "active"` sets `is_available: true`, publishes listing to the public marketplace, and immediately triggers instant alerts to all tenants with matching saved searches.
  - Transitioning to `status: "rejected"` or `"pending_approval"` keeps `is_available: false` (hidden from public searches).
  - Transitioning to `status: "rented"` moves the property to the Landlord's Vault.

---

### 9.9 AI Spam & Duplicate Detector Queue
- **Method:** `GET`
- **Endpoint:** `/api/v1/admin/ai-spam-queue/`
- **Auth:** SuperAdmin / Staff
- **Response (200 OK):** AI-flagged duplicate or broker-spammed listings with similarity scores.

---

### 9.10 Resolve AI Spam Report
- **Method:** `POST`
- **Endpoint:** `/api/v1/admin/ai-spam-queue/<str:pk>/resolve/`
- **Auth:** SuperAdmin / Staff
- **Request Body:**
```json
{
  "action": "listing_banned"
}
```
- **Response (200 OK):** Resolution confirmation.

---

### 9.11 Demand vs Supply Heatmap Telemetry
- **Method:** `GET`
- **Endpoint:** `/api/v1/admin/analytics/demand-supply-heatmap/`
- **Auth:** SuperAdmin / Staff
- **Response (200 OK):** High-precision geospatial market density points for Mirpur, Dhanmondi, Gulshan, Uttara, Bashundhara.

---

### 9.12 User Directory & Anti-Broker Registry
- **Method:** `GET`
- **Endpoint:** `/api/v1/admin/users/`
- **Auth:** SuperAdmin / Staff
- **Query Params:** `role`, `search`
- **Response (200 OK):** User directory list.

---

### 9.13 Toggle User Ban & Flag Broker
- **Method:** `POST`
- **Endpoint:** `/api/v1/admin/users/<str:pk>/ban/`
- **Auth:** SuperAdmin / Staff
- **Response (200 OK):** Updated user ban and broker status.

---

### 9.14 Digital Rent & Monetization Revenue Ledger
- **Method:** `GET`
- **Endpoint:** `/api/v1/admin/finance/ledger/`
- **Auth:** SuperAdmin / Staff
- **Response (200 OK):** All financial transactions, bills, boosts, and partner commissions.

---

## 📊 Complete 67-Endpoint Master Audit Matrix

| # | HTTP Method | Endpoint URI | View Class | Module | Auth |
| :- | :--- | :--- | :--- | :--- | :--- |
| 1 | `POST` | `/api/v1/auth/otp/request/` | `OTPRequestView` | Accounts | Public |
| 2 | `POST` | `/api/v1/auth/otp/verify/` | `OTPVerifyView` | Accounts | Public |
| 3 | `POST` | `/api/v1/auth/register/` | `RegisterView` | Accounts | Public |
| 4 | `POST` | `/api/v1/auth/login/` | `PasswordLoginView` | Accounts | Public |
| 5 | `POST` | `/api/v1/auth/token/refresh/` | `TokenRefreshView` | Accounts | Public |
| 6 | `POST` | `/api/v1/auth/role/switch/` | `RoleSwitchView` | Accounts | Bearer |
| 7 | `POST` | `/api/v1/auth/change-password/` | `ChangePasswordView` | Accounts | Bearer |
| 8 | `GET`, `PATCH` | `/api/v1/auth/profile/` | `UserProfileView` | Accounts | Bearer |
| 9 | `POST` | `/api/v1/auth/nid-verify/` | `NIDVerifyView` | Accounts | Bearer |
| 10 | `POST` | `/api/v1/auth/logout/` | `LogoutView` | Accounts | Bearer |
| 11 | `GET`, `POST` | `/api/v1/properties/` | `PropertyListCreateView` | Properties | Public / Landlord |
| 12 | `GET`, `PATCH`, `DELETE` | `/api/v1/properties/<uuid:pk>/` | `PropertyDetailView` | Properties | Public / Owner |
| 13 | `POST` | `/api/v1/properties/<uuid:pk>/toggle-vault/` | `PropertyVaultToggleView` | Properties | Owner Landlord |
| 14 | `POST` | `/api/v1/properties/<uuid:pk>/save/` | `PropertySaveToggleView` | Properties | Bearer |
| 15 | `GET` | `/api/v1/properties/saved/` | `SavedPropertiesListView` | Properties | Bearer |
| 16 | `POST` | `/api/v1/properties/<uuid:pk>/photos/` | `PropertyPhotoUploadView` | Properties | Owner Landlord |
| 17 | `POST` | `/api/v1/properties/<uuid:pk>/confirm-availability/` | `ListingAvailabilityConfirmView` | Properties | Owner Landlord |
| 18 | `POST` | `/api/v1/properties/<uuid:pk>/boost/` | `MonetizationBoostView` | Properties | Owner Landlord |
| 19 | `GET`, `POST` | `/api/v1/properties/saved-searches/` | `SavedSearchListCreateView` | Properties | Bearer |
| 20 | `GET` | `/api/v1/properties/saved-searches/alerts/` | `SavedSearchAlertListView` | Properties | Bearer |
| 21 | `PATCH` | `/api/v1/properties/saved-searches/alerts/<uuid:pk>/read/` | `SavedSearchAlertMarkReadView` | Properties | Bearer |
| 22 | `GET` | `/api/v1/properties/ai_search/` | `AISearchView` | Properties AI | Public |
| 23 | `POST` | `/api/v1/properties/draw-search/` | `DrawOnMapSearchView` | Properties GIS | Public |
| 24 | `POST` | `/api/v1/properties/compare/` | `PropertyCompareView` | Properties | Public |
| 25 | `POST` | `/api/v1/properties/calculate-move-in/` | `MoveInCostCalculatorView` | Properties | Public |
| 26 | `POST` | `/api/v1/properties/<uuid:pk>/move-in-cost/` | `MoveInCostCalculatorView` | Properties | Public |
| 27 | `GET` | `/api/v1/properties/<uuid:pk>/fair-rent-meter/` | `AIFairRentMeterView` | Properties AI | Public |
| 28 | `POST` | `/api/v1/properties/ai/classify-photo/` | `AIPhotoClassifierView` | Properties AI | Public |
| 29 | `POST` | `/api/v1/properties/ai-generate-description/` | `AIListingWriterView` | Properties AI | Bearer |
| 30 | `POST` | `/api/v1/properties/ai/generate-agreement/` | `AIRentAgreementGeneratorView` | Properties AI | Bearer |
| 31 | `POST` | `/api/v1/properties/commute-calculator/` | `CommuteCalculatorView` | Properties GIS | Public |
| 32 | `GET` | `/api/v1/properties/<uuid:pk>/nearby-essentials/` | `NearbyEssentialsView` | Properties GIS | Public |
| 33 | `GET` | `/api/v1/properties/<uuid:pk>/street-view/` | `StreetViewPreviewView` | Properties GIS | Public |
| 34 | `GET` | `/api/v1/properties/services/partners/` | `AffiliatePartnersView` | Services | Public |
| 35 | `POST` | `/api/v1/properties/services/book/` | `BookPartnerServiceView` | Services | Bearer |
| 36 | `POST` | `/api/v1/properties/admin/detect-spam/` | `AdminSpamDetectorView` | Admin AI | Public / Staff |
| 37 | `GET` | `/api/v1/properties/analytics/demand-supply-heatmap/` | `DemandSupplyHeatmapView` | Analytics | Public |
| 38 | `POST` | `/api/v1/inquiries/` | `InquiryCreateView` | Inquiries | Bearer |
| 39 | `GET` | `/api/v1/inquiries/landlord-inbox/` | `LandlordScreeningInboxView` | Inquiries | Landlord |
| 40 | `PATCH` | `/api/v1/inquiries/<uuid:pk>/status/` | `InquiryStatusUpdateView` | Inquiries | Landlord |
| 41 | `GET`, `POST` | `/api/v1/inquiries/visits/` | `VisitBookingListCreateView` | Inquiries | Bearer |
| 42 | `PATCH` | `/api/v1/inquiries/visits/<uuid:pk>/status/` | `VisitBookingStatusUpdateView` | Inquiries | Bearer |
| 43 | `GET` | `/api/v1/insights/area/` | `AreaInsightsView` | Insights | Public |
| 44 | `POST` | `/api/v1/insights/submit/` | `AreaInsightSubmitView` | Insights | Bearer |
| 45 | `GET`, `POST` | `/api/v1/ledger/tenancies/` | `TenancyContractListCreateView` | Ledger | Bearer |
| 46 | `GET`, `POST` | `/api/v1/ledger/bills/` | `RentBillListCreateView` | Ledger | Bearer |
| 47 | `POST` | `/api/v1/ledger/bills/<uuid:pk>/mark-paid/` | `MarkBillPaidView` | Ledger | Landlord |
| 48 | `GET` | `/api/v1/ledger/bills/<uuid:pk>/receipt/` | `RentReceiptDetailView` | Ledger | Bearer |
| 49 | `POST` | `/api/v1/ledger/bills/<uuid:pk>/send-reminder/` | `SendBillReminderView` | Ledger | Landlord |
| 50 | `GET`, `POST` | `/api/v1/chat/rooms/` | `ChatRoomListCreateView` | Chat | Bearer |
| 51 | `GET`, `POST` | `/api/v1/chat/rooms/<uuid:pk>/messages/` | `ChatMessageListCreateView` | Chat | Bearer |
| 52 | `POST` | `/api/v1/chat/rooms/<uuid:pk>/call-token/` | `MaskedCallTokenView` | Chat VoIP | Bearer |
| 53 | `PATCH` | `/api/v1/chat/calls/<uuid:pk>/` | `MaskedCallSessionUpdateView` | Chat VoIP | Bearer |
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

