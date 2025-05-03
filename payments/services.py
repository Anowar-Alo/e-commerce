import stripe
from django.conf import settings
from django.core.exceptions import ValidationError
from .models import PaymentMethod, Transaction

stripe.api_key = settings.STRIPE_SECRET_KEY

class PaymentService:
    @staticmethod
    def create_payment_method(user, payment_type, token):
        """Create a new payment method for a user."""
        try:
            # Create Stripe payment method
            stripe_payment_method = stripe.PaymentMethod.create(
                type=payment_type,
                card=token if payment_type == 'card' else None,
                billing_details={
                    'email': user.email,
                    'name': user.get_full_name() or user.username,
                }
            )
            
            # Create local payment method
            payment_method = PaymentMethod.objects.create(
                user=user,
                type=payment_type,
                provider='stripe',
                token=stripe_payment_method.id,
                is_default=not user.payment_methods.exists(),
            )
            
            # Attach payment method to customer
            customer = PaymentService.get_or_create_customer(user)
            stripe.PaymentMethod.attach(
                stripe_payment_method.id,
                customer=customer.id,
            )
            
            return payment_method
            
        except stripe.error.StripeError as e:
            raise ValidationError(str(e))
    
    @staticmethod
    def get_or_create_customer(user):
        """Get or create a Stripe customer for a user."""
        try:
            # Check if user already has a Stripe customer ID
            if user.stripe_customer_id:
                return stripe.Customer.retrieve(user.stripe_customer_id)
            
            # Create new Stripe customer
            customer = stripe.Customer.create(
                email=user.email,
                name=user.get_full_name() or user.username,
                metadata={
                    'user_id': user.id,
                }
            )
            
            # Save Stripe customer ID to user
            user.stripe_customer_id = customer.id
            user.save()
            
            return customer
            
        except stripe.error.StripeError as e:
            raise ValidationError(str(e))
    
    @staticmethod
    def create_payment_intent(amount, currency, payment_method_id=None, customer_id=None):
        """Create a payment intent for processing a payment."""
        try:
            intent_data = {
                'amount': int(amount * 100),  # Convert to cents
                'currency': currency,
                'automatic_payment_methods': {
                    'enabled': True,
                },
            }
            
            if payment_method_id:
                intent_data['payment_method'] = payment_method_id
            
            if customer_id:
                intent_data['customer'] = customer_id
            
            return stripe.PaymentIntent.create(**intent_data)
            
        except stripe.error.StripeError as e:
            raise ValidationError(str(e))
    
    @staticmethod
    def confirm_payment_intent(payment_intent_id):
        """Confirm a payment intent."""
        try:
            return stripe.PaymentIntent.confirm(payment_intent_id)
        except stripe.error.StripeError as e:
            raise ValidationError(str(e))
    
    @staticmethod
    def create_transaction(order, payment_intent):
        """Create a transaction record from a payment intent."""
        try:
            transaction = Transaction.objects.create(
                order=order,
                payment_method=PaymentMethod.objects.get(token=payment_intent.payment_method),
                transaction_id=payment_intent.id,
                amount=payment_intent.amount / 100,  # Convert from cents
                currency=payment_intent.currency,
                status=payment_intent.status,
                type='payment',
                provider='stripe',
                provider_transaction_id=payment_intent.id,
                provider_status=payment_intent.status,
                provider_response=payment_intent.to_dict(),
            )
            
            return transaction
            
        except stripe.error.StripeError as e:
            raise ValidationError(str(e))
    
    @staticmethod
    def refund_transaction(transaction, amount=None):
        """Refund a transaction."""
        try:
            refund = stripe.Refund.create(
                payment_intent=transaction.provider_transaction_id,
                amount=int(amount * 100) if amount else None,
            )
            
            # Create refund transaction
            refund_transaction = Transaction.objects.create(
                order=transaction.order,
                payment_method=transaction.payment_method,
                transaction_id=refund.id,
                amount=refund.amount / 100,
                currency=refund.currency,
                status=refund.status,
                type='refund',
                provider='stripe',
                provider_transaction_id=refund.id,
                provider_status=refund.status,
                provider_response=refund.to_dict(),
            )
            
            return refund_transaction
            
        except stripe.error.StripeError as e:
            raise ValidationError(str(e)) 