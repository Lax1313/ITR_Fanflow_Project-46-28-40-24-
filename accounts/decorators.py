from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

from .access import can_access


def role_required(*allowed_roles):
    """
    View decorator restricting access to specific UserProfile roles.

    Usage:
        @role_required('ADMIN', 'SCM')
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped(request, *args, **kwargs):
            profile = getattr(request.user, 'profile', None)
            if request.user.is_superuser or (profile and profile.role in allowed_roles):
                return view_func(request, *args, **kwargs)
            messages.error(request, "You don't have permission to access that page.")
            return redirect('dashboard:home')
        return _wrapped
    return decorator


def section_required(section_key):
    """
    View decorator restricting access based on the ROLE_SECTIONS map in
    accounts/access.py, rather than listing roles by hand in every view.

    Usage:
        @section_required('procurement')
        def purchase_orders_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped(request, *args, **kwargs):
            profile = getattr(request.user, 'profile', None)
            role = profile.role if profile else None
            if request.user.is_superuser or can_access(role, section_key):
                return view_func(request, *args, **kwargs)
            messages.error(request, "You don't have permission to access that page.")
            return redirect('dashboard:home')
        return _wrapped
    return decorator


class RoleRequiredMixin:
    """Class-based view equivalent of @role_required."""
    allowed_roles = ()

    def dispatch(self, request, *args, **kwargs):
        profile = getattr(request.user, 'profile', None)
        if request.user.is_authenticated and (
            request.user.is_superuser or (profile and profile.role in self.allowed_roles)
        ):
            return super().dispatch(request, *args, **kwargs)
        if not request.user.is_authenticated:
            return redirect(f"{'/accounts/login/'}?next={request.path}")
        raise PermissionDenied("You don't have permission to access this page.")
