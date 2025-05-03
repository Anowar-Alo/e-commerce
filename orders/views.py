from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from cart.cart import Cart
from .models import Order, OrderItem
from products.models import Product
import uuid

# Create your views here 

@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/order_list.html', {'orders': orders})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/detail.html', {'order': order})

@login_required
def order_create(request):
    cart = Cart(request)
    if not cart:
        messages.warning(request, 'Your cart is empty.')
        return redirect('cart:cart_detail')
    
    if request.method == 'POST':
        try:
            # Create order
            order = Order.objects.create(
                user=request.user,
                email=request.user.email,
                order_number=str(uuid.uuid4().hex[:16]),
                status='pending',
                payment_status='pending',
                
                # Shipping information
                shipping_name=request.user.get_full_name() or request.user.username,
                shipping_email=request.user.email,
                shipping_phone=request.POST.get('phone_number', ''),
                shipping_address=request.POST.get('shipping_address', ''),
                shipping_city='',  # Not collected in form
                shipping_state='',  # Not collected in form
                shipping_country='',  # Not collected in form
                shipping_postal_code='',  # Not collected in form
                
                # Billing information (same as shipping for now)
                billing_name=request.user.get_full_name() or request.user.username,
                billing_email=request.user.email,
                billing_phone=request.POST.get('phone_number', ''),
                billing_address=request.POST.get('shipping_address', ''),
                billing_city='',  # Not collected in form
                billing_state='',  # Not collected in form
                billing_country='',  # Not collected in form
                billing_postal_code='',  # Not collected in form
                
                # Amounts
                subtotal=cart.get_total_price(),
                shipping_cost=0,  # Free shipping for now
                tax=0,  # No tax for now
                total=cart.get_total_price(),
                
                # Payment information
                payment_method=request.POST.get('payment_method', 'cash'),
                notes=request.POST.get('notes', ''),
            )
            
            # Create order items
            for item in cart:
                product = get_object_or_404(Product, id=item['product_id'])
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=product.name,
                    sku=product.sku,
                    unit_price=item['price'],
                    quantity=item['quantity'],
                    total_price=item['total_price'],
                    product_data={
                        'name': product.name,
                        'description': product.description,
                        'price': str(product.price),
                        'image': product.image.url if product.image else None,
                    }
                )
            
            # Clear the cart
            cart.clear()
            
            # If it's an AJAX request, return success
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            
            # Otherwise, redirect to order list
            messages.success(request, 'Order created successfully.')
            return redirect('orders:order_list')
            
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'error': str(e)}, status=400)
            messages.error(request, f'Error creating order: {str(e)}')
            return redirect('cart:cart_detail')
    
    return render(request, 'orders/create.html', {
        'cart': cart,
    }) 