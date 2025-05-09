from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
from .models import Cart, CartItem
from register.models import MenuItem  # Replace 'your_app' with your menu app name
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from .models import Cart, Order, OrderItem
from .forms import ShippingAddressForm, PaymentForm
from decimal import Decimal
import uuid
from notification.models import Notification
from discount.models import PromoCode 
from cart.models import Order  # Import Order model

def is_first_order(user):
    if user.is_authenticated:
        return not Order.objects.filter(user=user).exists()
    return False


def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_id = request.session.session_key
        if not session_id:
            request.session.create()
            session_id = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_id=session_id)
    return cart


def add_to_cart(request, item_id):
    try:
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            data = {}

        quantity = int(data.get('quantity', 1))
        
        cart = get_or_create_cart(request)
        item = MenuItem.objects.get(id=item_id)

        cart_item, created = CartItem.objects.get_or_create(cart=cart, item=item)

        # The bug is here - we're always setting quantity to 1 when created
        # and adding 1 when not created
        if created:
            cart_item.quantity = quantity  # Set initial quantity from request
        else:
            cart_item.quantity += quantity  # Add requested quantity to existing

        cart_item.save()

        return JsonResponse({
            'success': True,
            'message': f"{quantity} item(s) added to cart",
            'cart_total': cart.items.count()
        })

    except MenuItem.DoesNotExist:
        return JsonResponse({'success': False, 'message': "Item not found"}, status=404)

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)




def view_cart(request):
    cart = get_or_create_cart(request)
    cart_items = cart.items.all()
    
    # Calculate subtotal
    subtotal = sum(item.item.price * item.quantity for item in cart_items)
    
    # Add shipping cost
    shipping_cost = Decimal('40.00')  # 40 TK shipping
    
    # Check if promo code is applied
    promo_code = request.session.get('promo_code', None)
    is_free_order = request.session.get('is_free_order', False)
    
    discount_amount = Decimal('0.00')
    discount_message = None
    
    if is_free_order or (promo_code and promo_code.upper() == 'GROUP2'):
        shipping_cost = Decimal('0.00')  # Free shipping with GROUP2 code
        total = subtotal  # No shipping cost
        discount_message = "GROUP2 promo code applied - Free shipping!"
        
        if is_free_order and promo_code and promo_code.upper() != 'GROUP2':
            total = Decimal('0.00')  # Entire order is free
            discount_message = "Special promo code applied - Your order is free!"
    elif promo_code:
        # Regular discount promo code
        try:
            promo = PromoCode.objects.get(code=promo_code)
            
            # First check if it's a first-order promo and if user is eligible
            if promo.is_first_order:
                if not request.user.is_authenticated:
                    # Remove promo code if user not logged in
                    request.session.pop('promo_code', None)
                    request.session.pop('is_free_order', None)
                    messages.error(request, 'You must be logged in to use the first-time customer discount')
                    total = subtotal + shipping_cost
                    context = {
                        'cart_items': cart_items,
                        'subtotal': subtotal,
                        'shipping_cost': shipping_cost,
                        'discount_amount': discount_amount,
                        'total': total,
                    }
                    return render(request, 'cart/cart.html', context)
                else:
                    from cart.models import Order
                    has_previous_orders = Order.objects.filter(user=request.user).exists()
                    
                    if has_previous_orders:
                        # Remove invalid promo code from session
                        request.session.pop('promo_code', None)
                        request.session.pop('is_free_order', None)
                        messages.error(request, 'This promo code is only valid for first-time customers')
                        total = subtotal + shipping_cost
                        context = {
                            'cart_items': cart_items,
                            'subtotal': subtotal,
                            'shipping_cost': shipping_cost,
                            'discount_amount': discount_amount,
                            'total': total,
                        }
                        return render(request, 'cart/cart.html', context)
            
            if promo.is_valid():
                discount_percentage = promo.discount_percentage
                discount_amount = (subtotal * discount_percentage) / Decimal('100.00')
                subtotal -= discount_amount
                
                if promo.is_first_order:
                    discount_message = f"First order promo code applied - {discount_percentage}% discount!"
                else:
                    discount_message = f"Promo code applied - {discount_percentage}% discount!"
            else:
                # Invalid or expired promo code, remove from session
                request.session.pop('promo_code', None)
                request.session.pop('is_free_order', None)
        except PromoCode.DoesNotExist:
            # Invalid promo code in session, remove it
            request.session.pop('promo_code', None)
            request.session.pop('is_free_order', None)
            
        total = subtotal + shipping_cost
    else:
        total = subtotal + shipping_cost
    
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping_cost': shipping_cost,
        'discount_amount': discount_amount,
        'total': total,
        'promo_code': promo_code,
        'discount_message': discount_message
    }
    
    # Render cart template
    return render(request, 'cart/cart.html', context)

