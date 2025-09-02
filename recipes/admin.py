from django.contrib import admin
from .models import SKURecipe

@admin.register(SKURecipe)
class SKURecipeAdmin(admin.ModelAdmin):
    list_display = ("sku_code", "sku_name", "material_type", "application_type", "ups", "purchase_ups", "created_at")
    search_fields = ("sku_code", "sku_name", "material_type", "application_type")
    list_filter = ("material_type", "application_type")
