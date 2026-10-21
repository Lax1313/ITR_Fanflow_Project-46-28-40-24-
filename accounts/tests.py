from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from .models import UserProfile

User = get_user_model()


class RoleAccessTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username='admin_test', password='pass12345')
        self.admin.profile.role = UserProfile.Role.ADMIN
        self.admin.profile.save()

        self.procurement = User.objects.create_user(username='proc_test', password='pass12345')
        self.procurement.profile.role = UserProfile.Role.PROCUREMENT_MANAGER
        self.procurement.profile.save()

    def test_admin_can_access_user_management(self):
        client = Client()
        client.login(username='admin_test', password='pass12345')
        response = client.get('/accounts/users/')
        self.assertEqual(response.status_code, 200)

    def test_non_admin_redirected_from_user_management(self):
        client = Client()
        client.login(username='proc_test', password='pass12345')
        response = client.get('/accounts/users/')
        self.assertEqual(response.status_code, 302)

    def test_unauthenticated_redirected_to_login(self):
        client = Client()
        response = client.get('/dashboard/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
