from rest_framework import serializers
from .models import Payment, Coupon


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class CouponSerializer(serializers.ModelSerializer):
    is_valid_now = serializers.SerializerMethodField()

    class Meta:
        model = Coupon
        fields = ('id', 'code', 'discount_type', 'discount_value', 'min_order_amount', 'is_valid_now')

    def get_is_valid_now(self, obj):
        return obj.is_valid()


class ApplyCouponSerializer(serializers.Serializer):
    code = serializers.CharField()
    order_total = serializers.DecimalField(max_digits=12, decimal_places=2)
