# fastapi-payment-integration

FastAPI + MongoDB + Razorpay ka pura payment integration — Order create karo, coupon apply karo, Razorpay se pay karo, verify karo, refund karo.

---

## Tech Stack

| Technology | Kaam |
|---|---|
| FastAPI | Backend framework |
| MongoDB | Database |
| Motor | Async MongoDB driver |
| Beanie | MongoDB ODM |
| Pydantic | Data validation |
| Razorpay | Payment gateway |
| JWT | Authentication |

---

## Project Structure

```
backend/
├── app.py                  # FastAPI app, startup, routes register
├── config/
│   ├── db.py               # MongoDB connection, collections
│   ├── Env.py              # Environment variables
│   └── razorpayConfig.py   # Razorpay client instance
├── models/
│   ├── orderModel.py       # Order, Payment, Coupon, Enums
│   ├── paymentModel.py     # PaymentInitiate, PaymentVerify, PaymentRefund
│   └── couponModel.py      # Coupon input model
├── routes/
│   ├── authRoute.py        # Register, Login
│   ├── productRoute.py     # Product CRUD
│   ├── orderRoute.py       # Order create
│   ├── couponRoute.py      # Coupon create, delete
│   └── paymentRoute.py     # Initiate, Verify, Refund
├── controllers/
│   ├── orderController.py
│   ├── couponController.py
│   └── paymentController.py
├── services/
│   ├── orderService.py
│   ├── couponService.py
│   └── paymentService.py
├── middleware/
│   └── verifyToken.py      # JWT verify middleware
└── .env
```

---

## Setup

### 1. Clone karo
```bash
git clone https://github.com/yourusername/fastapi-payment-integration
cd fastapi-payment-integration/backend
```

### 2. Virtual environment banao
```bash
python -m venv venv
venv\Scripts\activate       # Windows
source venv/bin/activate    # Mac/Linux
```

### 3. Dependencies install karo
```bash
pip install fastapi uvicorn beanie motor pydantic[email] razorpay python-jose bcrypt python-dotenv
```

### 4. `.env` file banao
```env
MONGO_URI=mongodb://localhost:27017
DB_NAME=ecom_db
JWT_SECRET=your_jwt_secret
RAZORPAY_KEY_ID=rzp_test_xxxxxxxx
RAZORPAY_KEY_SECRET=xxxxxxxxxxxxxxxx
```

### 5. Server start karo
```bash
uvicorn app:app --reload
```

---

## API Endpoints

### Auth
| Method | Route | Kaam |
|---|---|---|
| POST | `/api/v1/auth/register` | User register |
| POST | `/api/v1/auth/login` | User login → token milega |

### Product
| Method | Route | Kaam |
|---|---|---|
| POST | `/api/v1/product/create` | Product banao (admin) |
| GET | `/api/v1/product/all` | Saare products |
| GET | `/api/v1/product/:id` | Ek product |

### Order
| Method | Route | Kaam |
|---|---|---|
| POST | `/api/v1/order/create_order` | Order banao |

### Coupon
| Method | Route | Kaam |
|---|---|---|
| POST | `/api/v1/coupon/create_coupon` | Coupon banao (admin) |
| DELETE | `/api/v1/coupon/delete_coupon/:id` | Coupon delete (admin) |

### Payment
| Method | Route | Kaam |
|---|---|---|
| POST | `/api/v1/payment/initiate` | Payment shuru karo |
| POST | `/api/v1/payment/verify` | Payment verify karo |
| POST | `/api/v1/payment/refund` | Refund karo |

---

## Payment Flow

```
1. POST /order/create_order
   Body: { order_number, address, items, shipping_fee, coupon_code, payment_method }
   Response: { data: { _id, order_number, total_amount } }
        ↓
2. POST /payment/initiate
   Body: { order_id, payment_method: "razorpay" }
   Response: { razorpay_order_id, amount, currency }
        ↓
3. Frontend Razorpay Checkout open karo
   Razorpay khud deta hai:
     - razorpay_payment_id
     - razorpay_signature
     - razorpay_order_id
        ↓
4. POST /payment/verify
   Body: { order_id, razorpay_order_id, razorpay_payment_id, razorpay_signature }
   Response: { msg: "Payment verified successfully" }
```

---

## Postman Testing

### Step 1 — Register
```json
POST /api/v1/auth/register
{
  "name": "Rahul Sharma",
  "email": "rahul@test.com",
  "password": "123456"
}
```

### Step 2 — Login → Token lo
```json
POST /api/v1/auth/login
{
  "email": "rahul@test.com",
  "password": "123456"
}
```

### Step 3 — Coupon banao
```json
POST /api/v1/coupon/create_coupon
Headers: Authorization: Bearer <token>
{
  "code": "SAVE50",
  "type": "flat",
  "value": 50.0,
  "min_order_amount": 500.0,
  "valid_from": "2026-01-01T00:00:00",
  "valid_until": "2026-12-31T23:59:59"
}
```

### Step 4 — Order banao
```json
POST /api/v1/order/create_order
Headers: Authorization: Bearer <token>
{
  "order_number": "ORD-001",
  "address": {
    "full_name": "Rahul Sharma",
    "phone": "9876543210",
    "line1": "123 MG Road",
    "city": "Raipur",
    "state": "Chhattisgarh",
    "pincode": "492001"
  },
  "items": [
    {
      "product_id": "65f1a2b3c4d5e6f7a8b9c0d1",
      "product_name": "Nike Air Max",
      "quantity": 1,
      "unit_price": 500.0,
      "total": 500.0
    }
  ],
  "shipping_fee": 100.0,
  "coupon_code": "SAVE50",
  "payment_method": "razorpay"
}
```

### Step 5 — Payment Initiate
```json
POST /api/v1/payment/initiate
Headers: Authorization: Bearer <token>
{
  "order_id": "<order_id jo step 4 mein mila>",
  "payment_method": "razorpay"
}
```

### Step 6 — COD Test (Postman se seedha)
```json
POST /api/v1/payment/initiate
Headers: Authorization: Bearer <token>
{
  "order_id": "<order_id>",
  "payment_method": "cod"
}
```

---

## Validation Rules

| Cheez | Rule |
|---|---|
| Order total | `subtotal - discount + shipping_fee = total_amount` |
| Item total | `quantity × unit_price = total` |
| Product price | Frontend se aayi price DB se match honi chahiye |
| Product stock | Order quantity stock se zyada nahi honi chahiye |
| Coupon | Active, valid date, min amount, usage limit check |
| Payment signature | HMAC SHA256 verify hoti hai |

---

## Frontend React Integration

```jsx
// .env mein
VITE_RAZORPAY_KEY_ID=rzp_test_xxxxxxxx

// Component use karo
<CheckoutPayment />
```

Razorpay checkout ke baad automatically `razorpay_payment_id` aur `razorpay_signature` milte hain — frontend ne `/verify` pe bhej diye.

---

## Important Notes

- Amount **kabhi client se mat lo** — hamesha DB se lo
- `razorpay_signature` verify karna **zaroori** hai — bina iske koi bhi fake payment bhej sakta hai
- Stock **order ke baad minus** hota hai
- Coupon `used_count` **order ke baad +1** hota hai
- Cancel hone pe stock **wapas plus** hota hai
