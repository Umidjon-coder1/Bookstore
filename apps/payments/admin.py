from django.contrib import admin
from .models import Payment, Coupon


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'payment_method', 'status', 'amount', 'currency', 'created_at')
    list_filter = ('payment_method', 'status')
    search_fields = ('order__order_number', 'transaction_id')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'discount_value', 'used_count', 'max_uses', 'is_active', 'valid_until')
    list_filter = ('discount_type', 'is_active')
    search_fields = ('code',)
