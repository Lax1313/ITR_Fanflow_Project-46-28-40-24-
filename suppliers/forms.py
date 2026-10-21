from django import forms

from .models import Supplier, SupplierMaterial


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'contact_person', 'email', 'phone', 'location',
                  'quality_score', 'reliability_score', 'status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-select' if isinstance(field.widget, forms.Select) else 'form-control'


class SupplierMaterialForm(forms.ModelForm):
    class Meta:
        model = SupplierMaterial
        fields = ['unit_price', 'lead_time_days', 'quality_score', 'reliability_score',
                  'on_time_delivery_rate', 'minimum_order_quantity', 'supplier_capacity',
                  'transportation_cost']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
