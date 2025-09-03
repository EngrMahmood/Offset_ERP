from django.db import models
from recipes.models import SKURecipe
from django.contrib.auth.models import User
import datetime

class Job(models.Model):
    sku = models.CharField(max_length=50)  # Store the SKU code here
    sku_code = models.CharField(max_length=50, blank=True, null=True)  # SKU code field
    job_name = models.CharField(max_length=200, blank=True, null=True)  # JC# (Job Code)

    # --- PO-specific fields ---
    po_number = models.CharField(max_length=50)
    po_quantity = models.PositiveIntegerField()
    po_date = models.DateField()
    unit_cost = models.DecimalField(max_digits=10, decimal_places=1)
    stock = models.PositiveIntegerField(blank=True, null=True, help_text="Available stock")
    wastage = models.PositiveIntegerField(blank=True, null=True, help_text="Wastage quantity")
    
    planned_date = models.DateField()
    customer_name = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Status
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed')
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # --- Recipe fields ---
    material_type = models.CharField(max_length=100, blank=True, null=True)
    application_type = models.CharField(max_length=100, blank=True, null=True)
    one_up_width = models.DecimalField(max_digits=6, decimal_places=0, blank=True, null=True)
    one_up_height = models.DecimalField(max_digits=6, decimal_places=0, blank=True, null=True)
    print_sheet_width = models.DecimalField(max_digits=6, decimal_places=0, blank=True, null=True)
    print_sheet_height = models.DecimalField(max_digits=6, decimal_places=0, blank=True, null=True)
    print_sheet_size = models.CharField(max_length=50, blank=True, null=True)
    ups = models.PositiveIntegerField(blank=True, null=True)
    purchase_sheet_width = models.DecimalField(max_digits=6, decimal_places=0, blank=True, null=True)
    purchase_sheet_height = models.DecimalField(max_digits=6, decimal_places=0, blank=True, null=True)
    purchase_sheet_size = models.CharField(max_length=50, blank=True, null=True)
    purchase_ups = models.PositiveIntegerField(blank=True, null=True)

    def save(self, *args, **kwargs):
        # Generate the JC# (Job Code) before saving
        if not self.job_name:  # Ensure JC# is set only if not already set
            currentMonth = datetime.datetime.now().month
            currentYear = datetime.datetime.now().year
            self.job_name = f"JC-{currentMonth}-{currentYear}-{self.pk or '0000'}"

        if self.sku:  # If SKU is provided
            try:
                # Fetch the SKURecipe instance based on the SKU
                sku_recipe = SKURecipe.objects.get(sku_name=self.sku)
                # Populate fields with the fetched recipe's data
                self.sku_code = sku_recipe.sku_code
                self.material_type = sku_recipe.material_type
                self.application_type = sku_recipe.application_type
                self.one_up_width = sku_recipe.one_up_width
                self.one_up_height = sku_recipe.one_up_height
                self.print_sheet_width = sku_recipe.print_sheet_width
                self.print_sheet_height = sku_recipe.print_sheet_height
                self.print_sheet_size = sku_recipe.print_sheet_size
                self.ups = sku_recipe.ups
                self.purchase_sheet_width = sku_recipe.purchase_sheet_width
                self.purchase_sheet_height = sku_recipe.purchase_sheet_height
                self.purchase_sheet_size = sku_recipe.purchase_sheet_size
                self.purchase_ups = sku_recipe.purchase_ups
            except SKURecipe.DoesNotExist:
                raise ValueError("The specified SKU does not have an associated recipe.")
        
        # Ensure stock and wastage are integers or set them to 0 if empty
        if self.stock is None:
            self.stock = 0
        if self.wastage is None:
            self.wastage = 0

        super().save(*args, **kwargs)

    def mark_as_completed(self):
        self.status = 'completed'
        self.save()

    def mark_as_in_progress(self):
        self.status = 'in_progress'
        self.save()

    def __str__(self):
        return f"JC#{self.job_name} - {self.sku_code}"