# Add promo code validation function
@require_POST
def validate_promo_code(request):
    code = request.POST.get('promo_code')
    cart = get_or_create_cart(request)
    cart_items = cart.items.all()
    subtotal = sum(item.item.price * item.quantity for item in cart_items)
    shipping_cost = Decimal('40.00')  # Default shipping cost
    
    if not code:
        return JsonResponse({'valid': False, 'message': 'No promo code provided'})
    
    # Special case for GROUP2 promo code
    if PromoCode.is_group2_code(code):
        # Store the promo code in session
        request.session['promo_code'] = code.upper()
        request.session['is_free_order'] = True
        
        total = subtotal  # No shipping cost
        
        return JsonResponse({
            'valid': True,
            'message': 'Promo code GROUP2 applied! Your order shipping is free!',
            'subtotal': str(subtotal),
            'shipping_cost': '0.00',
            'total': str(total),
            'is_free': True
        })
    
    try:
        promo = PromoCode.objects.get(code=code)
        
        # Check if promo is valid for this specific user
        valid_for_user = True
        
        # For first-time promos, check user eligibility
        if promo.is_first_order:
            if not request.user.is_authenticated:
                return JsonResponse({
                    'valid': False, 
                    'message': 'You must be logged in to use the first-time customer discount'
                })
            
            # Check if user has previous orders
            from cart.models import Order
            has_previous_orders = Order.objects.filter(user=request.user).exists()
            
            if has_previous_orders:
                return JsonResponse({
                    'valid': False, 
                    'message': 'This promo code is only valid for first-time customers'
                })
        
        if promo.is_valid():
            # Store the promo code in session
            request.session['promo_code'] = code
            request.session['is_free_order'] = promo.is_special_free
            
            # Increment usage counter
            promo.current_uses += 1
            promo.save()
            
            discount_percentage = promo.discount_percentage
            discount_amount = (subtotal * discount_percentage) / Decimal('100.00')
            new_subtotal = subtotal - discount_amount
            
            # If special free promo, no shipping cost
            if promo.is_special_free:
                shipping_cost = Decimal('0.00')
                
            total = new_subtotal + shipping_cost
            
            # Custom message for first-order promo
            message = f'Promo code applied! {discount_percentage}% discount'
            if promo.is_first_order:
                message = f'First order promo code applied! {discount_percentage}% discount'
            
            return JsonResponse({
                'valid': True,
                'message': message,
                'subtotal': str(new_subtotal),
                'discount_amount': str(discount_amount),
                'shipping_cost': str(shipping_cost),
                'total': str(total),
                'is_free': promo.is_special_free
            })
        else:
            return JsonResponse({'valid': False, 'message': 'This promo code is not valid or has expired'})
    except PromoCode.DoesNotExist:
        return JsonResponse({'valid': False, 'message': 'Invalid promo code'})

