from django import forms
from .models import Job
from recipes.models import SKURecipe

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            'sku', 'sku_code', 'po_number', 'po_quantity', 
            'po_date', 'unit_cost', 'planned_date', 'customer_name', 'notes'
        ]
        widgets = {
            'po_date': forms.DateInput(attrs={'type': 'date'}),
            'planned_date': forms.DateInput(attrs={'type': 'date'}),
            'sku_code': forms.TextInput(attrs={'readonly': 'readonly'}),  # Make sku_code read-only
        }

    # Adding read-only fields for SKURecipe attributes
    material_type = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    application_type = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    one_up_width = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'readonly': 'readonly'}))
    one_up_height = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'readonly': 'readonly'}))
    print_sheet_width = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'readonly': 'readonly'}))
    print_sheet_height = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'readonly': 'readonly'}))
    print_sheet_size = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    ups = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'readonly': 'readonly'}))
    purchase_sheet_width = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'readonly': 'readonly'}))
    purchase_sheet_height = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'readonly': 'readonly'}))
    purchase_sheet_size = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    purchase_ups = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'readonly': 'readonly'}))

    # User input fields
    po_number = forms.CharField(required=True, max_length=50)
    po_quantity = forms.IntegerField(required=True)
    unit_cost = forms.DecimalField(required=True, max_digits=10, decimal_places=2)
    customer_name = forms.CharField(required=True, max_length=100)
    notes = forms.CharField(required=False, widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.sku:
            # Fetch the SKURecipe instance based on the sku
            try:
                sku_recipe = SKURecipe.objects.get(sku_name=self.instance.sku)
                # Set the sku_code and related fields
                self.fields['sku_code'].initial = sku_recipe.sku_code  # Set SKU Code here
                self.fields['material_type'].initial = sku_recipe.material_type
                self.fields['application_type'].initial = sku_recipe.application_type
                self.fields['one_up_width'].initial = sku_recipe.one_up_width
                self.fields['one_up_height'].initial = sku_recipe.one_up_height
                self.fields['print_sheet_width'].initial = sku_recipe.print_sheet_width
                self.fields['print_sheet_height'].initial = sku_recipe.print_sheet_height
                self.fields['print_sheet_size'].initial = sku_recipe.print_sheet_size
                self.fields['ups'].initial = sku_recipe.ups
                self.fields['purchase_sheet_width'].initial = sku_recipe.purchase_sheet_width
                self.fields['purchase_sheet_height'].initial = sku_recipe.purchase_sheet_height
                self.fields['purchase_sheet_size'].initial = sku_recipe.purchase_sheet_size
                self.fields['purchase_ups'].initial = sku_recipe.purchase_ups
            except SKURecipe.DoesNotExist:
                raise ValueError("The specified SKU does not have an associated recipe.")
