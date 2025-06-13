from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_delete

# Create your models here.

class Category(models.TextChoices):
    ELECTRONICS = 'Electronics'
    LAPTOPS = 'Laptops'
    ARTS = 'Arts'
    FOOD = 'Food'
    HOME = 'Home'
    KITCHEN = 'Kitchen'

class Product(models.Model):
    name = models.CharField(max_length=200, default="", blank=False)
    description = models.TextField(max_length=1000, default="", blank=False)
    price = models.DecimalField(max_digits=7, decimal_places=2, default=0.00, blank=False)
    brand = models.CharField(max_length=200, default="", blank=False)
    category = models.CharField(max_length=30, choices=Category.choices, default=Category.ELECTRONICS)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00, blank=False)
    stock = models.PositiveIntegerField(default=0, blank=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='products')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class ProductImages(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, related_name='images')
    image = models.ImageField(upload_to='product_images/')

    def __str__(self):
        return f"Image for {self.product.name}"

@receiver(post_delete, sender=ProductImages)
def auto_remove_image_on_delete(sender, instance, **kwargs):
    # django signal to delete the image file from s3 bucket when the ProductImages instance is deleted
    if instance.image:
        instance.image.delete(save=False)

class ProductReviews(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reviews')
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00, blank=False)
    comment = models.TextField(max_length=1000, default="", blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.comment[:50]  # Return first 50 characters of the comment