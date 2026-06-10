import paypalrestsdk
from django.conf import settings
from .base import BasePaymentGateway


class PayPalGateway(BasePaymentGateway):
    def __init__(self):
        paypalrestsdk.configure({
            'mode': settings.PAYPAL_MODE,
            'client_id': settings.PAYPAL_CLIENT_ID,
            'client_secret': settings.PAYPAL_CLIENT_SECRET,
        })

    def create_payment(self, order, amount):
        try:
            payment = paypalrestsdk.Payment({
                'intent': 'sale',
                'payer': {'payment_method': 'paypal'},
                'redirect_urls': {
                    'return_url': f"{getattr(settings, 'SITE_URL', 'http://localhost:8000')}/payments/paypal/success/",
                    'cancel_url': f"{getattr(settings, 'SITE_URL', 'http://localhost:8000')}/payments/paypal/cancel/",
                },
                'transactions': [{
                    'amount': {'total': str(amount), 'currency': 'USD'},
                    'description': f"Order {order.order_number}",
                }],
            })
            if payment.create():
                approval_url = next(link.href for link in payment.links if link.rel == 'approval_url')
                return {'success': True, 'payment_id': payment.id, 'approval_url': approval_url}
            return {'success': False, 'error': payment.error}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def confirm_payment(self, payment_id, payer_id=None):
        try:
            payment = paypalrestsdk.Payment.find(payment_id)
            if payer_id and payment.execute({'payer_id': payer_id}):
                return {'success': True, 'status': 'paid'}
            return {'success': False, 'error': 'Payment execution failed'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def refund_payment(self, payment_id, amount=None):
        try:
            payment = paypalrestsdk.Payment.find(payment_id)
            sale_id = payment.transactions[0].related_resources[0].sale.id
            sale = paypalrestsdk.Sale.find(sale_id)
            refund_data = {}
            if amount:
                refund_data['amount'] = {'total': str(amount), 'currency': 'USD'}
            refund = sale.refund(refund_data)
            if refund.success():
                return {'success': True, 'refund_id': refund.id}
            return {'success': False, 'error': refund.error}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_payment_status(self, payment_id):
        try:
            payment = paypalrestsdk.Payment.find(payment_id)
            return {'success': True, 'status': payment.state}
        except Exception as e:
            return {'success': False, 'error': str(e)}
