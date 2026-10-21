from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import UserProfile

User = get_user_model()


class BootstrapFormMixin:
    """Adds Bootstrap 5 CSS classes to every field's widget automatically."""

    def _apply_bootstrap(self):
        for field in self.fields.values():
            existing = field.widget.attrs.get('class', '')
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = (existing + ' form-check-input').strip()
            else:
                field.widget.attrs['class'] = (existing + ' form-control').strip()


class CreateEmployeeForm(BootstrapFormMixin, UserCreationForm):
    """Used by Admins to create a new employee account with a role."""

    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=False)
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=UserProfile.Role.choices)
    phone = forms.CharField(max_length=20, required=False)
    department = forms.CharField(max_length=100, required=False)

    class Meta:
        model = User
        fields = [
            'username', 'first_name', 'last_name', 'email',
            'password1', 'password2', 'role', 'phone', 'department',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_bootstrap()

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            profile = user.profile
            profile.role = self.cleaned_data['role']
            profile.phone = self.cleaned_data.get('phone', '')
            profile.department = self.cleaned_data.get('department', '')
            profile.save()
        return user


class UpdateRoleForm(BootstrapFormMixin, forms.ModelForm):
    """Used by Admins to change an existing employee's role/department."""

    class Meta:
        model = UserProfile
        fields = ['role', 'phone', 'department', 'is_active_employee']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_bootstrap()
