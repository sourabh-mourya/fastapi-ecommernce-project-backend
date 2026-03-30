import { useState, useEffect } from "react";
import axios from "axios";

const BASE_URL = "http://localhost:5000/api/v1";
const RAZORPAY_KEY_ID = import.meta.env.VITE_RAZORPAY_KEY_ID;

const CheckoutPayment = () => {

  const [cartItems, setCartItems] = useState([]);
  const [address, setAddress] = useState({
    full_name: "", phone: "", line1: "", city: "", state: "", pincode: "", country: "India",
  });
  const [couponCode, setCouponCode] = useState("");
  const [orderId, setOrderId] = useState(null);
  const [orderDetails, setOrderDetails] = useState(null);
  const [step, setStep] = useState("checkout");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [razorpayLoaded, setRazorpayLoaded] = useState(false);

  // useEffect 1 — Cart fetch karo
  useEffect(() => {
    const fetchCart = async () => {
      try {
        const response = await axios.get(`${BASE_URL}/cart`, {
          headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
        });
        setCartItems(response.data.items);
      } catch (err) {
        setError("Cart fetch karne mein problem aayi");
      }
    };
    fetchCart();
  }, []);

  // useEffect 2 — Razorpay script load karo
  useEffect(() => {
    if (window.Razorpay) { setRazorpayLoaded(true); return; }
    const script = document.createElement("script");
    script.src = "https://checkout.razorpay.com/v1/checkout.js";
    script.async = true;
    script.onload = () => setRazorpayLoaded(true);
    script.onerror = () => setError("Razorpay load nahi hua");
    document.head.appendChild(script);
    return () => { if (document.head.contains(script)) document.head.removeChild(script); };
  }, []);

  const calculateSubtotal = () => cartItems.reduce((sum, item) => sum + item.total, 0);

  // STEP 1 — Order Create karo
  const createOrder = async () => {
    setLoading(true);
    setError(null);
    try {
      const subtotal = calculateSubtotal();
      const shippingFee = 100;

      // ✅ API CALL 2 — POST /order/create_order
      // Body: { order_number, address, items, subtotal, shipping_fee, coupon_code, payment_method }
      const response = await axios.post(
        `${BASE_URL}/order/create_order`,
        {
          order_number: `ORD-${Date.now()}`,
          address,
          items: cartItems.map((item) => ({
            product_id: item.product_id,
            product_name: item.product_name,
            product_image: item.product_image,
            quantity: item.quantity,
            unit_price: item.unit_price,
            total: item.total,
          })),
          subtotal,
          shipping_fee: shippingFee,
          coupon_code: couponCode || null,
          payment_method: "razorpay",
        },
        { headers: { Authorization: `Bearer ${localStorage.getItem("token")}`, "Content-Type": "application/json" } }
      );

      // Backend ne diya: { msg: "...", data: { _id, order_number, total_amount, ... } }
      const createdOrder = response.data.data;
      console.log("Order created:", createdOrder);

      setOrderId(createdOrder._id);       // payment mein use hoga
      setOrderDetails(createdOrder);      // total dikhane ke liye
      setStep("payment");                 // payment step pe jao
    } catch (err) {
      setError(err.response?.data?.detail || "Order create nahi hua");
    } finally {
      setLoading(false);
    }
  };

  // STEP 2 — Payment Initiate karo
  const initiatePayment = async () => {
    // ✅ API CALL 3 — POST /payment/initiate
    // Body: { order_id, payment_method }
    // Response: { razorpay_order_id, amount, currency }
    const response = await axios.post(
      `${BASE_URL}/payment/initiate`,
      { order_id: orderId, payment_method: "razorpay" },
      { headers: { Authorization: `Bearer ${localStorage.getItem("token")}` } }
    );
    return response.data;
  };

  // STEP 3 — Razorpay Checkout kholo
  const openRazorpayCheckout = (initiateData) => {
    return new Promise((resolve, reject) => {
      const options = {
        key: RAZORPAY_KEY_ID,
        amount: initiateData.amount * 100,          // paise mein
        currency: initiateData.currency,
        order_id: initiateData.razorpay_order_id,   // Razorpay ka order id

        name: "My Shop",
        description: `Order #${orderDetails?.order_number}`,

        // ✅ User ne pay kiya — Razorpay KHUD deta hai:
        // razorpay_payment_id → "pay_Nxxxxxxxx"
        // razorpay_order_id   → "order_OFldlApBuMaZ8t"
        // razorpay_signature  → "abc123..." (HMAC hash)
        handler: function (razorpayResponse) {
          resolve(razorpayResponse);
        },

        prefill: { name: address.full_name, contact: address.phone },
        theme: { color: "#3B82F6" },
        modal: { ondismiss: () => reject(new Error("cancelled")) },
      };

      const rzp = new window.Razorpay(options);
      rzp.on("payment.failed", (res) => reject(new Error(res.error.description)));
      rzp.open();
    });
  };

  // STEP 4 — Payment Verify karo
  const verifyPayment = async (razorpayResponse) => {
    // ✅ API CALL 4 — POST /payment/verify
    // Body: { order_id, razorpay_order_id, razorpay_payment_id, razorpay_signature }
    // Backend HMAC verify karega — tamper hua toh 400 error
    const response = await axios.post(
      `${BASE_URL}/payment/verify`,
      {
        order_id: orderId,
        razorpay_order_id: razorpayResponse.razorpay_order_id,
        razorpay_payment_id: razorpayResponse.razorpay_payment_id,
        razorpay_signature: razorpayResponse.razorpay_signature,
      },
      { headers: { Authorization: `Bearer ${localStorage.getItem("token")}` } }
    );
    return response.data;
  };

  // MAIN — Pay Now click handler
  const handlePayNow = async () => {
    if (!razorpayLoaded) { setError("Razorpay load nahi hua"); return; }
    setLoading(true);
    setError(null);
    try {
      const initiateData = await initiatePayment();         // razorpay_order_id lo
      console.log("Initiate:", initiateData);

      const razorpayResponse = await openRazorpayCheckout(initiateData); // checkout kholo
      console.log("Razorpay ne diya:", razorpayResponse);

      await verifyPayment(razorpayResponse);                // verify karo
      setStep("success");
    } catch (err) {
      if (err.message === "cancelled") {
        setError("Aapne payment cancel kar diya");
      } else {
        setStep("failed");
        setError(err.response?.data?.detail || "Payment fail ho gayi");
      }
    } finally {
      setLoading(false);
    }
  };

  // COD Handler
  const handleCOD = async () => {
    setLoading(true);
    setError(null);
    try {
      await axios.post(
        `${BASE_URL}/payment/initiate`,
        { order_id: orderId, payment_method: "cod" },
        { headers: { Authorization: `Bearer ${localStorage.getItem("token")}` } }
      );
      setStep("success");
    } catch (err) {
      setError(err.response?.data?.detail || "COD place nahi hua");
    } finally {
      setLoading(false);
    }
  };

  // ── UI ──

  if (step === "success") return (
    <div style={styles.container}>
      <div style={{ ...styles.card, borderTop: "4px solid #22c55e" }}>
        <div style={styles.icon}>✅</div>
        <h2 style={{ ...styles.title, color: "#22c55e", textAlign: "center" }}>Payment Successful!</h2>
        <p style={styles.centerText}>Order #{orderDetails?.order_number} confirm ho gaya</p>
      </div>
    </div>
  );

  if (step === "failed") return (
    <div style={styles.container}>
      <div style={{ ...styles.card, borderTop: "4px solid #ef4444" }}>
        <div style={styles.icon}>❌</div>
        <h2 style={{ ...styles.title, color: "#ef4444", textAlign: "center" }}>Payment Failed</h2>
        <p style={styles.errorText}>{error}</p>
        <button style={styles.payButton} onClick={() => { setStep("payment"); setError(null); }}>
          Dobara Try Karo
        </button>
      </div>
    </div>
  );

  return (
    <div style={styles.container}>
      <div style={styles.card}>

        {/* Step Indicator */}
        <div style={styles.stepRow}>
          <span style={styles.stepDot}>1</span>
          <span style={styles.stepLine} />
          <span style={{ ...styles.stepDot, background: step === "payment" ? "#3B82F6" : "#e2e8f0", color: step === "payment" ? "#fff" : "#94a3b8" }}>2</span>
        </div>
        <div style={styles.stepLabels}><span>Checkout</span><span>Payment</span></div>

        {/* CHECKOUT STEP */}
        {step === "checkout" && (
          <>
            <h2 style={styles.title}>Order Summary</h2>
            {cartItems.map((item, i) => (
              <div key={i} style={styles.itemRow}>
                <span style={styles.itemName}>{item.product_name}</span>
                <span style={styles.itemQty}>×{item.quantity}</span>
                <span style={styles.itemPrice}>₹{item.total}</span>
              </div>
            ))}
            <div style={styles.divider} />
            <div style={styles.priceRow}><span>Subtotal</span><span>₹{calculateSubtotal()}</span></div>
            <div style={styles.priceRow}><span>Shipping</span><span>₹100</span></div>
            <div style={{ ...styles.priceRow, fontWeight: "700", fontSize: "16px" }}>
              <span>Total</span><span>₹{calculateSubtotal() + 100}</span>
            </div>
            <div style={styles.divider} />
            <h3 style={styles.sectionTitle}>Delivery Address</h3>
            {["full_name", "phone", "line1", "city", "state", "pincode"].map((field) => (
              <input key={field} style={styles.input}
                placeholder={field.replace("_", " ").toUpperCase()}
                value={address[field]}
                onChange={(e) => setAddress((prev) => ({ ...prev, [field]: e.target.value }))}
              />
            ))}
            <input style={styles.input} placeholder="Coupon Code (optional)"
              value={couponCode} onChange={(e) => setCouponCode(e.target.value)} />
            {error && <p style={styles.errorText}>{error}</p>}
            <button style={{ ...styles.payButton, opacity: loading ? 0.6 : 1 }}
              onClick={createOrder} disabled={loading}>
              {loading ? "Order place ho raha hai..." : "Place Order →"}
            </button>
          </>
        )}

        {/* PAYMENT STEP */}
        {step === "payment" && (
          <>
            <h2 style={styles.title}>Payment</h2>
            <div style={styles.orderBox}>
              <p style={styles.orderNum}>Order #{orderDetails?.order_number}</p>
              <p style={styles.orderTotal}>Total: ₹{orderDetails?.total_amount}</p>
            </div>
            {error && <p style={styles.errorText}>{error}</p>}
            <button style={{ ...styles.payButton, opacity: loading || !razorpayLoaded ? 0.6 : 1 }}
              onClick={handlePayNow} disabled={loading || !razorpayLoaded}>
              {loading ? "Processing..." : `Pay ₹${orderDetails?.total_amount} Online`}
            </button>
            <button style={styles.codButton} onClick={handleCOD} disabled={loading}>
              Cash on Delivery
            </button>
          </>
        )}
      </div>
    </div>
  );
};

