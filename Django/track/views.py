from django.shortcuts import render
from cart.models import Order

def track_order(request):
    order_id = request.GET.get('order_id')
    order = None
    
    if order_id:
        try:
            order = Order.objects.get(id=order_id)
        except:
            pass
            
    # Store current tracking page in session
    if not request.session.get('current_tracking_step'):
        request.session['current_tracking_step'] = 0
    
    return render(request, 'track/trac.html', {'order': order})