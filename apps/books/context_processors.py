from .models import Category


def global_context(request):
    nav_categories = list(
        Category.objects.filter(is_active=True, parent=None)
        .prefetch_related('children')
        .order_by('name')[:12]
    )

    cart_count = 0
    try:
        if request.user.is_authenticated:
            from apps.cart.models import Cart
            cart = Cart.objects.filter(user=request.user).first()
        else:
            sk = request.session.session_key
            cart = None
            if sk:
                from apps.cart.models import Cart
                cart = Cart.objects.filter(session_key=sk, user=None).first()
        if cart:
            cart_count = cart.items.count()
    except Exception:
        pass

    rating_choices = [
        ('4', '& Up'),
        ('3', '& Up'),
        ('2', '& Up'),
        ('1', '& Up'),
    ]

    return {
        'nav_categories': nav_categories,
        'cart_count': cart_count,
        'rating_choices': rating_choices,
    }
