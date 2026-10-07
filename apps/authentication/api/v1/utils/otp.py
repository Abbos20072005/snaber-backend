import random

import redis
from django.core.mail import send_mail

from config import settings

redis_client = redis.StrictRedis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=True,
)


def generate_code():
    return random.randint(100000, 999999)


def send_verification_email(email):
    code = generate_code()

    redis_client.setex(f"otp:{email}", settings.OTP_EXPIRY, code)

    send_mail(
        subject="Your verification code",
        message=f"Your verification code is: {code}",
        from_email="jonh1234554321@gmail.com",
        recipient_list=[email],
        fail_silently=False,
    )


def verify_code(email, code):
    key = f"otp:{email}"
    saved_code = redis_client.get(key)

    if saved_code is None:
        return False

    if saved_code == str(code):
        redis_client.delete(key)
        return True

    return False


def send_forget_password_email(email):
    code = generate_code()
    redis_client.setex(f"forget_password_otp:{email}", settings.OTP_EXPIRY, code)
    send_mail(
        subject="Password reset code",
        message=f"Your password reset code is: {code}",
        from_email="jonh1234554321@gmail.com",
        recipient_list=[email],
        fail_silently=False,
    )


def verify_forget_password_code(email, code):
    key = f"forget_password_otp:{email}"
    saved_code = redis_client.get(key)

    if saved_code is None:
        return False

    if saved_code == str(code):
        redis_client.delete(key)
        return True

    return False
