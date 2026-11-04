from rest_framework import serializers

_MONEY = {"max_digits": 20, "decimal_places": 2}


class KpiSerializer(serializers.Serializer):
    revenue = serializers.DecimalField(**_MONEY)
    orders_count = serializers.IntegerField()
    average_order_value = serializers.DecimalField(**_MONEY)
    units_sold = serializers.IntegerField()
    new_users = serializers.IntegerField()
    active_buyers = serializers.IntegerField()
    returning_buyers = serializers.IntegerField()


class DailyPointSerializer(serializers.Serializer):
    date = serializers.DateField()
    revenue = serializers.DecimalField(**_MONEY)
    orders_count = serializers.IntegerField()


class OverviewSerializer(serializers.Serializer):
    period = serializers.CharField()
    days = serializers.IntegerField()
    start = serializers.DateField()
    end = serializers.DateField()
    previous_start = serializers.DateField()
    previous_end = serializers.DateField()
    current = KpiSerializer()
    previous = KpiSerializer()
    daily = DailyPointSerializer(many=True)


class AbandonedCartSerializer(serializers.Serializer):
    customer = serializers.CharField(allow_blank=True)
    phone_number = serializers.CharField(allow_blank=True)
    is_guest = serializers.BooleanField()
    items_count = serializers.IntegerField()
    total = serializers.DecimalField(**_MONEY)
    last_activity = serializers.DateTimeField()


class AbandonedCartsSerializer(serializers.Serializer):
    after_hours = serializers.IntegerField()
    carts_count = serializers.IntegerField()
    total_value = serializers.DecimalField(**_MONEY)
    top = AbandonedCartSerializer(many=True)


class StockProductSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    sku = serializers.CharField(allow_blank=True)
    stock_quantity = serializers.IntegerField()
    stock_value = serializers.DecimalField(required=False, **_MONEY)


class StockAlertsSerializer(serializers.Serializer):
    low_stock_threshold = serializers.IntegerField()
    dead_stock_days = serializers.IntegerField()
    low_stock_count = serializers.IntegerField()
    out_of_stock_count = serializers.IntegerField()
    dead_stock_count = serializers.IntegerField()
    dead_stock_value = serializers.DecimalField(**_MONEY)
    low_stock = StockProductSerializer(many=True)
    out_of_stock = StockProductSerializer(many=True)
    dead_stock = StockProductSerializer(many=True)