# Apply promo code to session
def apply_promo_code(request):
    if request.method == 'POST':
        code = request.POST.get('promo_code')
        
        # Handle AJAX requests
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        if not code:
            if is_ajax:
                return JsonResponse({'valid': False, 'message': 'No promo code provided'})
            messages.error(request, 'Please enter a promo code')
            return redirect('view_cart')
        
        # Handle the GROUP2 special code
        if PromoCode.is_group2_code(code):
            request.session['promo_code'] = code.upper()
            request.session['is_free_order'] = True
            
            # Try to find if GROUP2 exists in the database to increment usage
            try:
                promo = PromoCode.objects.get(code='GROUP2')
                promo.current_uses += 1
                promo.save()
            except PromoCode.DoesNotExist:
                # GROUP2 is a special code not in the database
                pass
            
            if is_ajax:
                return JsonResponse({
                    'valid': True, 
                    'message': 'Promo code GROUP2 applied! Your shipping is free!'
                })
            
            messages.success(request, 'Promo code GROUP2 applied! Your shipping is free!')
            return redirect('view_cart')
        
        # Handle regular promo codes
        try:
            promo = PromoCode.objects.get(code=code)
            
            # Check if it's a first-order promo code and validate for the user
            if promo.is_first_order:
                if not request.user.is_authenticated:
                    if is_ajax:
                        return JsonResponse({
                            'valid': False, 
                            'message': 'You must be logged in to use the first-time customer discount'
                        })
                    messages.error(request, 'You must be logged in to use the first-time customer discount')
                    return redirect('view_cart')
                
                # Check if user has previous orders
                from cart.models import Order
                has_previous_orders = Order.objects.filter(user=request.user).exists()
                
                if has_previous_orders:
                    if is_ajax:
                        return JsonResponse({
                            'valid': False, 
                            'message': 'This promo code is only valid for first-time customers'
                        })
                    messages.error(request, 'This promo code is only valid for first-time customers')
                    return redirect('view_cart')
            
            if promo.is_valid():
                request.session['promo_code'] = code
                request.session['is_free_order'] = promo.is_special_free
                
                # Increment the promo code usage
                promo.current_uses += 1
                promo.save()
                
                # Custom message based on promo type
                success_message = f'Promo code {code} applied!'
                if promo.is_first_order:
                    success_message = f'First order promo code applied! {promo.discount_percentage}% discount!'
                
                if is_ajax:
                    return JsonResponse({
                        'valid': True, 
                        'message': success_message
                    })
                
                messages.success(request, success_message)
            else:
                if is_ajax:
                    return JsonResponse({
                        'valid': False, 
                        'message': 'This promo code is not valid or has expired'
                    })
                messages.error(request, 'This promo code is not valid or has expired')
        except PromoCode.DoesNotExist:
            if is_ajax:
                return JsonResponse({'valid': False, 'message': 'Invalid promo code'})
            messages.error(request, 'Invalid promo code')
        
        return redirect('view_cart')
    
    # GET requests should redirect to cart
    return redirect('view_cart')


