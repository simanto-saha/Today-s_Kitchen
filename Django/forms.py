from django import forms
from datetime import datetime

class ShippingAddressForm(forms.Form):
    full_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    address = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'form-control'}))
    city = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    state = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    postal_code = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control'}))

class PaymentForm(forms.Form):
    PAYMENT_CHOICES = [
        ('cash', 'Cash on Delivery'),
        ('card', 'Credit/Debit Card'),
    ]
    
    payment_method = forms.ChoiceField(
        choices=PAYMENT_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'payment-method-radio'})
    )
    
    MONTH_CHOICES = [(i, str(i)) for i in range(1, 13)]
    YEAR_CHOICES = [(i, str(i)) for i in range(datetime.now().year, datetime.now().year + 11)]
    
    card_number = forms.CharField(
        max_length=16, 
        min_length=16, 
        widget=forms.TextInput(attrs={'class': 'form-control card-field', 'placeholder': '1234 5678 9012 3456'}),
        required=False
    )
    card_holder_name = forms.CharField(
        max_length=100, 
        widget=forms.TextInput(attrs={'class': 'form-control card-field'}),
        required=False
    )
    expiry_month = forms.ChoiceField(
        choices=MONTH_CHOICES, 
        widget=forms.Select(attrs={'class': 'form-control card-field'}),
        required=False
    )
    expiry_year = forms.ChoiceField(
        choices=YEAR_CHOICES, 
        widget=forms.Select(attrs={'class': 'form-control card-field'}),
        required=False
    )
    cvv = forms.CharField(
        max_length=4, 
        min_length=3, 
        widget=forms.TextInput(attrs={'class': 'form-control card-field', 'placeholder': 'CVV'}),
        required=False
    )
    
    def clean(self):
        cleaned_data = super().clean()
        payment_method = cleaned_data.get('payment_method')
        
        if payment_method == 'card':
            # Validate card fields only if card payment is selected
            card_fields = ['card_number', 'card_holder_name', 'expiry_month', 'expiry_year', 'cvv']
            for field in card_fields:
                if not cleaned_data.get(field):
                    self.add_error(field, f"This field is required for card payment")
            
            # Validate card number format
            card_number = cleaned_data.get('card_number')
            if card_number:
                card_number = card_number.replace(' ', '')
                if not card_number.isdigit():
                    self.add_error('card_number', "Card number must contain only digits")
                cleaned_data['card_number'] = card_number
                
        return cleaned_data