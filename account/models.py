from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    reset_password_token = models.CharField(max_length=50, blank=True, default='')
    reset_password_token_expiry = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.user.username
    
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, created, **kwargs):

    print('User profile signal triggered')

    user = instance

    if created:
        userProfile = UserProfile(user=user)
        userProfile.save()