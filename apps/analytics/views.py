from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.db.models import Sum, Count, Avg
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import timedelta
import json
from apps.orders.models import Order
from apps.books.models import Book
from apps.users.models import CustomUser
from .models import BookView, SalesReport


@method_decorator(login_required, name='dispatch')
class DashboardView(View):
    def get(self, request):
        if not (request.user.is_super_admin or request.user.is_store_manager):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied

        now = timezone.now()
        thirty_days_ago = now - timedelta(days=30)

        total_books = Book.objects.filter(is_active=True).count()
        total_users = CustomUser.objects.count()
        total_orders = Order.objects.count()
        total_revenue = Order.objects.filter(payment_status='paid').aggregate(Sum('total'))['total__sum'] or 0
        recent_orders = Order.objects.select_related('user').order_by('-created_at')[:10]
        low_stock_books = Book.objects.filter(stock_status__in=['low_stock', 'out_of_stock'])[:10]

        monthly_revenue = (
            Order.objects.filter(payment_status='paid', created_at__gte=thirty_days_ago)
            .annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(revenue=Sum('total'), orders=Count('id'))
            .order_by('month')
        )
        revenue_labels = [str(r['month'].strftime('%b %Y')) for r in monthly_revenue]
        revenue_data = [float(r['revenue']) for r in monthly_revenue]

        top_books = (
            Book.objects.annotate(order_count=Count('orderitem'))
            .order_by('-order_count')[:5]
        )

        context = {
            'total_books': total_books,
            'total_users': total_users,
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'recent_orders': recent_orders,
            'low_stock_books': low_stock_books,
            'revenue_labels': json.dumps(revenue_labels),
            'revenue_data': json.dumps(revenue_data),
            'top_books': top_books,
        }
        return render(request, 'dashboard/index.html', context)


@method_decorator(login_required, name='dispatch')
class DashboardBooksView(View):
    def get(self, request):
        if not (request.user.is_super_admin or request.user.is_store_manager):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied
        books = Book.objects.select_related('author', 'category').order_by('-created_at')
        return render(request, 'dashboard/books.html', {'books': books})


@method_decorator(login_required, name='dispatch')
class DashboardUsersView(View):
    def get(self, request):
        if not request.user.is_super_admin:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied
        users = CustomUser.objects.order_by('-created_at')
        return render(request, 'dashboard/users.html', {'users': users})


@method_decorator(login_required, name='dispatch')
class DashboardOrdersView(View):
    def get(self, request):
        if not (request.user.is_super_admin or request.user.is_store_manager):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied
        orders = Order.objects.select_related('user', 'shipping_address').order_by('-created_at')
        return render(request, 'dashboard/orders.html', {'orders': orders})

    def post(self, request):
        if not (request.user.is_super_admin or request.user.is_store_manager):
            from django.http import JsonResponse
            return JsonResponse({'error': 'Permission denied'}, status=403)
        from django.http import JsonResponse
        order_id = request.POST.get('order_id')
        new_status = request.POST.get('status')
        try:
            order = Order.objects.get(pk=order_id)
            order.status = new_status
            order.save()
            return JsonResponse({'success': True})
        except Order.DoesNotExist:
            return JsonResponse({'error': 'Order not found'}, status=404)
