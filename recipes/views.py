import csv
import io
import openpyxl
import pandas as pd
import re
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib import messages
from django.http import HttpResponse
from .models import SKURecipe
from .forms import SKURecipeForm, BulkUploadForm
from decimal import Decimal, InvalidOperation
from django.views.decorators.http import require_POST

# ------------------------
# Home Page
# ------------------------
def home(request):
    return render(request, "home.html")


# ------------------------
# List View with Search
# ------------------------
def sku_list(request):
    query = request.GET.get("q", "")
    if query:
        skus = SKURecipe.objects.filter(
            Q(sku_name__icontains=query) | Q(sku_code__icontains=query)
        )
    else:
        skus = SKURecipe.objects.all()
    return render(request, "recipes/sku_list.html", {"skus": skus, "query": query})


# ------------------------
# Create SKU
# ------------------------
def sku_create(request):
    if request.method == "POST":
        form = SKURecipeForm(request.POST)
        if form.is_valid():
            try:
                obj = form.save(commit=False)

                # ✅ Ensure auto sku_code generation if your model uses it
                if not obj.sku_code:
                    from django.utils.crypto import get_random_string
                    obj.sku_code = f"SKU-{get_random_string(6).upper()}"

                obj.save()
                messages.success(request, f"SKU {obj.sku_code} created successfully!")
                print("✅ SKU saved successfully:", obj.sku_code)  # Debug log
                return redirect("sku-list")

            except Exception as e:
                print("❌ Error while saving SKU:", str(e))  # Debug log
                messages.error(request, f"Error while saving: {str(e)}")
        else:
            print("❌ Form validation errors:", form.errors)  # Debug log
            messages.error(request, "Please correct the errors below.")
    else:
        form = SKURecipeForm()

    return render(request, "recipes/sku_form.html", {"form": form})



# ------------------------
# Edit SKU
# ------------------------
def sku_edit(request, pk):
    sku = get_object_or_404(SKURecipe, pk=pk)
    if request.method == "POST":
        form = SKURecipeForm(request.POST, instance=sku)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "SKU Recipe updated successfully!")
                return redirect("sku-list")
            except Exception as e:
                messages.error(request, f"Error: {str(e)}")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SKURecipeForm(instance=sku)
    return render(request, "recipes/sku_form.html", {"form": form})


# ------------------------
# Delete SKU
# ------------------------
def sku_delete(request, pk):
    sku = get_object_or_404(SKURecipe, pk=pk)
    if request.method == "POST":
        sku.delete()
        messages.success(request, "SKU Recipe deleted successfully!")
        return redirect("sku-list")
    return render(request, "recipes/sku_confirm_delete.html", {"sku": sku})


# ------------------------
# Helpers
# ------------------------
def _parse_decimal(value, field_name="value"):
    """Try to parse a value into Decimal. Reject WxH strings."""
    if pd.isna(value) or str(value).strip() == "":
        return None

    val = str(value).strip()

    # Prevent WxH strings being passed here
    if any(x in val.lower() for x in ["x", "×", "*"]):
        raise ValueError(f"Invalid {field_name}: '{value}' looks like WxH, expected a number only")

    try:
        return Decimal(val.replace(",", "."))
    except (InvalidOperation, ValueError):
        raise ValueError(f"Invalid {field_name}: '{value}' must be a decimal number")


