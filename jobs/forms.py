from django import forms
from .models import Job
from recipes.models import SKURecipe
import datetime

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            'sku', 'sku_code', 'job_name', 'po_number', 'po_quantity', 
            'po_date', 'unit_cost', 'planned_date', 'customer_name', 'notes',
            'stock', 'wastage'
        ]
        widgets = {
            'po_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'planned_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'sku_code': forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
            'job_name': forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),  # Read-only JC# field
        }

    def save(self, commit=True, *args, **kwargs):
        # Add the JC# from JavaScript before saving
        if not self.instance.job_name:
            # Ensure we generate the JC# before saving
            currentMonth = datetime.datetime.now().month
            currentYear = datetime.datetime.now().year
            job_number = f"JC-{currentMonth}-{currentYear}-00X1"  # Default to 0001

            self.instance.job_name = job_number  # Set the JC# here

        return super().save(commit=commit, *args, **kwargs)

    # Adding read-only fields for SKURecipe attributes
    material_type = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control'}))
    application_type = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control'}))
    one_up_width = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'readonly': 'readonly', 'class': 'form-control'}))
    one_up_height = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'readonly': 'readonly', 'class': 'form-control'}))
    print_sheet_width = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'readonly': 'readonly', 'class': 'form-control'}))
    print_sheet_height = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'readonly': 'readonly', 'class': 'form-control'}))
    print_sheet_size = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control'}))
    ups = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'readonly': 'readonly', 'class': 'form-control'}))
    purchase_sheet_width = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'readonly': 'readonly', 'class': 'form-control'}))
    purchase_sheet_height = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'readonly': 'readonly', 'class': 'form-control'}))
    purchase_sheet_size = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control'}))
    purchase_ups = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'readonly': 'readonly', 'class': 'form-control'}))

    # User input fields
    po_number = forms.CharField(required=True, max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))
    po_quantity = forms.IntegerField(required=True, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    unit_cost = forms.DecimalField(required=True, max_digits=10, decimal_places=2, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    customer_name = forms.CharField(required=True, max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    notes = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control'}))
    stock = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    wastage = forms.DecimalField(required=False, max_digits=6, decimal_places=2, widget=forms.NumberInput(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.sku:
            # Fetch the SKURecipe instance based on the sku
            try:
                sku_recipe = SKURecipe.objects.get(sku_name=self.instance.sku)
                # Set the sku_code and related fields
                self.fields['sku_code'].initial = sku_recipe.sku_code
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
