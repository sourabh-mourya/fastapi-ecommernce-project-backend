# fastapi-ecommernce-project-backend


# Order Service Flow

## Services Structure

```
services/
    ├── orderService.py      # order create, update, cancel
    ├── paymentService.py    # payment initiate, verify, refund
    └── couponService.py     # coupon validate, apply
```

---

## 1. Create Order

```
Request aaya
    ↓
User token se nikalo (user_id)
    ↓
Har item ka product_id check karo — exist karta hai?
    ↓
❌ Nahi mila → 404 error
    ↓
Product ka stock check karo — quantity available hai?
    ↓
❌ Stock nahi → 400 error
    ↓
Coupon apply kiya hai?
    ↓
✅ Haan → coupon exist karta hai?
         → active hai?
         → valid date range mein hai?
         → min_order_amount satisfy hoti hai?
         → usage_limit reach nahi hua?
         ❌ Koi bhi fail → 400 error
    ↓
Subtotal calculate karo — har item ka quantity × unit_price
    ↓
Discount   karo — flat ya percentage
    ↓
Total validate karo — subtotal - discount + shipping_fee = total_amount
    ↓
❌ Total galat → 400 error
    ↓
Order DB mein save karo
    ↓
Coupon used_count +1 karo
    ↓
Product stock update karo — quantity minus karo
    ↓
Payment initiate karo
    ↓
Response return karo
```

---

## 2. Payment Flow

```
Order create hua
    ↓
Payment method kya hai?
    ↓
COD → Order status = confirmed
      Payment status = unpaid
      Payment record banao
    ↓
Razorpay/Stripe → Gateway pe order create karo
                  gateway_order_id milega
                  Payment record banao status = initiated
                  Frontend ko gateway_order_id bhejo
                  Frontend payment kare
                  Webhook aayega
                      ↓
                  Signature verify karo
                      ↓
                  ❌ Invalid → 400 error
                      ↓
                  ✅ Valid → Payment status = paid
                             Order status = confirmed
                             Payment record update karo
```

---

## 3. Coupon Apply

```
Coupon code aaya
    ↓
DB mein code dhundo
    ↓
❌ Nahi mila → 404 error
    ↓
is_active check karo
    ↓
❌ Inactive → 400 error
    ↓
valid_from aur valid_until check karo
    ↓
❌ Expired → 400 error
    ↓
min_order_amount check karo
    ↓
❌ Order amount kam → 400 error
    ↓
usage_limit check karo
    ↓
❌ Limit reach → 400 error
    ↓
Type check karo
    ↓
FLAT       → discount = coupon.value
PERCENTAGE → discount = subtotal × (value/100)
             max_discount cap check karo
    ↓
CouponSnapshot banao aur order mein store karo
```

---

## 4. Order Status Update

```
Admin status update kare
    ↓
Current status kya hai?
    ↓
PENDING   → sirf CONFIRMED ho sakta hai
CONFIRMED → sirf SHIPPED ho sakta hai
SHIPPED   → sirf DELIVERED ho sakta hai
DELIVERED → kuch nahi ho sakta
CANCELLED → kuch nahi ho sakta
    ↓
❌ Invalid transition → 400 error
    ↓
Timestamp update karo
confirmed_at / shipped_at / delivered_at / cancelled_at
    ↓
DB update karo
```

---

## 5. Cancel Order

```
Cancel request aaya
    ↓
Order exist karta hai?
    ↓
❌ Nahi → 404 error
    ↓
Status check karo — DELIVERED ya already CANCELLED?
    ↓
❌ Haan → 400 error — cancel nahi ho sakta
    ↓
Payment status check karo
    ↓
PAID → Refund initiate karo
       refund_id store karo
       refund_amount store karo
       Payment status = REFUNDED
    ↓
Stock wapas karo — quantity plus karo products mein
    ↓
Coupon use tha → used_count -1 karo
    ↓
Order status = CANCELLED
cancelled_at = now
    ↓
DB update karo
```

---

## Service Responsibilities

### `couponService.py`

```python
validateCoupon(code, subtotal)
    → coupon check karo
    → discount calculate karo
    → CouponSnapshot return karo
```

### `paymentService.py`

```python
initiatePayment(order_id, amount, method)
    → Payment record banao
    → COD hai → seedha confirm
    → Gateway hai → gateway pe request karo

verifyPayment(gateway_order_id, transaction_id, signature)
    → signature verify karo
    → Payment record update karo
    → Order status update karo

refundPayment(payment_id, amount)
    → Gateway pe refund karo
    → Payment record update karo
```

### `orderService.py`

```python
createOrder(data, user)
    → couponService.validateCoupon() call karo   ← coupon service use karo
    → product check karo
    → stock check karo
    → order save karo
    → paymentService.initiatePayment() call karo ← payment service use karo
    → stock update karo
    → coupon used_count update karo

updateOrderStatus(order_id, new_status)
    → status transition check karo
    → timestamp update karo

cancelOrder(order_id)
    → status check karo
    → paymentService.refundPayment() call karo   ← payment service use karo
    → stock wapas karo
    → coupon used_count -1 karo
```

---

## Overall Flow

```
Route
  ↓
orderService          ← main coordinator
  ↓           ↓
coupon       payment
Service      Service
```

> `orderService` ek main coordinator hai — woh directly `couponService` aur `paymentService` ko call karta hai. Saari business logic in teeno services mein distributed hai.