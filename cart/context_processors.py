from .cart import Cart

def cart(request):
    """
    Context processor that adds the cart to the template context.
    """
    return {'cart': Cart(request)} 