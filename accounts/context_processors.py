from .access import SIDEBAR_ITEMS, sections_for_role


def sidebar_context(request):
    """
    Makes `sidebar_items` (filtered to what the current user's role can see)
    available in every template without each view having to pass it in.
    """
    if not request.user.is_authenticated:
        return {}

    profile = getattr(request.user, 'profile', None)
    role = profile.role if profile else None

    if request.user.is_superuser:
        allowed = {item['key'] for item in SIDEBAR_ITEMS}
    else:
        allowed = sections_for_role(role)

    visible_items = [item for item in SIDEBAR_ITEMS if item['key'] in allowed]

    return {
        'sidebar_items': visible_items,
        'user_role_display': profile.get_role_display() if profile else 'No role assigned',
    }
