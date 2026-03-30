# FastAPI + MongoDB + Razorpay — Poore Notes (Hinglish)

---

## 1. Pydantic Model kya hota hai?

Socho ek **security guard** hai jo door pe baitha hai — andar aane se pehle check karta hai ki sab sahi hai ya nahi.

Jab bhi user data bhejta hai — Pydantic pehle check karta hai:
- Sahi type hai? (str, int, float)
- Required fields hain?
- gt=0, ge=0 jaise constraints sahi hain?

```python
class OrderCreate(BaseModel):
    order_number: str
    total_amount: float = Field(..., gt=0)  # 0 se bada hona chahiye
```

```
User ne data bheja
    ↓
Pydantic ne check kiya
    ↓
❌ Galat → 422 error → function chala hi nahi
✅ Sahi  → function chala → DB mein save hua
```

> **Simple:** Pydantic = Door pe security guard. Galat data andar aaya hi nahi.

---

## 2. `model_dump()` kab use karte hain?

`model_dump()` Pydantic object ko **dict mein convert** karta hai.

MongoDB ko dict chahiye insert karne ke liye — isliye `model_dump()` use karte hain.

```python
data = OrderCreate(order_number="ORD-001", total_amount=500)

# ✅ DB mein insert karna hai
order_dict = data.model_dump()
# { "order_number": "ORD-001", "total_amount": 500 }
await collection.insert_one(order_dict)

# ✅ Sirf ek field chahiye — seedha dot se lo
data.order_number   # "ORD-001"
data.total_amount   # 500
```

| Situation | Tarika |
|---|---|
| DB mein insert karna | `data.model_dump()` |
| Sirf ek field access | `data.field_name` |

> **Simple:** `model_dump()` = Pydantic object ka DNA nikalo dict mein.

---

## 3. DB se data fetch kiya toh kaise access karo?

DB se jo data aata hai wo **pehle se dict hota hai** — `model_dump()` ki zaroorat nahi.

```python
# DB se aaya — pehle se dict hai
user = await user_collection.find_one({"email": "test@test.com"})

# ✅ [] se access karo
user["name"]
user["email"]
user["_id"]

# ❌ dot notation nahi chalega
user.name   # Error aayega
```

| Data kahan se aaya | Kaise access karo |
|---|---|
| Pydantic object (user ne bheja) | `data.name` dot se |
| DB se fetch kiya | `user["name"]` bracket se |
| Pydantic → DB mein dalna | `data.model_dump()` |

> **Simple:** User ne bheja = dot. DB se aaya = bracket `[]`.

---

## 4. `response_model` kya hota hai?

`response_model` ek **filter** ki tarah kaam karta hai — sirf wahi fields client ko jaati hain jo tumne define ki hain.

```python
class OrderResponse(BaseModel):
    order_number: str
    total_amount: float
    # user_id, internal_notes — yeh nahi jayenge

@router.post('/create_order', response_model=OrderResponse)
async def createOrder(data: OrderCreate):
    return order  # poora order — but sirf OrderResponse wali fields jayengi
```

```
DB se poora document aaya:
{ order_number, total_amount, user_id, internal_notes, _id ... }
    ↓
response_model ne filter kiya
    ↓
Client ko mila:
{ order_number, total_amount }
```

| Model | Kaam |
|---|---|
| `OrderCreate` | User se input lo — sirf wahi fields |
| `Order` | DB mein store — saari fields |
| `OrderResponse` | Client ko bhejo — filtered fields |

> **Simple:** response_model = Output ka filter. Jo dikhana ho wahi likho.

---

## 5. `@field_validator` kya hota hai?

Field save hone se **pehle check** karta hai ki value sahi hai ya nahi.

```python
@field_validator("total")
@classmethod
def total_must_match(cls, v, info):
    data = info.data
    expected = data["quantity"] * data["unit_price"]
    if abs(v - expected) > 0.01:
        raise ValueError("total galat hai")
    return v
```

```
quantity=2, unit_price=500, total=999 bheja
    ↓
field_validator ne check kiya
    ↓
❌ 2×500=1000 ≠ 999 → Error → Object bana hi nahi
```

> **Simple:** field_validator = Object banne se pehle ka last check.

---

## 6. Beanie kya hota hai?

Beanie ek **MongoDB ODM** hai — matlab Mongoose ka Python version.

Beanie ka main kaam:
- Tumhari Document class dekh ke **MongoDB mein sahi collection mein jaata hai**
- `Settings` class mein jo `name` diya — wahi collection use hoti hai

```python
class Order(Document):
    order_number: str
    total_amount: float

    class Settings:
        name = "orders"  # ← MongoDB mein "orders" collection mein jayega
```

```
await order.insert()
    ↓
Beanie ne dekha — Settings mein name = "orders"
    ↓
MongoDB ke "orders" collection mein insert ho gaya
```

### Bina Beanie ke (Raw MongoDB):
```python
# khud collection ka naam likhna padta
await db["orders"].insert_one({"order_number": "ORD-001"})
```

### Beanie ke saath:
```python
# clean — collection ka naam khud jaanta hai
order = Order(order_number="ORD-001")
await order.insert()
```

> **Simple:** Beanie = Collection manager. Tum sirf object banao — Beanie jaanta hai kahan dalna hai.

---

## 7. `Indexed` kya hota hai?

`Indexed` MongoDB mein **fast search** ke liye index lagata hai — existence check nahi karta.

```python
class Order(Document):
    order_number: Annotated[str, Indexed(unique=True)]  # unique index
    user_id: Annotated[PydanticObjectId, Indexed()]     # normal index
```

