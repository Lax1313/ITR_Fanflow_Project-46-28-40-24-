from django import forms
from django.forms import inlineformset_factory

from .models import BOM, BOMItem


class BOMForm(forms.ModelForm):
    class Meta:
        model = BOM
        fields = ['product', 'version', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-select' if isinstance(field.widget, forms.Select) else 'form-control'


BOMItemFormSet = inlineformset_factory(
    BOM, BOMItem,
    fields=['material', 'quantity_required'],
    extra=5, can_delete=True,
)


class CompleteProductionForm(forms.Form):
    product = forms.ModelChoiceField(queryset=None, label="Product manufactured")
    quantity_produced = forms.IntegerField(min_value=1, label="Quantity completed")
    reference = forms.CharField(max_length=100, required=False, label="Reference / Order #",
                                 help_text="Optional — e.g. the customer order number this run fulfills.")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from products.models import Product
        self.fields['product'].queryset = Product.objects.filter(is_active=True)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-select' if isinstance(field.widget, forms.Select) else 'form-control'


class MRPForm(forms.Form):
    product = forms.ModelChoiceField(queryset=None, label="Product")
    production_quantity = forms.IntegerField(min_value=1, label="Planned production quantity")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from products.models import Product
        self.fields['product'].queryset = Product.objects.filter(is_active=True)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-select' if isinstance(field.widget, forms.Select) else 'form-control'
