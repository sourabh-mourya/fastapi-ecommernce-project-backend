import razorpay
from Env import EnvConfig

razorpayInstance = razorpay.Client(
    auth=(EnvConfig.RAZORPAY_KEY_ID, EnvConfig.RAZORPAY_KEY_SECRET)
)