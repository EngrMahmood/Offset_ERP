from django.db import models
from decimal import Decimal, InvalidOperation
import re


class SKURecipe(models.Model):
    sku_code = models.CharField(max_length=50, unique=True, editable=False)  # auto-generated
    sku_name = models.CharField(max_length=200, unique=True)  # key field

    material_type = models.CharField(max_length=100)
    application_type = models.CharField(max_length=100)

    one_up_width = models.DecimalField(max_digits=6, decimal_places=2, help_text="Width in mm")
    one_up_height = models.DecimalField(max_digits=6, decimal_places=2, help_text="Height in mm")

    # --- Print Sheet ---
    print_sheet_width = models.DecimalField(max_digits=6, decimal_places=2, help_text="Width in mm", null=True, blank=True)
    print_sheet_height = models.DecimalField(max_digits=6, decimal_places=2, help_text="Height in mm", null=True, blank=True)
    print_sheet_size = models.CharField(max_length=50, blank=True, null=True, help_text="Format: WxH (optional)")

    ups = models.PositiveIntegerField(help_text="How many 1-ups fit in print sheet")

    # --- Purchase Sheet ---
    purchase_sheet_width = models.DecimalField(max_digits=6, decimal_places=2, help_text="Width in inches", null=True, blank=True)
    purchase_sheet_height = models.DecimalField(max_digits=6, decimal_places=2, help_text="Height in inches", null=True, blank=True)
    purchase_sheet_size = models.CharField(max_length=50, blank=True, null=True, help_text="Format: WxH (optional)")

    purchase_ups = models.PositiveIntegerField(help_text="How many ups fit in purchase sheet")

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Auto-generate sequential SKU code
        if not self.sku_code:
            last_obj = SKURecipe.objects.order_by("-created_at").first()
            if last_obj and last_obj.sku_code.startswith("SKU-"):
                try:
                    last_number = int(last_obj.sku_code.replace("SKU-", ""))
                except ValueError:
                    last_number = 0
            else:
                last_number = 0
            self.sku_code = f"SKU-{last_number + 1:04d}"

        # Parse print sheet size if WxH string is provided
        if self.print_sheet_size and (not self.print_sheet_width or not self.print_sheet_height):
            try:
                w, h = self._parse_size(self.print_sheet_size)
                self.print_sheet_width = w
                self.print_sheet_height = h
            except Exception:
                pass

        # Parse purchase sheet size if WxH string is provided
        if self.purchase_sheet_size and (not self.purchase_sheet_width or not self.purchase_sheet_height):
            try:
                w, h = self._parse_size(self.purchase_sheet_size)
                self.purchase_sheet_width = w
                self.purchase_sheet_height = h
            except Exception:
                pass

        super().save(*args, **kwargs)

    def _parse_size(self, value):
        """Parse WxH string into Decimal tuple"""
        if not value:
            raise ValueError("Empty size value")
        cleaned = value.lower().replace("×", "x").replace("*", "x")
        parts = re.split(r"[x]", cleaned)
        if len(parts) != 2:
            raise ValueError(f"'{value}' not in WxH format")
        try:
            return Decimal(parts[0].strip()), Decimal(parts[1].strip())
        except InvalidOperation:
            raise ValueError(f"'{value}' contains invalid numbers")

    def __str__(self):
        return f"{self.sku_code} - {self.sku_name}"
