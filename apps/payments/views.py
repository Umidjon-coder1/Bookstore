from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
from .models import Payment, Coupon
from apps.orders.models import Order
import json


@method_decorator(login_required, name='dispatch')
class PaymentView(View):
    def get(self, request, order_number):
        order = get_object_or_404(Order, order_number=order_number, user=request.user)
        return render(request, 'payments/payment.html', {
            'order': order,
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
        })

    def post(self, request, order_number):
        order = get_object_or_404(Order, order_number=order_number, user=request.user)
        payment_method = request.POST.get('payment_method', 'cod')

        if payment_method == 'stripe':
            from .gateways.stripe_gateway import StripeGateway
            gateway = StripeGateway()
            result = gateway.create_payment(order, order.total)
            if result['success']:
                Payment.objects.get_or_create(
                    order=order,
                    defaults={
                        'payment_method': 'stripe',
                        'amount': order.total,
                        'stripe_payment_intent_id': result['payment_intent_id'],
                    }
                )
                return render(request, 'payments/payment.html', {
                    'order': order,
                    'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
                    'client_secret': result['client_secret'],
                })
        elif payment_method == 'cod':
            Payment.objects.get_or_create(
                order=order,
                defaults={'payment_method': 'cod', 'amount': order.total, 'status': 'pending'}
            )
            order.payment_method = 'cod'
            order.status = Order.Status.CONFIRMED
            order.save()
            messages.success(request, 'Buyurtma naqd pul orqali tasdiqlandi!')
            return redirect('payments:success', order_number=order_number)

        return redirect('payments:payment', order_number=order_number)


@method_decorator(login_required, name='dispatch')
class PaymentSuccessView(View):
    def get(self, request, order_number):
        order = get_object_or_404(Order, order_number=order_number, user=request.user)
        return render(request, 'payments/success.html', {'order': order})


class ApplyCouponView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            code = data.get('code', '').strip()
        except Exception:
            code = request.POST.get('code', '').strip()

        if not code:
            return JsonResponse({'success': False, 'message': 'Kupon kodi kiritilmagan'})

        coupon = Coupon.objects.filter(code=code).first()
        if not coupon or not coupon.is_valid():
            return JsonResponse({'success': False, 'message': 'Kupon kodi noto\'g\'ri yoki muddati o\'tgan'})

        request.session['coupon_code'] = code
        from apps.cart.views import get_or_create_cart
        cart = get_or_create_cart(request)
        discount = coupon.get_discount_amount(cart.subtotal)
        return JsonResponse({
            'success': True,
            'discount': str(discount),
            'coupon_code': code,
            'message': f'Kupon qo\'llanildi! {discount} so\'m chegirma'
        })


def stripe_webhook(request):
    import stripe
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
        if event['type'] == 'payment_intent.succeeded':
            intent = event['data']['object']
            payment = Payment.objects.filter(stripe_payment_intent_id=intent['id']).first()
            if payment:
                payment.status = Payment.Status.PAID
                payment.transaction_id = intent['id']
                payment.save()
                payment.order.payment_status = 'paid'
                payment.order.status = Order.Status.CONFIRMED
                payment.order.save()
    except Exception:
        return HttpResponse(status=400)
    return HttpResponse(status=200)
