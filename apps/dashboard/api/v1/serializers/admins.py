from rest_framework import serializers


class TodayOrdersCountSerializer(serializers.Serializer):
    orders_count = serializers.IntegerField()


class Last30DaysStatsSerializer(serializers.Serializer):
    total_spent = serializers.DecimalField(max_digits=20, decimal_places=2)
    orders_count = serializers.IntegerField()
    total_users_count = serializers.IntegerField()


class UserCountsSerializer(serializers.Serializer):
    buyers = serializers.IntegerField()
    admins = serializers.IntegerField()
    total_users = serializers.IntegerField()


class WeeklyJoinedUsersItemSerializer(serializers.Serializer):
    day = serializers.CharField()
    count = serializers.IntegerField()


class MonthlyRevenueItemSerializer(serializers.Serializer):
    month = serializers.CharField()
    total = serializers.DecimalField(max_digits=20, decimal_places=2)


class OrdersCountByCategorySerializer(serializers.Serializer):
    category_name = serializers.CharField()
    orders_count = serializers.IntegerField()


class TopProductByOrdersSerializer(serializers.Serializer):
    product_name = serializers.CharField()
    orders_count = serializers.IntegerField()
    orders_total = serializers.DecimalField(max_digits=20, decimal_places=2)
