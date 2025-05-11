from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from products.models import Product
from .cart import Cart
from .forms import CartAddProductForm

def cart_detail(request):
    cart = Cart(request)
    for item in cart:
        item['update_quantity_form'] = CartAddProductForm(
            initial={'quantity': item['quantity'],
                    'update': True})
    return render(request, 'cart/detail.html', {'cart': cart})

@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    
    # Check if product is in stock
    if product.stock <= 0:
        messages.error(request, f'Sorry, {product.name} is out of stock.')
        return redirect('cart:cart_detail')
    
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        quantity = cd['quantity']
        
        # Check if requested quantity is available
        if quantity > product.stock:
            messages.error(request, f'Sorry, only {product.stock} units of {product.name} are available.')
            return redirect('cart:cart_detail')
        
        cart.add(product=product,
                quantity=quantity,
                update_quantity=cd['update'])
        messages.success(request, f'{product.name} added to cart.')
    return redirect('cart:cart_detail')

def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    messages.success(request, f'{product.name} removed from cart.')
    return redirect('cart:cart_detail')

@require_POST
def cart_update(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    
    # Check if product is in stock
    if product.stock <= 0:
        messages.error(request, f'Sorry, {product.name} is out of stock.')
        return redirect('cart:cart_detail')
    
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        quantity = cd['quantity']
        
        # Check if requested quantity is available
        if quantity > product.stock:
            messages.error(request, f'Sorry, only {product.stock} units of {product.name} are available.')
            return redirect('cart:cart_detail')
        
        cart.add(product=product,
                quantity=quantity,
                update_quantity=cd['update'])
        messages.success(request, f'Cart updated successfully.')
    return redirect('cart:cart_detail')

def cart_clear(request):
    cart = Cart(request)
    cart.clear()
    messages.success(request, 'Cart cleared.')
    return redirect('cart:cart_detail') 