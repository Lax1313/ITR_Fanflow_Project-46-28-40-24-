from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from accounts.models import UserProfile

User = get_user_model()

DEMO_USERS = [
    ('scm_manager', 'Sana', 'Kapoor', UserProfile.Role.SUPPLY_CHAIN_MANAGER),
    ('procurement_manager', 'Raj', 'Mehta', UserProfile.Role.PROCUREMENT_MANAGER),
    ('inventory_manager', 'Priya', 'Nair', UserProfile.Role.INVENTORY_MANAGER),
    ('production_manager', 'Arjun', 'Rao', UserProfile.Role.PRODUCTION_MANAGER),
]

DEMO_PASSWORD = 'DemoPass123!'


class Command(BaseCommand):
    help = 'Creates one demo user per role (password: DemoPass123!) so you can test role-based access.'

    def handle(self, *args, **options):
        for username, first, last, role in DEMO_USERS:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={'first_name': first, 'last_name': last, 'email': f'{username}@example.com'},
            )
            if created:
                user.set_password(DEMO_PASSWORD)
                user.save()

            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.role = role
            profile.department = role.label
            profile.save()

            status = 'created' if created else 'updated'
            self.stdout.write(self.style.SUCCESS(f"{status}: {username} -> {role.label}"))

        self.stdout.write(self.style.SUCCESS(f"\nAll demo users share the password: {DEMO_PASSWORD}"))
