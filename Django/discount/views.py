# Create your views here.
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from decimal import Decimal
from .models import PromoCode


def validate_promo_code(request):
    if request.method == 'POST':
        code = request.POST.get('promo_code')
        total_amount = Decimal(request.POST.get('total_amount', '0.00'))
        
        if not code:
            return JsonResponse({'valid': False, 'message': 'No promo code provided'})
        
        # Special case for GROUP2 promo code
        if code.upper() == 'GROUP2':
            return JsonResponse({
                'valid': True,
                'message': 'Promo code applied! Your order is free!',
                'discount_amount': str(total_amount),
                'new_total': '0.00',
                'discount_percentage': '100',
                'is_free': True
            })
        
        try:
            promo = PromoCode.objects.get(code=code)
            if promo.is_valid():
                discount_percentage = promo.discount_percentage
                discount_amount = (total_amount * discount_percentage) / Decimal('100.00')
                new_total = total_amount - discount_amount
                
                return JsonResponse({
                    'valid': True,
                    'message': f'Promo code applied! {discount_percentage}% discount',
                    'discount_amount': str(discount_amount),
                    'new_total': str(new_total),
                    'discount_percentage': str(discount_percentage),
                    'is_free': False
                })
            else:
                return JsonResponse({'valid': False, 'message': 'This promo code is not valid or has expired'})
        except PromoCode.DoesNotExist:
            return JsonResponse({'valid': False, 'message': 'Invalid promo code'})
    
    return JsonResponse({'valid': False, 'message': 'Invalid request'})

# View to apply promo code in session
def apply_promo_code(request):
    if request.method == 'POST':
        code = request.POST.get('promo_code')
        if code:
            # Special case for GROUP2 promo code
            if code.upper() == 'GROUP2':
                request.session['promo_code'] = code.upper()
                request.session['is_free_order'] = True
                messages.success(request, 'Promo code GROUP2 applied! Your order is free!')
                return redirect('checkout')
            
            try:
                promo = PromoCode.objects.get(code=code)
                if promo.is_valid():
                    request.session['promo_code'] = code
                    request.session['is_free_order'] = False
                    messages.success(request, f'Promo code {code} applied!')
                else:
                    messages.error(request, 'This promo code is not valid or has expired')
            except PromoCode.DoesNotExist:
                messages.error(request, 'Invalid promo code')
        
        return redirect('checkout')