def checkout(request):
    cart = get_or_create_cart(request)
    cart_items = cart.items.all()
    
    if not cart_items:
        messages.warning(request, "Your cart is empty. Add some items before checking out.")
        return redirect('view_cart')
    
    # Calculate cart subtotal
    subtotal = sum(item.item.price * item.quantity for item in cart_items)
    
    # Check if user is placing their first order
    is_new_user = is_first_order(request.user)

    if is_new_user:
        # Apply 25% discount for new users
        discount_percentage = 25
        discount_amount = (subtotal * discount_percentage) / Decimal('100.00')
        subtotal -= discount_amount
        discount_message = f"First order discount applied: {discount_percentage}% off!"
        messages.success(request, "You are eligible for a 25% discount on your first order!")
    else:
        discount_amount = Decimal('0.00')
        discount_message = None

    # Check if GROUP2 promo code is applied
    promo_code = request.session.get('promo_code', None)
    is_free_order = request.session.get('is_free_order', False)
    
    # Set shipping cost based on promo code
    shipping_cost = Decimal('0.00') if is_free_order or (promo_code and promo_code.upper() == 'GROUP2') else Decimal('40.00')
    
    # Calculate final total
    total = subtotal + shipping_cost
    
    # Handle discount if it's not a free order but has promo code
    discount_amount = Decimal('0.00')
    if promo_code and not is_free_order:
        try:
            promo = PromoCode.objects.get(code=promo_code)
            if promo.is_valid():
                discount_percentage = promo.discount_percentage
                discount_amount = (subtotal * discount_percentage) / Decimal('100.00')
                subtotal -= discount_amount
                total = subtotal + shipping_cost
        except PromoCode.DoesNotExist:
            pass

    
    # Pre-fill data for authenticated users
    initial_shipping_data = {}
    if request.user.is_authenticated:
        initial_shipping_data = {
            'full_name': request.user.get_full_name(),
            'email': request.user.email,
        }
    
    # Create forms
    shipping_form = ShippingAddressForm(prefix='shipping', initial=initial_shipping_data)
    payment_form = PaymentForm(prefix='payment', initial={'payment_method': 'cash'})
    
    if request.method == 'POST':
        shipping_form = ShippingAddressForm(request.POST, prefix='shipping')
        payment_form = PaymentForm(request.POST, prefix='payment')
        
        if shipping_form.is_valid() and payment_form.is_valid():
            # Create order
            order = Order()
            if request.user.is_authenticated:
                order.user = request.user
            
            # Set shipping info
            shipping_data = shipping_form.cleaned_data
            order.full_name = shipping_data['full_name']
            order.email = shipping_data['email']
            order.address = shipping_data['address']
            order.city = shipping_data['city']
            order.state = shipping_data['state']
            order.postal_code = shipping_data['postal_code']
            order.phone = shipping_data['phone']
            
            # Set payment method
            payment_data = payment_form.cleaned_data
            payment_method = payment_data['payment_method']
            order.payment_method = payment_method
            
            # Generate order number and set total
            order.order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
            order.subtotal = subtotal
            order.shipping_cost = shipping_cost
            order.discount_amount = discount_amount
            order.total_amount = total
            
            # Set promo code reference if used
            if promo_code:
                try:
                    promo = PromoCode.objects.get(code=promo_code)
                    order.promo_code = promo
                    order.is_free_order = is_free_order
                except PromoCode.DoesNotExist:
                    pass
            
            order.save()

            Notification.objects.create(
                user=request.user,
                title=f"New Order Placed: {order.order_number}",
                message=f"Order {order.order_number} has been placed. Click to view details.",
                order=order
            )
            
            # Create order items
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    item=cart_item.item,
                    quantity=cart_item.quantity,
                    price=cart_item.item.price
                )
            # Process payment based on method (unless free order)
            payment_successful = True
            if not is_free_order and payment_method == 'card' and total > 0:
                # Process card payment (in a real app, integrate with a payment gateway)
                payment_successful = process_card_payment(payment_data, total)
            else:
                # Cash on delivery or free order, no payment processing needed
                order.payment_status = 'pending' if total > 0 else 'completed'
                order.save()
            
            if payment_successful:
                # Clear the cart and promo code from session
                cart_items.delete()
                request.session.pop('promo_code', None)
                request.session.pop('is_free_order', None)
                
                # Redirect to order confirmation
                return redirect('order_confirmation', order_number=order.order_number)
            else:
                messages.error(request, "Payment processing failed. Please try again.")
    
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping_cost': shipping_cost,
        'discount_amount': discount_amount,
        'total': total,
        'shipping_form': shipping_form,
        'payment_form': payment_form,
        'promo_code': promo_code,
        'is_free_order': is_free_order,
        'discount_message': discount_message,
    }
    print(promo_code, shipping_cost)
    return render(request, 'cart/checkout.html', context)


# Helper function for card payment processing
def process_card_payment(payment_data, amount):
    # Implement your payment gateway integration here
    # This is a placeholder that always returns success
    return True


def process_payment(payment_data, amount):
    """
    Process payment (placeholder function)
    In a real app, this would integrate with a payment gateway like Stripe, PayPal, etc.
    """
    # For demo purposes, always return True (successful payment)
    # In production, you would validate the card and process the payment
    return True


def order_confirmation(request, order_number):
    try:
        order = Order.objects.get(order_number=order_number)
        context = {
            'order': order,
            'order_items': order.items.all()
        }
        return render(request, 'cart/order_confirmation.html', context)
    except Order.DoesNotExist:
        messages.error(request, "Order not found")
        return redirect('view_cart')