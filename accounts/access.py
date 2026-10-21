"""
Central place that maps each role to:
  - the Django Group it corresponds to (for model-level permissions)
  - which sidebar sections / URL namespaces it's allowed to open

Per MASTER PROMPT Section 16:

Admin                    -> full access
Supply Chain Manager     -> Dashboard, Forecasting, Inventory, Suppliers,
                             Procurement, Logistics, Analytics, AI Assistant
Procurement Manager      -> Suppliers, Supplier comparison, Procurement,
                             Purchase orders
Inventory Manager        -> Inventory, Materials, Stock transactions, Alerts
Production Manager       -> Orders, Demand forecasts, BOM, Material requirements

Every role also gets Dashboard and Reports, since every role needs a
landing page and the ability to export their own reports.
"""

from accounts.models import UserProfile

Role = UserProfile.Role

ALL_SECTIONS = {
    'dashboard', 'products', 'materials', 'bom', 'orders', 'forecasting',
    'inventory', 'suppliers', 'procurement', 'logistics', 'risk',
    'analytics', 'ai_assistant', 'reports', 'settings', 'user_management',
}

ROLE_SECTIONS = {
    Role.ADMIN: ALL_SECTIONS,
    Role.SUPPLY_CHAIN_MANAGER: {
        'dashboard', 'forecasting', 'inventory', 'suppliers', 'procurement',
        'logistics', 'analytics', 'ai_assistant', 'reports',
    },
    Role.PROCUREMENT_MANAGER: {
        'dashboard', 'suppliers', 'procurement', 'reports',
    },
    Role.INVENTORY_MANAGER: {
        'dashboard', 'inventory', 'materials', 'reports',
    },
    Role.PRODUCTION_MANAGER: {
        'dashboard', 'orders', 'forecasting', 'bom', 'products', 'reports',
    },
}

# Human-readable labels + icons + URL name for the sidebar, keyed by section.
# url is None where the view doesn't exist yet (added in a later step) --
# the template renders those as disabled/greyed-out links.
SIDEBAR_ITEMS = [
    {'key': 'dashboard', 'label': 'Dashboard', 'icon': 'bi-speedometer2', 'url': 'dashboard:home'},
    {'key': 'products', 'label': 'Products', 'icon': 'bi-box-seam', 'url': 'products:list'},
    {'key': 'materials', 'label': 'Materials', 'icon': 'bi-tools', 'url': 'materials:list'},
    {'key': 'bom', 'label': 'BOM', 'icon': 'bi-diagram-2', 'url': 'production:bom_list'},
    {'key': 'orders', 'label': 'Orders', 'icon': 'bi-cart-check', 'url': 'orders:list'},
    {'key': 'forecasting', 'label': 'Forecasting', 'icon': 'bi-graph-up-arrow', 'url': 'forecasting:home'},
    {'key': 'inventory', 'label': 'Inventory', 'icon': 'bi-boxes', 'url': 'inventory:list'},
    {'key': 'suppliers', 'label': 'Suppliers', 'icon': 'bi-truck', 'url': 'suppliers:list'},
    {'key': 'procurement', 'label': 'Procurement', 'icon': 'bi-bag-check', 'url': 'procurement:recommendations'},
    {'key': 'logistics', 'label': 'Logistics', 'icon': 'bi-signpost-split', 'url': 'logistics:list'},
    {'key': 'risk', 'label': 'Risk Analysis', 'icon': 'bi-exclamation-triangle', 'url': 'risk_management:list'},
    {'key': 'analytics', 'label': 'Analytics', 'icon': 'bi-bar-chart-line', 'url': 'analytics:home'},
    {'key': 'ai_assistant', 'label': 'AI Assistant', 'icon': 'bi-robot', 'url': 'ai_assistant:chat'},
    {'key': 'reports', 'label': 'Reports', 'icon': 'bi-file-earmark-text', 'url': 'reports:hub'},
    {'key': 'user_management', 'label': 'Users & Roles', 'icon': 'bi-people', 'url': 'accounts:user_list'},
    {'key': 'settings', 'label': 'Settings', 'icon': 'bi-gear', 'url': None},
]


def sections_for_role(role):
    return ROLE_SECTIONS.get(role, {'dashboard'})


def can_access(role, section_key):
    return section_key in sections_for_role(role)
