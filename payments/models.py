from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords


class PaymentMethod(models.Model):
    TYPE_CHOICES = (
        ('card', _('Credit/Debit Card')),
        ('bank', _('Bank Account')),
        ('wallet', _('Digital Wallet')),
        ('upi', _('UPI')),
    )
    
    PROVIDER_CHOICES = (
        ('stripe', _('Stripe')),
        ('paypal', _('PayPal')),
        ('razorpay', _('Razorpay')),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payment_methods')
    type = models.CharField(_('type'), max_length=20, choices=TYPE_CHOICES)
    provider = models.CharField(_('provider'), max_length=20, choices=PROVIDER_CHOICES, default='stripe')
    token = models.CharField(_('token'), max_length=255)
    is_default = models.BooleanField(_('default'), default=False)
    is_active = models.BooleanField(_('active'), default=True)
    
    # Card-specific fields
    card_last4 = models.CharField(_('last 4 digits'), max_length=4, blank=True)
    card_brand = models.CharField(_('card brand'), max_length=50, blank=True)
    card_exp_month = models.PositiveSmallIntegerField(_('expiry month'), null=True, blank=True)
    card_exp_year = models.PositiveSmallIntegerField(_('expiry year'), null=True, blank=True)
    
    # Bank account fields
    bank_name = models.CharField(_('bank name'), max_length=100, blank=True)
    bank_account_last4 = models.CharField(_('last 4 digits of account'), max_length=4, blank=True)
    
    # Digital wallet fields
    wallet_email = models.EmailField(_('wallet email'), blank=True)
    
    # UPI fields
    upi_id = models.CharField(_('UPI ID'), max_length=255, blank=True)
    
    # Stripe-specific fields
    stripe_payment_method_id = models.CharField(_('Stripe payment method ID'), max_length=255, blank=True)
    stripe_customer_id = models.CharField(_('Stripe customer ID'), max_length=255, blank=True)
    
    # Metadata
    metadata = models.JSONField(_('metadata'), null=True, blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('payment method')
        verbose_name_plural = _('payment methods')
        unique_together = ('user', 'token')
    
    def __str__(self):
        if self.type == 'card':
            return f"{self.card_brand} **** {self.card_last4}"
        elif self.type == 'bank':
            return f"{self.bank_name} **** {self.bank_account_last4}"
        elif self.type == 'wallet':
            return f"{self.provider} - {self.wallet_email}"
        elif self.type == 'upi':
            return f"UPI - {self.upi_id}"
        return self.token


class Transaction(models.Model):
    STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('processing', _('Processing')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
        ('refunded', _('Refunded')),
    )
    
    TYPE_CHOICES = (
        ('payment', _('Payment')),
        ('refund', _('Refund')),
        ('chargeback', _('Chargeback')),
    )
    
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='transactions')
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True)
    transaction_id = models.CharField(_('transaction ID'), max_length=255, unique=True)
    amount = models.DecimalField(_('amount'), max_digits=10, decimal_places=2)
    currency = models.CharField(_('currency'), max_length=3)
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES)
    type = models.CharField(_('type'), max_length=20, choices=TYPE_CHOICES)
    
    # Payment provider details
    provider = models.CharField(_('provider'), max_length=100)
    provider_transaction_id = models.CharField(_('provider transaction ID'), max_length=255)
    provider_status = models.CharField(_('provider status'), max_length=100)
    provider_response = models.JSONField(_('provider response'), null=True, blank=True)
    
    # Error handling
    error_code = models.CharField(_('error code'), max_length=100, blank=True)
    error_message = models.TextField(_('error message'), blank=True)
    
    # Metadata
    metadata = models.JSONField(_('metadata'), null=True, blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    completed_at = models.DateTimeField(_('completed at'), null=True, blank=True)
    
    # History
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = _('transaction')
        verbose_name_plural = _('transactions')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.transaction_id} - {self.amount} {self.currency}"


class Invoice(models.Model):
    STATUS_CHOICES = (
        ('draft', _('Draft')),
        ('sent', _('Sent')),
        ('paid', _('Paid')),
        ('cancelled', _('Cancelled')),
    )
    
    order = models.OneToOneField('orders.Order', on_delete=models.CASCADE, related_name='invoice')
    invoice_number = models.CharField(_('invoice number'), max_length=50, unique=True)
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Amounts
    subtotal = models.DecimalField(_('subtotal'), max_digits=10, decimal_places=2)
    tax = models.DecimalField(_('tax'), max_digits=10, decimal_places=2)
    shipping = models.DecimalField(_('shipping'), max_digits=10, decimal_places=2)
    total = models.DecimalField(_('total'), max_digits=10, decimal_places=2)
    
    # Dates
    issue_date = models.DateField(_('issue date'))
    due_date = models.DateField(_('due date'))
    paid_date = models.DateField(_('paid date'), null=True, blank=True)
    
    # Notes
    notes = models.TextField(_('notes'), blank=True)
    terms = models.TextField(_('terms and conditions'), blank=True)
    
    # Metadata
    metadata = models.JSONField(_('metadata'), null=True, blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('invoice')
        verbose_name_plural = _('invoices')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Invoice {self.invoice_number}" 