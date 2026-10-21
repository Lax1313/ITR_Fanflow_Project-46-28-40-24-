from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model

from .models import UserProfile

User = get_user_model()


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_role', 'is_staff')

    def get_role(self, obj):
        return getattr(obj.profile, 'get_role_display', lambda: '—')()
    get_role.short_description = 'Role'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'department', 'is_active_employee', 'created_at')
    list_filter = ('role', 'is_active_employee')
    search_fields = ('user__username', 'user__email', 'department')


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