const styles = {
  container: { minHeight: "100vh", backgroundColor: "#f1f5f9", display: "flex", alignItems: "center", justifyContent: "center", padding: "20px", fontFamily: "'Segoe UI', sans-serif" },
  card: { backgroundColor: "#fff", borderRadius: "16px", padding: "32px", width: "100%", maxWidth: "480px", boxShadow: "0 4px 24px rgba(0,0,0,0.08)", borderTop: "4px solid #3B82F6" },
  title: { fontSize: "22px", fontWeight: "700", color: "#1e293b", marginBottom: "20px" },
  sectionTitle: { fontSize: "15px", fontWeight: "600", color: "#475569", margin: "16px 0 8px" },
  stepRow: { display: "flex", alignItems: "center", marginBottom: "4px" },
  stepDot: { width: "28px", height: "28px", borderRadius: "50%", background: "#3B82F6", color: "#fff", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "13px", fontWeight: "700" },
  stepLine: { flex: 1, height: "2px", background: "#e2e8f0", margin: "0 8px" },
  stepLabels: { display: "flex", justifyContent: "space-between", fontSize: "12px", color: "#94a3b8", marginBottom: "20px" },
  itemRow: { display: "flex", justifyContent: "space-between", marginBottom: "8px", fontSize: "14px" },
  itemName: { color: "#334155", flex: 1 },
  itemQty: { color: "#94a3b8", margin: "0 12px" },
  itemPrice: { color: "#1e293b", fontWeight: "600" },
  divider: { height: "1px", background: "#e2e8f0", margin: "12px 0" },
  priceRow: { display: "flex", justifyContent: "space-between", fontSize: "14px", color: "#475569", marginBottom: "6px" },
  input: { width: "100%", padding: "10px 14px", marginBottom: "10px", border: "1.5px solid #e2e8f0", borderRadius: "8px", fontSize: "14px", color: "#334155", boxSizing: "border-box", outline: "none" },
  payButton: { width: "100%", padding: "14px", backgroundColor: "#3B82F6", color: "#fff", border: "none", borderRadius: "10px", fontSize: "16px", fontWeight: "600", cursor: "pointer", marginBottom: "10px" },
  codButton: { width: "100%", padding: "14px", backgroundColor: "#fff", color: "#334155", border: "2px solid #e2e8f0", borderRadius: "10px", fontSize: "16px", fontWeight: "600", cursor: "pointer" },
  orderBox: { background: "#f8fafc", borderRadius: "10px", padding: "16px", marginBottom: "20px" },
  orderNum: { color: "#64748b", fontSize: "13px", marginBottom: "4px" },
  orderTotal: { color: "#1e293b", fontSize: "20px", fontWeight: "700" },
  errorText: { color: "#ef4444", fontSize: "13px", marginBottom: "10px" },
  icon: { fontSize: "48px", textAlign: "center", marginBottom: "16px" },
  centerText: { textAlign: "center", color: "#475569" },
};

export default CheckoutPayment;

// USE KARO: <CheckoutPayment />