import logging
import secrets

import redis
import requests
from django.conf import settings

from apps.core.exceptions import (
    ExternalServiceException,
    TooManyRequestsException,
    ValidationError,
)

logger = logging.getLogger(__name__)

OTP_LENGTH = 6

redis_client = redis.StrictRedis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=True,
)


def _key(kind: str, phone: str) -> str:
    return f"otp:{kind}:{phone}"


def generate_code() -> str:
    return "".join(secrets.choice("0123456789") for _ in range(OTP_LENGTH))


def deliver_code(phone: str, code: str) -> None:
    """Send the OTP code. Telegram channel for now, an SMS provider later."""
    token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_OTP_CHAT_ID

    if not token or not chat_id:
        logger.warning("Telegram is not configured, OTP for %s: %s", phone, code)
        return

    minutes = settings.OTP_EXPIRY // 60
    try:
        response = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": (
                    f"Snaber.uz verification code\n"
                    f"Phone: {phone}\n"
                    f"Code: {code}\n"
                    f"Valid for {minutes} min."
                ),
            },
            timeout=10,
        )
        response.raise_for_status()
    except requests.RequestException as err:
        logger.exception("Failed to deliver OTP to Telegram")
        raise ExternalServiceException(
            message="Could not send the verification code. Please try again later.",
            message_key="otp_delivery_failed",
        ) from err


def send_otp(phone: str) -> int:
    """Create and deliver a code. Returns the seconds until the next resend."""
    cooldown_key = _key("cooldown", phone)
    retry_after = redis_client.ttl(cooldown_key)
    if retry_after and retry_after > 0:
        raise TooManyRequestsException(
            message="Please wait before requesting a new code.",
            message_key="otp_cooldown",
            errors={"retry_after": retry_after},
        )

    sends_key = _key("sends", phone)
    sends = redis_client.incr(sends_key)
    if sends == 1:
        redis_client.expire(sends_key, 3600)
    if sends > settings.OTP_MAX_SENDS_PER_HOUR:
        raise TooManyRequestsException(
            message="You have reached the maximum number of OTP requests."
            " Please try again later.",
            message_key="otp_too_many_requests",
            errors={"retry_after": redis_client.ttl(sends_key)},
        )

    code = generate_code()
    deliver_code(phone, code)

    redis_client.setex(_key("code", phone), settings.OTP_EXPIRY, code)
    redis_client.delete(_key("attempts", phone))
    redis_client.setex(cooldown_key, settings.OTP_RESEND_COOLDOWN, 1)
    return settings.OTP_RESEND_COOLDOWN


def verify_otp(phone: str, code: str) -> None:
    """Raise ValidationError unless the code matches. The code is single use."""
    code_key = _key("code", phone)
    saved_code = redis_client.get(code_key)
    if saved_code is None:
        raise ValidationError(
            message="Invalid or expired OTP code.", message_key="otp_invalid"
        )

    attempts_key = _key("attempts", phone)
    attempts = redis_client.incr(attempts_key)
    if attempts == 1:
        redis_client.expire(attempts_key, settings.OTP_EXPIRY)
    if attempts > settings.OTP_MAX_ATTEMPTS:
        redis_client.delete(code_key, attempts_key)
        raise ValidationError(
            message="Too many wrong attempts. Request a new code.",
            message_key="otp_attempts_exceeded",
        )

    if not secrets.compare_digest(saved_code, str(code)):
        raise ValidationError(
            message="Invalid or expired OTP code.", message_key="otp_invalid"
        )

    redis_client.delete(code_key, attempts_key)
