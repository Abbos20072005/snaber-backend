from rest_framework import serializers


class TodayOrdersCountSerializer(serializers.Serializer):
    orders_count = serializers.IntegerField()
    rfq_orders_count = serializers.IntegerField()


class Last30DaysStatsSerializer(serializers.Serializer):
    total_spent = serializers.DecimalField(max_digits=20, decimal_places=2)
    orders_count = serializers.IntegerField()
    verified_sellers_count = serializers.IntegerField()
    total_users_count = serializers.IntegerField()


class UserCountsSerializer(serializers.Serializer):
    sellers = serializers.IntegerField()
    buyers = serializers.IntegerField()
    moderators = serializers.IntegerField(required=False)
    admins = serializers.IntegerField(required=False)
    total_users = serializers.IntegerField()


class WeeklyJoinedUsersItemSerializer(serializers.Serializer):
    day = serializers.CharField()
    count = serializers.IntegerField()


class RFQOrderStatusCountSerializer(serializers.Serializer):
    negotiation = serializers.IntegerField()
    accepted = serializers.IntegerField()
    rejected = serializers.IntegerField()


class MonthlyRevenueItemSerializer(serializers.Serializer):
    month = serializers.CharField()
    total = serializers.DecimalField(max_digits=20, decimal_places=2)


class OrdersCountByCategorySerializer(serializers.Serializer):
    category_name = serializers.CharField()
    orders_count = serializers.IntegerField()


class TopCompanyByOrdersSerializer(serializers.Serializer):
    company_name = serializers.CharField()
    orders_count = serializers.IntegerField()
    orders_total = serializers.DecimalField(max_digits=20, decimal_places=2)
