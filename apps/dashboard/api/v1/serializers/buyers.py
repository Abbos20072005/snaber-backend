from rest_framework import serializers


class BuyerKpiSerializer(serializers.Serializer):
    total_orders = serializers.IntegerField()
    estimated_spend = serializers.DecimalField(max_digits=20, decimal_places=2)


class BuyerPurchaseMomentumSerializer(serializers.Serializer):
    month = serializers.DateTimeField()
    orders = serializers.IntegerField()
    spend = serializers.DecimalField(max_digits=20, decimal_places=2)


class BuyerRecentActivitySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    product = serializers.CharField(source="product_name", allow_null=True)
    quantity = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=20, decimal_places=2)
    date = serializers.DateTimeField(source="created_at")

