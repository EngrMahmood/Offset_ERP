from django import forms
from .models import SKURecipe

class SKURecipeForm(forms.ModelForm):
    class Meta:
        model = SKURecipe
        fields = [
            'sku_name',
            'material_type', 'application_type',
            'one_up_width', 'one_up_height',
            'print_sheet_width', 'print_sheet_height', 'ups',
            'purchase_sheet_width', 'purchase_sheet_height', 'purchase_ups',
        ]
        widgets = {
            'sku_name': forms.TextInput(attrs={'class': 'form-control'}),
            'material_type': forms.TextInput(attrs={'class': 'form-control'}),
            'application_type': forms.TextInput(attrs={'class': 'form-control'}),

            'one_up_width': forms.NumberInput(attrs={'class': 'form-control'}),
            'one_up_height': forms.NumberInput(attrs={'class': 'form-control'}),

            'print_sheet_width': forms.NumberInput(attrs={'class': 'form-control'}),
            'print_sheet_height': forms.NumberInput(attrs={'class': 'form-control'}),
            'ups': forms.NumberInput(attrs={'class': 'form-control'}),

            'purchase_sheet_width': forms.NumberInput(attrs={'class': 'form-control'}),
            'purchase_sheet_height': forms.NumberInput(attrs={'class': 'form-control'}),
            'purchase_ups': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class BulkUploadForm(forms.Form):
    file = forms.FileField(
        label="Upload CSV or Excel file",
        help_text="Only .csv or .xlsx files are supported"
    )
