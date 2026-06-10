import stripe
from django.conf import settings
from .base import BasePaymentGateway


class StripeGateway(BasePaymentGateway):
    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY

    def create_payment(self, order, amount):
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # cents
                currency='usd',
                metadata={
                    'order_number': order.order_number,
                    'user_id': str(order.user.id),
                },
                description=f"Order {order.order_number}",
            )
            return {
                'success': True,
                'payment_intent_id': intent.id,
                'client_secret': intent.client_secret,
            }
        except stripe.error.StripeError as e:
            return {'success': False, 'error': str(e)}

    def confirm_payment(self, payment_id):
        try:
            intent = stripe.PaymentIntent.retrieve(payment_id)
            if intent.status == 'succeeded':
                return {'success': True, 'status': 'paid'}
            return {'success': False, 'status': intent.status}
        except stripe.error.StripeError as e:
            return {'success': False, 'error': str(e)}

    def refund_payment(self, payment_id, amount=None):
        try:
            params = {'payment_intent': payment_id}
            if amount:
                params['amount'] = int(amount * 100)
            refund = stripe.Refund.create(**params)
            return {'success': True, 'refund_id': refund.id}
        except stripe.error.StripeError as e:
            return {'success': False, 'error': str(e)}

    def get_payment_status(self, payment_id):
        try:
            intent = stripe.PaymentIntent.retrieve(payment_id)
            return {'success': True, 'status': intent.status}
        except stripe.error.StripeError as e:
            return {'success': False, 'error': str(e)}
