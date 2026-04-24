import razorpay
import hmac
import hashlib
from app.config import settings

# Initialize client
client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)

# CREATE ORDER

def create_order(amount_inr: float, receipt: str):
    return client.order.create({
        "amount": int(amount_inr * 100),  # convert to paise
        "currency": "INR",
        "receipt": receipt,
        "payment_capture": 1
    })

# VERIFY PAYMENT SIGNATURE

def verify_payment(razorpay_order_id: str, razorpay_payment_id: str, razorpay_signature: str):
    body = f"{razorpay_order_id}|{razorpay_payment_id}"

    expected_signature = hmac.new(
        bytes(settings.RAZORPAY_KEY_SECRET, "utf-8"),
        bytes(body, "utf-8"),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected_signature, razorpay_signature)

# REFUND PAYMENT

def refund_payment(payment_id: str, amount_paise: int | None = None):
    try:
        if amount_paise:
            return client.payment.refund(payment_id, {"amount": amount_paise})
        return client.payment.refund(payment_id)
    except Exception as e:
        print(f"[refund_error] {e}")
        return None