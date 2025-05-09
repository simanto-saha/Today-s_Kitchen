# meal/forms.py

from django import forms

class MealRegisterForm(forms.Form):
    address = forms.CharField(
        max_length=100,
        required=True,
        label='Address',
        widget=forms.TextInput(attrs={'placeholder': 'Enter your address'})
    )
    
    start_date = forms.DateField(
        required=True,
        label='Start Date',
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    
    advance_payment = forms.DecimalField(
        max_digits=8,
        decimal_places=2,
        required=True,
        label='Advance Payment (BDT)',
        widget=forms.NumberInput(attrs={'placeholder': 'Enter amount (e.g., 500.00)'})
    )
    
    agree_terms = forms.BooleanField(
        required=True,
        label='I agree to the Terms and Policies'
    )

    # Add the meal range selection field
    meal_range = forms.ChoiceField(
        choices=[('150-200', '150 - 200'),
                 ('500-600', '500 - 600'),
                 ('1000+', '1000+')],
        required=True,
        label='Meal Range'
    )
