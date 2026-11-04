"""Fills a database with a year of believable shop activity, so every dashboard chart
and KPI has something to show. The buyers it creates have a phone number starting with
DEMO_PREFIX, so `--reset` removes exactly them with their orders and carts."""

import random
from datetime import timedelta

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from apps.authentication.models import User
from apps.order.models import Order, OrderItem
from apps.product.models import Cart, CartItem, Favourite, Product

DEMO_PREFIX = "+99891999"

FIRST = [
    "Jasur",
    "Dilshod",
    "Aziz",
    "Bekzod",
    "Sardor",
    "Otabek",
    "Rustam",
    "Timur",
    "Javlon",
    "Sherzod",
    "Nodir",
    "Farhod",
    "Ulugbek",
    "Aziza",
    "Madina",
    "Nilufar",
    "Gulnora",
    "Dilnoza",
    "Sevara",
    "Malika",
]
LAST = [
    "Karimov",
    "Rahimov",
    "Tursunov",
    "Aliyev",
    "Yusupov",
    "Ismoilov",
    "Abdullayev",
    "Normatov",
    "Qodirov",
    "Saidov",
    "Xolmatov",
    "Mirzayev",
    "Hamidov",
    "Nazarov",
    "Sobirov",
]
COMPANIES = [
    "Qurilish Invest",
    "Temir Yo'l Servis",
    "Texno Mashina",
    "Oltin Vodiy Agro",
    "Sanoat Plus",
    "Mega Stroy",
    "Ustaxona №1",
    "Zavod Ta'minot",
    "Metall Trade",
    "Neft Ehtiyot",
]


class Command(BaseCommand):
    help = "Seed demo buyers, orders, carts and stock levels for the admin dashboard."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete the demo buyers (and their orders/carts) first.",
        )
        parser.add_argument(
            "--adjust-products",
            action="store_true",
            help="Also reset stock levels and creation dates of the products, so the "
            "low stock and not selling lists have something to show.",
        )
        parser.add_argument("--seed", type=int, default=7)

    def handle(self, *args, **options):
        demo = User.objects.filter(phone_number__startswith=DEMO_PREFIX)
        if options["reset"]:
            self.stdout.write(
                f"Removing {demo.count()} demo buyers with their orders and carts"
            )
            demo.delete()
        elif demo.exists():
            raise CommandError("Demo data already exists. Use --reset to rebuild it.")

        rng = random.Random(options["seed"])
        now = timezone.now()
        with transaction.atomic():
            buyers = self._buyers(rng, now)
            products = list(Product.objects.filter(is_active=True))
            rng.shuffle(products)
            sellers = products[:70]  # the ones that actually sell
            if options["adjust_products"]:
                self._adjust_products(rng, now, sellers, products[70:])
            orders = self._orders(rng, now, buyers, sellers)
            self._carts(rng, now, buyers, sellers)
            self._favourites(rng, buyers)
        self.stdout.write(
            self.style.SUCCESS(f"Done: {len(buyers)} buyers, {orders} orders")
        )

    def _buyers(self, rng, now):
        buyers = []
        for i in range(48):
            # Most of the base joined over the year, a handful in the last week.
            days_ago = rng.randint(0, 6) if i < 6 else int(rng.random() ** 0.8 * 360)
            user = User.objects.create(
                full_name=f"{rng.choice(FIRST)} {rng.choice(LAST)}"
                if i % 3
                else rng.choice(COMPANIES) + f" {i}",
                phone_number=f"{DEMO_PREFIX}{i:04d}",
                role=User.Roles.BUYER,
                is_verified=True,
            )
            joined = now - timedelta(days=days_ago, hours=rng.randint(0, 20))
            User.objects.filter(id=user.id).update(created_at=joined)
            user.created_at = joined
            buyers.append(user)
        return buyers

    def _orders(self, rng, now, buyers, sellers):
        weights = [1 / (rank + 1) ** 0.9 for rank in range(len(sellers))]
        activity = {b.id: rng.choice([1, 1, 2, 3, 6]) for b in buyers}
        total = 0
        for day in range(364, -1, -1):
            when = now - timedelta(days=day)
            progress = 1 - day / 365
            expected = (0.25 + 2.4 * progress**1.6) * (
                0.55 if when.weekday() >= 5 else 1.0
            )
            count = sum(1 for _ in range(6) if rng.random() < expected / 6)
            for _ in range(count):
                joined = [b for b in buyers if b.created_at <= when]
                if not joined:
                    continue
                buyer = rng.choices(joined, weights=[activity[b.id] for b in joined])[0]
                created = when.replace(
                    hour=rng.randint(8, 20), minute=rng.randint(0, 59)
                )
                order = Order.objects.create(buyer=buyer)
                for product in rng.choices(
                    sellers, weights=weights, k=rng.choice([1, 1, 2, 2, 3, 4, 5])
                ):
                    if OrderItem.objects.filter(order=order, product=product).exists():
                        continue
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=rng.choice([1, 1, 2, 3, 5, 10, 20]),
                    )
                order.save()
                Order.objects.filter(id=order.id).update(created_at=created)
                OrderItem.objects.filter(order=order).update(created_at=created)
                total += 1
        return total

    def _carts(self, rng, now, buyers, sellers):
        def fill(cart, hours_ago):
            stamp = now - timedelta(hours=hours_ago)
            for product in rng.sample(sellers, rng.randint(1, 4)):
                item = CartItem.objects.create(
                    cart=cart, product=product, quantity=rng.choice([1, 2, 5, 10])
                )
                CartItem.objects.filter(id=item.id).update(
                    created_at=stamp, updated_at=stamp
                )

        for buyer in rng.sample(buyers, 10):  # abandoned: untouched for 1-6 days
            fill(Cart.objects.create(user=buyer), rng.randint(26, 140))
        for i in range(4):
            fill(
                Cart.objects.create(session_key=f"demo-guest-{i}"), rng.randint(30, 200)
            )
        for buyer in rng.sample(buyers, 2):  # still warm, must not count as abandoned
            fill(Cart.objects.create(user=buyer), rng.randint(1, 6))

    def _favourites(self, rng, buyers):
        for buyer in rng.sample(buyers, 25):
            for product in rng.sample(
                list(Product.objects.filter(is_active=True)[:120]), rng.randint(1, 4)
            ):
                Favourite.objects.get_or_create(user=buyer, product=product)

    def _adjust_products(self, rng, now, sellers, others):
        def update(products, **fields):
            for product in products:
                Product.objects.filter(id=product.id).update(**fields)

        # The shop must be older than 90 days, or "not selling" can never show anything.
        for product in sellers + others:
            Product.objects.filter(id=product.id).update(
                created_at=now - timedelta(days=rng.randint(120, 330)),
                stock_quantity=rng.randint(15, 400),
            )
        for product in sellers[:9]:  # best sellers running low
            update([product], stock_quantity=rng.randint(1, 5))
        update(sellers[9:13], stock_quantity=0)
        for product in others[:5]:
            update([product], stock_quantity=rng.randint(1, 5))
        update(others[5:8], stock_quantity=0)
