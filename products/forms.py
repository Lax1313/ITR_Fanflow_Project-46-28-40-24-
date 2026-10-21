from django import forms

from .models import Product


class BootstrapModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs['class'] = 'form-control'
                field.widget.attrs['rows'] = 3
            else:
                field.widget.attrs['class'] = 'form-control'


class ProductForm(BootstrapModelForm):
    class Meta:
        model = Product
        fields = ['name', 'model_number', 'category', 'description', 'selling_price',
                  'production_capacity', 'power_rating', 'is_active']
