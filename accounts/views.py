from django.contrib import messages
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect, render

from .decorators import role_required
from .forms import CreateEmployeeForm, UpdateRoleForm
from .models import UserProfile

User = get_user_model()


@role_required('ADMIN')
def user_list(request):
    """Admin-only screen listing every employee account and their role."""
    profiles = UserProfile.objects.select_related('user').all()
    return render(request, 'accounts/user_list.html', {
        'profiles': profiles,
        'role_choices': UserProfile.Role.choices,
    })


@role_required('ADMIN')
def user_add(request):
    """Admin-only screen to create a new employee account with a role."""
    if request.method == 'POST':
        form = CreateEmployeeForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(
                request,
                f"Account created for {user.username} "
                f"({user.profile.get_role_display()})."
            )
            return redirect('accounts:user_list')
    else:
        form = CreateEmployeeForm()

    return render(request, 'accounts/user_form.html', {'form': form, 'mode': 'add'})


@role_required('ADMIN')
def user_edit(request, user_id):
    """Admin-only screen to change an employee's role or deactivate them."""
    target_user = get_object_or_404(User, pk=user_id)
    profile, _ = UserProfile.objects.get_or_create(user=target_user)

    if request.method == 'POST':
        form = UpdateRoleForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, f"Updated role for {target_user.username}.")
            return redirect('accounts:user_list')
    else:
        form = UpdateRoleForm(instance=profile)

    return render(request, 'accounts/user_form.html', {
        'form': form,
        'mode': 'edit',
        'target_user': target_user,
    })
