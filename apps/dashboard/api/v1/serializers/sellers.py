from rest_framework import serializers


class HeroSummarySerializer(serializers.Serializer):
    monthly_growth = serializers.FloatField()
    # Chat center (unread chats metric) is disabled for the frontend
    # unread_buyer_chats = serializers.IntegerField()
    dispatch_due_today = serializers.IntegerField()


class KpiSerializer(serializers.Serializer):
    value = serializers.FloatField()
    delta = serializers.FloatField()


class RevenueMomentumSerializer(serializers.Serializer):
    month = serializers.CharField()
    revenue = serializers.FloatField()
    orders = serializers.IntegerField()
    quotes = serializers.IntegerField()


class SalesByCategorySerializer(serializers.Serializer):
    category_name = serializers.CharField()
    category_name_uz = serializers.CharField()
    category_name_ru = serializers.CharField()
    category_name_en = serializers.CharField()
    orders_count = serializers.IntegerField()


# Chat center (buyer engagement metric) is disabled for the frontend
# class BuyerEngagementSerializer(serializers.Serializer):
#     day = serializers.CharField()
#     views = serializers.IntegerField()
#     chats = serializers.IntegerField()


class TopProductSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(source="id")
    product = serializers.CharField(source="name")
    sku = serializers.CharField(allow_null=True, allow_blank=True)
    orders = serializers.IntegerField(source="orders_count", default=0)
    revenue = serializers.FloatField(default=0)
    stock_health = serializers.SerializerMethodField()

    def get_stock_health(self, obj):
        return min(100, int(obj.stock or 0))


class RecentOrderSerializer(serializers.Serializer):
    buyer = serializers.CharField(source="buyer.full_name", default="")
    order = serializers.CharField(source="id")
    amount = serializers.FloatField(source="total_price", default=0)
    status = serializers.CharField()


class RfqPipelineSerializer(serializers.Serializer):
    negotiation = serializers.IntegerField(default=0)
    accepted = serializers.IntegerField(default=0)
    rejected = serializers.IntegerField(default=0)

