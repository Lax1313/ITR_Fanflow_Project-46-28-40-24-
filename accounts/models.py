from django.conf import settings
from django.db import models


class UserProfile(models.Model):
    """
    Extends Django's built-in User with the role this person plays in the
    supply chain organisation. The role drives:
      - which sidebar sections they see
      - which views they're allowed to open (via role_required decorator)
      - which Django Group they belong to (for model-level permissions,
        added as each app's models are built in later steps)
    """

    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        SUPPLY_CHAIN_MANAGER = 'SCM', 'Supply Chain Manager'
        PROCUREMENT_MANAGER = 'PROCUREMENT', 'Procurement Manager'
        INVENTORY_MANAGER = 'INVENTORY', 'Inventory Manager'
        PRODUCTION_MANAGER = 'PRODUCTION', 'Production Manager'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.PRODUCTION_MANAGER,
    )
    phone = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=100, blank=True)
    is_active_employee = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['user__username']

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"
