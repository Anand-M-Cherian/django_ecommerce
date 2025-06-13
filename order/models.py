from django.db import models
from django.contrib.auth.models import User
from product.models import Product

# Create your models here.

class PaymentStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    PAID = 'paid', 'Paid'
    FAILED = 'failed', 'Failed'
    REFUNDED = 'refunded', 'Refunded'

class PaymentMethod(models.TextChoices):
    CREDIT_CARD = 'credit_card', 'Credit Card'
    PAYPAL = 'paypal', 'PayPal'
    BANK_TRANSFER = 'bank_transfer', 'Bank Transfer'
    CASH_ON_DELIVERY = 'cash_on_delivery', 'Cash on Delivery'

class OrderStatus(models.TextChoices):
    PROCESSING = 'processing', 'Processing'
    SHIPPED = 'shipped', 'Shipped'
    DELIVERED = 'delivered', 'Delivered'
    CANCELED = 'canceled', 'Canceled'

class Order(models.Model):
    street = models.CharField(max_length=255, default="", blank=False)
    city = models.CharField(max_length=100, default="", blank=False)
    state = models.CharField(max_length=100, default="", blank=False)
    zip_code = models.CharField(max_length=20, default="", blank=False)
    phone_number = models.CharField(max_length=20, default="", blank=False)
    country = models.CharField(max_length=100, default="", blank=False)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING
    )
    order_status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PROCESSING
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.CREDIT_CARD
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Order {self.order_id} - {self.customer_name}"
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=255, default="", blank=False)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=7, decimal_places=2, default=0.00)
    image = models.CharField(max_length=2048, default="", blank=True) # URL to the product image
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.name)