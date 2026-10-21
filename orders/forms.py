from django import forms

from .models import CustomerOrder


class CustomerOrderForm(forms.ModelForm):
    class Meta:
        model = CustomerOrder
        fields = ['customer_name', 'product', 'quantity', 'order_date',
                  'required_delivery_date', 'region', 'priority', 'status']
        widgets = {
            'order_date': forms.DateInput(attrs={'type': 'date'}),
            'required_delivery_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-select' if isinstance(field.widget, forms.Select) else 'form-control'
