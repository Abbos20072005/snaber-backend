import json
import logging
from decimal import Decimal, ROUND_HALF_UP
from urllib.request import Request, urlopen

import redis
from django.conf import settings

logger = logging.getLogger(__name__)


class CurrencyService:
    CACHE_KEY_PREFIX = "currency_rate"
    CBU_API_URL = "https://cbu.uz/uz/arkhiv-kursov-valyut/json/{currency}/"

    def __init__(self):
        self._redis = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
        )

    def _cache_key(self, from_cur, to_cur):
        return f"{self.CACHE_KEY_PREFIX}:{from_cur}:{to_cur}"

    def _fetch_rate_from_cbu(self, from_cur, to_cur):
        """Fetch exchange rate from Central Bank of Uzbekistan API.
        CBU provides rates as UZS per foreign currency unit.
        """
        if from_cur == "UZS" and to_cur == "UZS":
            return Decimal("1")

        try:
            if to_cur == "UZS":
                target = from_cur
                invert = False
            elif from_cur == "UZS":
                target = to_cur
                invert = True
            else:
                return None

            url = self.CBU_API_URL.format(currency=target)
            req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
            response = urlopen(req, timeout=5)
            data = json.loads(response.read().decode("utf-8"))

            if not data:
                return None

            rate = Decimal(str(data[0]["Rate"]))
            nominal = Decimal(str(data[0]["Nominal"]))
            rate_per_unit = rate / nominal

            return (Decimal("1") / rate_per_unit) if invert else rate_per_unit

        except Exception as e:
            logger.error(f"Error fetching rate from CBU for {from_cur}-{to_cur}: {e}")
            return None

    def get_rate(self, from_cur, to_cur):
        """Get exchange rate with Redis caching."""
        if from_cur == to_cur:
            return Decimal("1")

        cache_key = self._cache_key(from_cur, to_cur)
        cached_rate = self._redis.get(cache_key)

        if cached_rate:
            return Decimal(cached_rate.decode("utf-8"))

        rate = self._fetch_rate_from_cbu(from_cur, to_cur)
        if rate:
            self._redis.setex(cache_key, settings.CURRENCY_CACHE_TTL, str(rate))
            return rate

        # Return 1 if everything fails, to not break the app
        logger.warning(f"Returning default rate 1 for {from_cur}-{to_cur}")
        return Decimal("1")

    def convert(self, amount, from_cur, to_cur):
        """Convert amount between currencies."""
        if not amount:
            return amount

        if from_cur == to_cur:
            return amount

        rate = self.get_rate(from_cur, to_cur)
        return (Decimal(str(amount)) * rate).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
