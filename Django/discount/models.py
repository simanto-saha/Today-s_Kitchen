# discount/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import decimal as Decimal

class PromoCode(models.Model):
    code = models.CharField(max_length=20, unique=True)
    description = models.CharField(max_length=255)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField(default=timezone.now)
    valid_to = models.DateTimeField(null=True, blank=True)
    max_uses = models.PositiveIntegerField(default=0)  # 0 means unlimited
    current_uses = models.PositiveIntegerField(default=0)
    is_special_free = models.BooleanField(default=False, help_text="If true, this promo code makes the entire order free")
    is_first_order = models.BooleanField(default=False, help_text="If true, this promo code is for first-time customers only")
    
    def __str__(self):
        if self.is_special_free:
            return f"{self.code} (FREE ORDER)"
        if self.is_first_order:
            return f"{self.code} (FIRST ORDER - {self.discount_percentage}%)"
        return f"{self.code} ({self.discount_percentage}%)"
    
    def is_valid(self):
        now = timezone.now()
        if not self.is_active:
            return False
        if self.valid_to and now > self.valid_to:
            return False
        if now < self.valid_from:
            return False
        if self.max_uses > 0 and self.current_uses >= self.max_uses:
            return False
        return True
    
    def is_valid_for_user(self, user):
        """Check if promo code is valid for the specific user"""
        # First check general validity
        if not self.is_valid():
            return False
            
        # If it's a first-order promo, check if user has previous orders
        if self.is_first_order and user and user.is_authenticated:
            from cart.models import Order  # Import here to avoid circular imports
            previous_orders = Order.objects.filter(user=user).exists()
            if previous_orders:
                return False
                
        return True

    @classmethod
    def is_group2_code(cls, code):
        """Check if the provided code is the special GROUP2 code"""
        return code and code.upper() == 'GROUP2'


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='discount_orders')
    created_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    final_amount = models.DecimalField(max_digits=10, decimal_places=2)
    promo_code = models.ForeignKey(PromoCode, on_delete=models.SET_NULL, null=True, blank=True, related_name='discount_orders')
    is_first_order = models.BooleanField(default=False)
    is_free_order = models.BooleanField(default=False, help_text="If true, this order was free due to a special promo code")
    
    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"
    
    def save(self, *args, **kwargs):
        # Calculate final amount
        if self.is_free_order:
            self.discount_amount = self.total_amount
            self.final_amount = Decimal('0.00')
        else:
            self.final_amount = self.total_amount - self.discount_amount
        super().save(*args, **kwargs)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    has_used_first_order_discount = models.BooleanField(default=False)
    
    def __str__(self):
        return self.user.username
