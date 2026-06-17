from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views import View
from .models import Order, Address, OrderItem
from apps.cart.models import Cart
from apps.cart.views import get_or_create_cart


@method_decorator(login_required, name='dispatch')
class CheckoutView(View):
    def get(self, request):
        cart = get_or_create_cart(request)
        if not cart.items.exists():
            messages.warning(request, 'Savatingiz bo\'sh.')
            return redirect('cart:cart')
        addresses = Address.objects.filter(user=request.user)
        coupon_code = request.session.get('coupon_code', '')
        discount = Decimal('0')
        if coupon_code:
            from apps.payments.models import Coupon
            coupon = Coupon.objects.filter(code=coupon_code).first()
            if coupon and coupon.is_valid():
                discount = coupon.get_discount_amount(cart.subtotal)
        shipping = Decimal('0') if cart.subtotal >= Decimal('35000') else Decimal('5000')
        total = max(Decimal('0'), cart.subtotal + shipping - discount)
        return render(request, 'orders/checkout.html', {
            'cart': cart,
            'addresses': addresses,
            'coupon_code': coupon_code,
            'discount': discount,
            'shipping': shipping,
            'total': total,
        })

    def post(self, request):
        cart = get_or_create_cart(request)
        if not cart.items.exists():
            return redirect('cart:cart')

        address_id = request.POST.get('address_id')
        payment_method = request.POST.get('payment_method', 'cod')

        if address_id:
            address = get_object_or_404(Address, pk=address_id, user=request.user)
        else:
            address = Address.objects.create(
                user=request.user,
                full_name=request.POST.get('full_name', ''),
                phone=request.POST.get('phone', ''),
                address_line1=request.POST.get('address_line1', ''),
                city=request.POST.get('city', ''),
                country=request.POST.get('country', ''),
                postal_code=request.POST.get('postal_code', ''),
            )

        subtotal = cart.subtotal
        shipping_cost = Decimal('0') if subtotal >= Decimal('35000') else Decimal('5000')

        coupon_code = request.session.get('coupon_code', '')
        discount = Decimal('0')
        if coupon_code:
            from apps.payments.models import Coupon
            coupon = Coupon.objects.filter(code=coupon_code).first()
            if coupon and coupon.is_valid():
                discount = coupon.get_discount_amount(subtotal)

        order = Order.objects.create(
            user=request.user,
            shipping_address=address,
            payment_method=payment_method,
            subtotal=subtotal,
            shipping_cost=shipping_cost,
            tax=round(subtotal * Decimal('0.1'), 2),
            discount=discount,
        )

        for item in cart.items.select_related('book'):
            OrderItem.objects.create(
                order=order,
                book=item.book,
                quantity=item.quantity,
                price=item.book.final_price,
            )
            item.book.quantity -= item.quantity
            item.book.save()

        cart.items.all().delete()
        request.session.pop('coupon_code', None)

        messages.success(request, f'{order.order_number} raqamli buyurtma muvaffaqiyatli qabul qilindi!')
        return redirect('orders:detail', order_number=order.order_number)


@method_decorator(login_required, name='dispatch')
class OrderListView(View):
    def get(self, request):
        orders = Order.objects.filter(user=request.user).prefetch_related('items__book')
        return render(request, 'orders/list.html', {'orders': orders})


@method_decorator(login_required, name='dispatch')
class OrderDetailView(View):
    def get(self, request, order_number):
        order = get_object_or_404(Order, order_number=order_number, user=request.user)
        return render(request, 'orders/detail.html', {'order': order})
