from django.db.models.signals import post_save
from django.contrib.auth.models import User, Group
from django.dispatch import receiver
from allauth.account.signals import user_signed_up
from .models import Profile

@receiver(user_signed_up)
def assign_reader_group(request, user, **kwargs):
    """
    Assign the 'Reader' group to new users upon registration.
    """
    try:
        reader_group = Group.objects.get(name='Reader')
        user.groups.add(reader_group)
    except Group.DoesNotExist:
        pass

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """
    Create a Profile for the user when a User object is created.
    """
    if created:
        Profile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    """
    Save the Profile when the User object is saved.
    """
    try:
        instance.profile.save()
    except Profile.DoesNotExist:
        Profile.objects.create(user=instance)
