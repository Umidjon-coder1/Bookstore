from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Payment, Coupon
from .serializers import PaymentSerializer, CouponSerializer, ApplyCouponSerializer


class PaymentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_number):
        from apps.orders.models import Order
        order = Order.objects.filter(order_number=order_number, user=request.user).first()
        if not order:
            return Response({'error': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)
        payment = Payment.objects.filter(order=order).first()
        if not payment:
            return Response({'error': 'No payment found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(PaymentSerializer(payment).data)


class ApplyCouponAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ApplyCouponSerializer(data=request.data)
        if serializer.is_valid():
            code = serializer.validated_data['code']
            order_total = serializer.validated_data['order_total']
            coupon = Coupon.objects.filter(code=code).first()
            if not coupon or not coupon.is_valid():
                return Response({'error': 'Invalid or expired coupon.'}, status=status.HTTP_400_BAD_REQUEST)
            discount = coupon.get_discount_amount(order_total)
            return Response({'discount': discount, 'coupon': CouponSerializer(coupon).data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
