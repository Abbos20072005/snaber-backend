from rest_framework.throttling import ScopedRateThrottle


class OrderRateThrottle(ScopedRateThrottle):
    """Limits accepted orders per client address.

    Oddiy throttle har bir so'rovni sanaydi: formani xato to'ldirib qayta
    yuborgan mijoz limitni tugatib qo'yardi. Bu yerda faqat `record()`
    chaqirilganda, ya'ni buyurtma yaratilgandan keyin sanaladi.
    """

    def throttle_success(self):
        return True

    def record(self):
        # `allow_request()` dan keyin chaqiriladi; tezlik sozlanmagan bo'lsa kalit bo'lmaydi.
        if getattr(self, "key", None) is None:
            return
        self.history.insert(0, self.now)
        self.cache.set(self.key, self.history, self.duration)
