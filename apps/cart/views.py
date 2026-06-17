from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views import View
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import Cart, CartItem
from apps.books.models import Book
import json


def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user, defaults={'session_key': ''})
    else:
        if not request.session.session_key:
            request.session.create()
        cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key, user=None)
    return cart


class CartView(View):
    def get(self, request):
        from decimal import Decimal
        cart = get_or_create_cart(request)
        coupon_code = request.session.get('coupon_code', '')
        discount = Decimal('0')
        if coupon_code:
            try:
                from apps.payments.models import Coupon
                coupon = Coupon.objects.filter(code=coupon_code).first()
                if coupon and coupon.is_valid():
                    discount = coupon.get_discount_amount(cart.subtotal)
                else:
                    request.session.pop('coupon_code', None)
                    coupon_code = ''
            except Exception:
                pass
        from decimal import Decimal as _D
        shipping = _D('0') if cart.subtotal >= _D('35000') else _D('5000')
        cart_total = max(_D('0'), cart.subtotal + shipping - discount)
        return render(request, 'cart/cart.html', {
            'cart': cart,
            'coupon_code': coupon_code,
            'discount': discount,
            'shipping': shipping,
            'cart_total': cart_total,
        })


class RemoveCouponView(View):
    def post(self, request):
        request.session.pop('coupon_code', None)
        return JsonResponse({'success': True})


class AddToCartView(View):
    def post(self, request, book_id):
        book = get_object_or_404(Book, pk=book_id, is_active=True)
        cart = get_or_create_cart(request)
        quantity = int(request.POST.get('quantity', 1))

        item, created = CartItem.objects.get_or_create(cart=cart, book=book)
        if not created:
            item.quantity += quantity
        else:
            item.quantity = quantity
        item.save()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'total_items': cart.total_items, 'message': f'{book.title} added to cart'})
        messages.success(request, f'{book.title} savatga qo\'shildi!')
        return redirect('cart:cart')


class RemoveFromCartView(View):
    def post(self, request, item_id):
        item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user if request.user.is_authenticated else None)
        item.delete()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            cart = get_or_create_cart(request)
            return JsonResponse({'success': True, 'total_items': cart.total_items, 'subtotal': str(cart.subtotal)})
        messages.success(request, 'Mahsulot savatdan o\'chirildi.')
        return redirect('cart:cart')


class UpdateCartView(View):
    def post(self, request, item_id):
        item = get_object_or_404(CartItem, pk=item_id)
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            item.quantity = quantity
            item.save()
        else:
            item.delete()
        cart = item.cart
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'total_items': cart.total_items, 'subtotal': str(cart.subtotal)})
        return redirect('cart:cart')
