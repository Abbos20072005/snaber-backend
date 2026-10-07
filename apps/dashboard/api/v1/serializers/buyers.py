from rest_framework import serializers


class BuyerKpiSerializer(serializers.Serializer):
    total_orders = serializers.IntegerField()
    active_orders = serializers.IntegerField()
    rfq_orders = serializers.IntegerField()
    estimated_spend = serializers.DecimalField(max_digits=20, decimal_places=2)


class BuyerPurchaseMomentumSerializer(serializers.Serializer):
    month = serializers.DateTimeField()
    orders = serializers.IntegerField()
    spend = serializers.DecimalField(max_digits=20, decimal_places=2)


class BuyerStatusMixSerializer(serializers.Serializer):
    status = serializers.CharField()
    count = serializers.IntegerField()


class BuyerOrderTypeSplitSerializer(serializers.Serializer):
    type = serializers.CharField()
    count = serializers.IntegerField()


class BuyerRecentActivitySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    product = serializers.CharField(source="product_name", allow_null=True)
    type = serializers.CharField(source="product_type", allow_null=True)
    quantity = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=20, decimal_places=2)
    status = serializers.CharField()
    date = serializers.DateTimeField(source="created_at")


class BuyerSummarySerializer(serializers.Serializer):
    acceptance_rate = serializers.FloatField()
    orders_in_progress = serializers.IntegerField()
    custom_requests = serializers.IntegerField()
