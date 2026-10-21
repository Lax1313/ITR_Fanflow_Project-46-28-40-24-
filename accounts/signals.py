from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import UserProfile

User = get_user_model()

# Maps each role value to the Django Group name it should belong to.
ROLE_GROUP_NAME = {
    UserProfile.Role.ADMIN: 'Admin',
    UserProfile.Role.SUPPLY_CHAIN_MANAGER: 'Supply Chain Manager',
    UserProfile.Role.PROCUREMENT_MANAGER: 'Procurement Manager',
    UserProfile.Role.INVENTORY_MANAGER: 'Inventory Manager',
    UserProfile.Role.PRODUCTION_MANAGER: 'Production Manager',
}


@receiver(post_save, sender=User)
def create_profile_for_new_user(sender, instance, created, **kwargs):
    """Every new User automatically gets a UserProfile (defaults to
    Production Manager until an Admin assigns a real role)."""
    if created:
        UserProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=UserProfile)
def sync_group_with_role(sender, instance, **kwargs):
    """
    Keep the user's Django Group membership in sync with their role.
    This is what makes Django's built-in permission system
    (`user.has_perm(...)`) work correctly as model-level permissions
    are added to each Group in later steps.
    """
    group_name = ROLE_GROUP_NAME.get(instance.role)
    if not group_name:
        return

    group, _ = Group.objects.get_or_create(name=group_name)

    # Remove the user from any other role groups, then add the current one.
    instance.user.groups.remove(*[
        Group.objects.get_or_create(name=name)[0]
        for name in ROLE_GROUP_NAME.values()
        if name != group_name
    ])
    instance.user.groups.add(group)

    # Admins get Django's is_staff so they can use /admin/ too.
    if instance.role == UserProfile.Role.ADMIN and not instance.user.is_staff:
        instance.user.is_staff = True
        instance.user.save(update_fields=['is_staff'])
