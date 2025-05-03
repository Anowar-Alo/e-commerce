from django.shortcuts import render
import stripe
import json
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import PaymentMethod, Transaction
from .services import PaymentService
from orders.models import Order

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def payment_methods(request):
    """View for managing payment methods."""
    payment_methods = request.user.payment_methods.all()
    return render(request, 'payments/payment_methods.html', {
        'payment_methods': payment_methods,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
    })

@login_required
def create_payment_intent(request, order_id):
    """Create a payment intent for an order."""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    try:
        # Get or create Stripe customer
        customer = PaymentService.get_or_create_customer(request.user)
        
        # Create payment intent
        payment_intent = PaymentService.create_payment_intent(
            amount=order.total,
            currency=settings.CURRENCY,
            customer_id=customer.id,
        )
        
        return JsonResponse({
            'clientSecret': payment_intent.client_secret,
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
def stripe_webhook(request):
    """Handle Stripe webhooks."""
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)
    
    # Handle the event
    if event.type == 'payment_intent.succeeded':
        payment_intent = event.data.object
        try:
            order = Order.objects.get(stripe_payment_intent_id=payment_intent.id)
            transaction = PaymentService.create_transaction(order, payment_intent)
            order.status = 'paid'
            order.save()
        except Order.DoesNotExist:
            pass
    
    elif event.type == 'payment_intent.payment_failed':
        payment_intent = event.data.object
        try:
            order = Order.objects.get(stripe_payment_intent_id=payment_intent.id)
            order.status = 'payment_failed'
            order.save()
        except Order.DoesNotExist:
            pass
    
    return HttpResponse(status=200)

@login_required
def process_payment(request, order_id):
    """Process a payment for an order."""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if request.method == 'POST':
        try:
            payment_method_id = request.POST.get('payment_method_id')
            
            # Create payment intent
            payment_intent = PaymentService.create_payment_intent(
                amount=order.total,
                currency=settings.CURRENCY,
                payment_method_id=payment_method_id,
            )
            
            # Confirm payment intent
            confirmed_intent = PaymentService.confirm_payment_intent(payment_intent.id)
            
            # Create transaction
            transaction = PaymentService.create_transaction(order, confirmed_intent)
            
            # Update order status
            order.status = 'paid'
            order.stripe_payment_intent_id = payment_intent.id
            order.save()
            
            messages.success(request, 'Payment successful!')
            return redirect('orders:order_detail', order_id=order.id)
            
        except Exception as e:
            messages.error(request, str(e))
            return redirect('orders:checkout', order_id=order.id)
    
    return render(request, 'payments/process_payment.html', {
        'order': order,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
    }) 