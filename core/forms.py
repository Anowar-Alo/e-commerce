from django import forms
from django.contrib.auth import get_user_model
from .models import UserProfile
from payments.models import PaymentMethod
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

User = get_user_model()

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'avatar', 'phone_number', 'address', 'city', 'state', 'country', 'postal_code']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
        }

class PaymentMethodForm(forms.ModelForm):
    class Meta:
        model = PaymentMethod
        fields = ['type', 'provider', 'token', 'is_default', 'card_last4', 'card_brand', 'card_exp_month', 'card_exp_year', 'bank_name', 'bank_account_last4', 'wallet_email', 'upi_id']
        widgets = {
            'type': forms.Select(attrs={'class': 'form-control'}),
            'provider': forms.TextInput(attrs={'class': 'form-control'}),
            'token': forms.TextInput(attrs={'class': 'form-control'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'card_last4': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 4}),
            'card_brand': forms.TextInput(attrs={'class': 'form-control'}),
            'card_exp_month': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 12}),
            'card_exp_year': forms.NumberInput(attrs={'class': 'form-control', 'min': 2024, 'max': 2030}),
            'bank_name': forms.TextInput(attrs={'class': 'form-control'}),
            'bank_account_last4': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 4}),
            'wallet_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'upi_id': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        payment_type = cleaned_data.get('type')
        
        if payment_type == 'card':
            if not cleaned_data.get('card_last4'):
                self.add_error('card_last4', 'Last 4 digits are required for cards')
            if not cleaned_data.get('card_brand'):
                self.add_error('card_brand', 'Card brand is required')
            if not cleaned_data.get('card_exp_month'):
                self.add_error('card_exp_month', 'Expiry month is required')
            if not cleaned_data.get('card_exp_year'):
                self.add_error('card_exp_year', 'Expiry year is required')
        
        elif payment_type == 'bank':
            if not cleaned_data.get('bank_name'):
                self.add_error('bank_name', 'Bank name is required')
            if not cleaned_data.get('bank_account_last4'):
                self.add_error('bank_account_last4', 'Last 4 digits of account are required')
        
        elif payment_type == 'wallet':
            if not cleaned_data.get('wallet_email'):
                self.add_error('wallet_email', 'Wallet email is required')
        
        elif payment_type == 'upi':
            if not cleaned_data.get('upi_id'):
                self.add_error('upi_id', 'UPI ID is required')
        
        return cleaned_data

class CustomAdminLoginForm(AuthenticationForm):
    username = forms.CharField(
        label=_("Username"),
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter your username'),
            'autofocus': True
        })
    )
    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter your password')
        })
    )

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(
                self.request,
                username=username,
                password=password
            )
            if self.user_cache is None:
                raise forms.ValidationError(
                    _("Please enter a correct username and password. Note that both fields may be case-sensitive."),
                    code='invalid_login',
                )
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise forms.ValidationError(
                _("This account is inactive."),
                code='inactive',
            )
        if not user.is_staff:
            raise forms.ValidationError(
                _("This account doesn't have admin privileges."),
                code='no_admin',
            )

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email address is already in use.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'avatar', 'phone_number', 'address', 'city', 'state', 'country', 'postal_code']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
        } 