```
Indexed lagaya → MongoDB mein index bana
    ↓
Query fast chalegi is field pe
    ↓
Existence check — khud karna padega service mein
```

> **Simple:** Indexed = Speed boost for search. Existence check alag karo.

---

## 8. ObjectId ka Issue

MongoDB ka `_id` field **ObjectId** type ka hota hai — string nahi.

```python
from bson import ObjectId

# ❌ String se query nahi hogi
await collection.find_one({"_id": "69c7e6310b72974a64a13433"})

# ✅ ObjectId mein convert karo
await collection.find_one({"_id": ObjectId("69c7e6310b72974a64a13433")})
```

> **Simple:** DB mein ID dhundhni ho toh pehle ObjectId() mein wrap karo.

---

## 9. serialize_doc kyun chahiye?

MongoDB se jo data aata hai usme `ObjectId` aur `datetime` hote hain — yeh **JSON mein directly nahi jaate**.

```python
def serialize_doc(doc):
    if isinstance(doc, dict):
        return {key: serialize_doc(value) for key, value in doc.items()}
    elif isinstance(doc, list):
        return [serialize_doc(item) for item in doc]
    elif isinstance(doc, ObjectId):
        return str(doc)         # ObjectId → "69c7e6310b72974a64a13433"
    elif isinstance(doc, datetime):
        return doc.isoformat()  # datetime → "2024-03-15T10:30:00"
    return doc
```

```
DB se document aaya
    ↓
{ "_id": ObjectId(...), "placed_at": datetime(...) }
    ↓
serialize_doc ne convert kiya
    ↓
{ "_id": "69c7e...", "placed_at": "2024-03-15T10:30:00" }
    ↓
JSON response sahi gaya ✅
```

> **Simple:** serialize_doc = MongoDB objects ko JSON friendly banao.

---

## 10. Razorpay Payment — Pura Flow

### Step 1 — Order Initiate (Backend):
```
Frontend → POST /payment/initiate { order_id }
    ↓
Backend → DB se order dhunda → amount nikala
    ↓
razorpayInstance.order.create({ amount, currency })
    ↓
Razorpay ne diya → razorpay_order_id = "order_OFldlApBuMaZ8t"
    ↓
DB mein payment save kiya status = "initiated"
    ↓
Frontend ko bheja → razorpay_order_id, amount, currency
```

### Step 2 — Checkout (Frontend):
```
Frontend ko mila razorpay_order_id
    ↓
new Razorpay({ key, order_id, amount })
    ↓
Razorpay checkout UI khuli
    ↓
User ne card/UPI se pay kiya
    ↓
Razorpay ne handler() mein diya:
    razorpay_payment_id = "pay_Nxxxxxxxx"
    razorpay_signature  = "abc123xyz..."
    razorpay_order_id   = "order_OFldlApBuMaZ8t"
```

### Step 3 — Verify (Backend):
```
Frontend → POST /payment/verify
    ↓
Backend ne HMAC signature generate kiya:
body = "order_id|payment_id"
generated = hmac.new(secret, body, sha256).hexdigest()
    ↓
generated == razorpay_signature?
    ↓
❌ Nahi → 400 "Invalid signature"
✅ Haan → Order status = confirmed, payment_status = paid
```

### IDs ka fark:
| ID | Kahan se aaya |
|---|---|
| `order_id` | Tumhara MongoDB ka _id |
| `razorpay_order_id` | Razorpay ne diya order.create() pe |
| `razorpay_payment_id` | User ne pay kiya tab Razorpay ne diya |
| `razorpay_signature` | User ne pay kiya tab Razorpay ne diya |

---

## 11. Interview Mein Kya Puch Sakte Hain

### Pydantic:
- Pydantic kya hai aur FastAPI mein kaise use hota hai?
- `model_dump()` kab use karte hain?
- `field_validator` kya kaam karta hai?
- `BaseModel` aur `Document` mein kya fark hai?

### FastAPI:
- `response_model` kyu use karte hain?
- `Depends()` kya hota hai?
- FastAPI mein request validation kaise hoti hai?
- Async await kyun use karte hain?

### MongoDB:
- ObjectId kya hota hai aur string se kaise alag hai?
- `find_one` aur `find` mein kya fark hai?
- `$inc`, `$set` operators kya karte hain?
- Index lagane se kya fayda hota hai?

### Beanie:
- Beanie kya hai aur kyun use karte hain?
- `Settings` class mein `name` kya karta hai?
- Raw MongoDB aur Beanie mein kya fark hai?

### Payment:
- Razorpay payment flow explain karo?
- HMAC signature verification kyun zaroori hai?
- `razorpay_order_id` aur `razorpay_payment_id` mein kya fark hai?
- Payment tamper ho sakti hai kya? Kaise rokenge?
- Webhook kyun use karte hain?

### Security:
- Amount client se kyun nahi lena chahiye?
- JWT token kya hota hai?
- Sensitive data response mein kyun nahi bhejte?

---

## 12. Common Mistakes Jo Hoti Hain

| Galti | Sahi |
|---|---|
| `data.model_dump()` bina DB insert | Hamesha `model_dump()` use karo insert mein |
| DB se aaye data pe dot notation | `[]` bracket use karo |
| `await` bhool gaye async function mein | Har async call pe `await` lagao |
| ObjectId ko string se compare kiya | `ObjectId()` mein convert karo |
| Amount client se liya | Hamesha DB se lo |
| `response_model` use nahi kiya | Sensitive data leak ho sakta hai |
| Collection name mismatch | `db.py` aur `Settings` mein same naam rakho |