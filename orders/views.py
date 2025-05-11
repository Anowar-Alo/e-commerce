from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from cart.cart import Cart
from .models import Order, OrderItem, OrderStatusUpdate
from products.models import Product
from core.models import Dashboard
from django.utils import timezone
from django.db import transaction
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
            with transaction.atomic():
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
                    shipping_city='',  # Default empty
                    shipping_state='',  # Default empty
                    shipping_country='',  # Default empty
                    shipping_postal_code='',  # Default empty
                    
                    # Billing information (same as shipping for now)
                    billing_name=request.user.get_full_name() or request.user.username,
                    billing_email=request.user.email,
                    billing_phone=request.POST.get('phone_number', ''),
                    billing_address=request.POST.get('shipping_address', ''),
                    billing_city='',  # Default empty
                    billing_state='',  # Default empty
                    billing_country='',  # Default empty
                    billing_postal_code='',  # Default empty
                    
                    # Amounts
                    subtotal=cart.get_total_price(),
                    shipping_cost=0,  # Free shipping for now
                    tax=0,  # No tax for now
                    total=cart.get_total_price(),
                    
                    # Shipping method (default to standard)
                    shipping_method='standard',
                    
                    # Payment information
                    payment_method=request.POST.get('payment_method', 'cash'),
                    customer_notes=request.POST.get('notes', '')
                )
                
                # Create order items
                for item in cart:
                    if 'product' in item:
                        product = item['product']
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

@login_required
def order_update(request, order_id):
    """Update order status and create status update record."""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to update orders.')
        return redirect('orders:order_list')
    
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        notes = request.POST.get('notes', '')
        
        if new_status in dict(Order.STATUS_CHOICES):
            # Update order status
            order.status = new_status
            
            # Update timestamps based on status
            if new_status == 'shipped':
                order.shipped_at = timezone.now()
            elif new_status == 'delivered':
                order.delivered_at = timezone.now()
            
            order.save()
            
            # Create status update record
            OrderStatusUpdate.objects.create(
                order=order,
                status=new_status,
                notes=notes,
                created_by=request.user
            )
            
            # Update dashboard metrics
            dashboard = Dashboard.objects.first()
            if dashboard:
                dashboard.update_metrics()
            
            messages.success(request, f'Order status updated to {new_status}.')
        else:
            messages.error(request, 'Invalid status provided.')
    
    return redirect('admin:orders_order_change', order_id)

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if not order.can_cancel:
        messages.error(request, 'This order cannot be cancelled.')
        return redirect('orders:order_list')
    
    try:
        with transaction.atomic():
            # Update order status
            order.status = 'cancelled'
            order.save()
            
            # Create status update record
            OrderStatusUpdate.objects.create(
                order=order,
                status='cancelled',
                notes='Order cancelled by customer',
                created_by=request.user
            )
            
            # Restore product stock
            order.restore_product_stock()
            
            messages.success(request, 'Order cancelled successfully.')
    except Exception as e:
        messages.error(request, f'Error cancelling order: {str(e)}')
    
    return redirect('orders:order_list') 