def _parse_sheet_fields(width, height, size, field_name="sheet"):
    """
    Decide whether to store as width/height or size string.
    Allows formats like '12.5x11' or '12.5*11' in either width/height or size column.
    """
    # Case 1: If size string is provided
    if pd.notna(size) and str(size).strip() != "":
        val = str(size).replace("×", "x").replace("*", "x").strip()
        if "x" in val.lower():
            parts = re.split(r"[x]", val)
            if len(parts) == 2:
                return _parse_decimal(parts[0], f"{field_name}_width"), _parse_decimal(parts[1], f"{field_name}_height"), None
            return None, None, val  # fallback: keep as string
        else:
            return _parse_decimal(val, f"{field_name}_size"), None, None

    # Case 2: Width/Height provided separately
    if pd.notna(width) and isinstance(width, str) and any(x in width for x in ["x", "×", "*"]):
        parts = re.split(r"[x*×]", width)
        if len(parts) == 2:
            return _parse_decimal(parts[0], f"{field_name}_width"), _parse_decimal(parts[1], f"{field_name}_height"), None

    if pd.notna(height) and isinstance(height, str) and any(x in height for x in ["x", "×", "*"]):
        parts = re.split(r"[x*×]", height)
        if len(parts) == 2:
            return _parse_decimal(parts[0], f"{field_name}_width"), _parse_decimal(parts[1], f"{field_name}_height"), None

    # Normal case
    w = _parse_decimal(width, f"{field_name}_width") if pd.notna(width) else None
    h = _parse_decimal(height, f"{field_name}_height") if pd.notna(height) else None
    return w, h, None



# ------------------------
# Bulk Upload SKUs
# ------------------------
def bulk_upload(request):
    if request.method == "POST":
        form = BulkUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES["file"]
            file_ext = file.name.split(".")[-1].lower()

            try:
                # Read CSV or Excel into DataFrame
                if file_ext == "csv":
                    df = pd.read_csv(file)
                elif file_ext in ["xls", "xlsx"]:
                    df = pd.read_excel(file)
                else:
                    messages.error(request, "Unsupported file format. Upload CSV or Excel only.")
                    return redirect("bulk-upload")

                # Required minimal columns
                required_cols = [
                    "sku_name", "material_type", "application_type",
                    "one_up_width", "one_up_height",
                    "ups", "purchase_ups"
                ]
                missing_cols = [col for col in required_cols if col not in df.columns]
                if missing_cols:
                    messages.error(request, f"Missing required columns: {', '.join(missing_cols)}")
                    return redirect("bulk-upload")

                # Add Error column
                df["Error"] = ""

                # Get last used SKU number
                last_sku = SKURecipe.objects.order_by("-id").first()
                last_number = 0
                if last_sku:
                    try:
                        last_number = int(last_sku.sku_code.replace("SKU-", ""))
                    except Exception:
                        last_number = 0

                # Process each row
                for idx, row in df.iterrows():
                    try:
                        row_errors = []

                        # Check duplicate SKU Name
                        if SKURecipe.objects.filter(sku_name=row["sku_name"]).exists():
                            row_errors.append("SKU name already exists")
                            df.at[idx, "Error"] = f"Row {idx+2}: {', '.join(row_errors)}"
                            continue

                        # Generate next SKU code
                        last_number += 1
                        sku_code = f"SKU-{last_number:04d}"

                        # Parse fields safely
                        try:
                            one_up_width = _parse_decimal(row["one_up_width"], "one_up_width")
                        except ValueError as e:
                            row_errors.append(str(e))
                            one_up_width = None

                        try:
                            one_up_height = _parse_decimal(row["one_up_height"], "one_up_height")
                        except ValueError as e:
                            row_errors.append(str(e))
                            one_up_height = None

                        # Handle Print Sheet
                        try:
                            print_w, print_h, print_size = _parse_sheet_fields(
                                row.get("print_sheet_width"),
                                row.get("print_sheet_height"),
                                row.get("print_sheet_size"),
                                field_name="print_sheet"
                            )
                        except ValueError as e:
                            row_errors.append(str(e))
                            print_w, print_h, print_size = None, None, None

                        # Handle Purchase Sheet
                        try:
                            purchase_w, purchase_h, purchase_size = _parse_sheet_fields(
                                row.get("purchase_sheet_width"),
                                row.get("purchase_sheet_height"),
                                row.get("purchase_sheet_size"),
                                field_name="purchase_sheet"
                            )
                        except ValueError as e:
                            row_errors.append(str(e))
                            purchase_w, purchase_h, purchase_size = None, None, None

                        # If any errors → mark row and skip creation
                        if row_errors:
                            df.at[idx, "Error"] = f"Row {idx+2}: {', '.join(row_errors)}"
                            continue

                        # Create SKU
                        SKURecipe.objects.create(
                            sku_code=sku_code,
                            sku_name=row["sku_name"],
                            material_type=row["material_type"],
                            application_type=row["application_type"],
                            one_up_width=one_up_width,
                            one_up_height=one_up_height,
                            ups=int(row["ups"]) if pd.notna(row["ups"]) else 0,

                            # Print sheet
                            print_sheet_width=print_w,
                            print_sheet_height=print_h,
                            print_sheet_size=print_size,

                            # Purchase sheet
                            purchase_sheet_width=purchase_w,
                            purchase_sheet_height=purchase_h,
                            purchase_sheet_size=purchase_size,

                            purchase_ups=int(row["purchase_ups"]) if pd.notna(row["purchase_ups"]) else 0,
                        )

                    except Exception as e:
                        df.at[idx, "Error"] = f"Row {idx+2}: Unexpected error → {str(e)}"

                # If any errors → return error Excel
                if (df["Error"].str.strip() != "").any():
                    response = HttpResponse(
                        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                    response["Content-Disposition"] = 'attachment; filename="bulk_upload_results.xlsx"'
                    df.to_excel(response, index=False)
                    return response

                messages.success(request, "Bulk upload completed successfully!")
                return redirect("bulk-upload")

            except Exception as e:
                messages.error(request, f"Error processing file: {str(e)}")
                return redirect("bulk-upload")
    else:
        form = BulkUploadForm()

    return render(request, "recipes/bulk_upload.html", {"form": form})

# ------------------------
# Download Sample CSV
# ------------------------
def download_sample_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="sample_recipes.csv"'

    writer = csv.writer(response)
    writer.writerow([
        "sku_name", "material_type", "application_type",
        "one_up_width", "one_up_height",
        "print_sheet_width", "print_sheet_height", "ups",
        "purchase_sheet_width", "purchase_sheet_height", "purchase_ups",
    ])
    writer.writerow([
        "Clothing Tag", "Art Paper", "Lamination",
        50.00, 70.00,
        500.00, 700.00, 49,
        23.00, 35.00, 6,
    ])
    return response


# ------------------------
# Download Sample Excel
# ------------------------
def download_sample_excel(request):
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Recipes"

    headers = [
        "sku_name", "material_type", "application_type",
        "one_up_width", "one_up_height",
        "print_sheet_width", "print_sheet_height", "ups",
        "purchase_sheet_width", "purchase_sheet_height", "purchase_ups",
    ]
    sheet.append(headers)

    sheet.append([
        "Clothing Tag", "Art Paper", "Lamination",
        50.00, 70.00,
        500.00, 700.00, 49,
        23.00, 35.00, 6,
    ])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="sample_recipes.xlsx"'
    workbook.save(response)
    return response






def bulk_actions(request):
    if request.method == "POST":
        selected_ids = request.POST.getlist("selected_skus")
        action = request.POST.get("action")

        if not selected_ids:
            return redirect("sku-list")

        queryset = SKURecipe.objects.filter(pk__in=selected_ids)

        if action == "delete":
            queryset.delete()
            return redirect("sku-list")

        elif action == "download":
            # Export to CSV
            response = HttpResponse(content_type="text/csv")
            response["Content-Disposition"] = 'attachment; filename="selected_skus.csv"'

            writer = csv.writer(response)
            writer.writerow([
                "SKU Code", "SKU Name", "Material", "Application",
                "1-Up Width", "1-Up Height",
                "Print Sheet Width", "Print Sheet Height", "UPS",
                "Purchase Sheet Width", "Purchase Sheet Height", "Purchase UPS",
                "Created At"
            ])

            for sku in queryset:
                writer.writerow([
                    sku.sku_code, sku.sku_name, sku.material_type, sku.application_type,
                    sku.one_up_width, sku.one_up_height,
                    sku.print_sheet_width, sku.print_sheet_height, sku.ups,
                    sku.purchase_sheet_width, sku.purchase_sheet_height, sku.purchase_ups,
                    sku.created_at.strftime("%Y-%m-%d %H:%M"),
                ])
            return response

    return redirect("sku-list")