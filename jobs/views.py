from django.shortcuts import render, redirect,get_object_or_404
from .forms import JobForm
from .models import Job
from recipes.models import SKURecipe
from django.http import JsonResponse


# Home view (formerly Dashboard)
def home(request):
    jobs = Job.objects.all()  # Get all jobs
    recent_jobs = jobs[:5]  # Get the most recent 5 jobs
    jobs_count = jobs.count()  # Total number of jobs
    sku_recipes = SKURecipe.objects.all()  # Fetch all recipes
    return render(request, 'home.html', {
        'jobs_count': jobs_count,
        'recent_jobs': recent_jobs,
        'sku_recipes': sku_recipes,
    })

# Job list view
def job_list(request):
    jobs = Job.objects.all()  # Get all jobs
    return render(request, 'jobs/job_list.html', {'jobs': jobs})


def job_create(request):
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            # Get SKU based on SKU field
            sku_value = form.cleaned_data.get('sku')
            try:
                # Fetch the SKURecipe instance based on the SKU
                sku_recipe = SKURecipe.objects.get(sku_name=sku_value)
                # Populate the sku_code field with the fetched recipe's sku_code
                form.instance.sku_code = sku_recipe.sku_code
                form.instance.material_type = sku_recipe.material_type
                form.instance.application_type = sku_recipe.application_type
                form.instance.one_up_width = sku_recipe.one_up_width
                form.instance.one_up_height = sku_recipe.one_up_height
                form.instance.print_sheet_width = sku_recipe.print_sheet_width
                form.instance.print_sheet_height = sku_recipe.print_sheet_height
                form.instance.print_sheet_size = sku_recipe.print_sheet_size
                form.instance.ups = sku_recipe.ups
                form.instance.purchase_sheet_width = sku_recipe.purchase_sheet_width
                form.instance.purchase_sheet_height = sku_recipe.purchase_sheet_height
                form.instance.purchase_sheet_size = sku_recipe.purchase_sheet_size
                form.instance.purchase_ups = sku_recipe.purchase_ups
            except SKURecipe.DoesNotExist:
                form.add_error('sku', 'SKU does not exist.')
                return render(request, 'jobs/job_create.html', {'form': form})

            # Save the job after ensuring all fields are populated
            form.save()
            return redirect('job-list')  # Redirect to the job list after successful creation
    else:
        form = JobForm()
    
    return render(request, 'jobs/job_create.html', {'form': form})

def fetch_recipe(request):
    sku = request.GET.get('sku', None)
    if not sku:
        return JsonResponse({'error': 'No SKU provided'}, status=400)

    try:
        # Fetch the SKURecipe instance based on the SKU
        recipe = SKURecipe.objects.get(sku_name=sku)
        # Prepare the data to be returned as a JSON response
        data = {
            'sku_code': recipe.sku_code,
            'material_type': recipe.material_type,
            'application_type': recipe.application_type,
            'one_up_width': str(recipe.one_up_width),
            'one_up_height': str(recipe.one_up_height),
            'print_sheet_width': str(recipe.print_sheet_width),
            'print_sheet_height': str(recipe.print_sheet_height),
            'print_sheet_size': recipe.print_sheet_size,
            'ups': recipe.ups,
            'purchase_sheet_width': str(recipe.purchase_sheet_width),
            'purchase_sheet_height': str(recipe.purchase_sheet_height),
            'purchase_sheet_size': recipe.purchase_sheet_size,
            'purchase_ups': recipe.purchase_ups,
        }
        return JsonResponse(data)
    except SKURecipe.DoesNotExist:
        return JsonResponse({'error': 'SKU not found'}, status=404)
    

def job_edit(request, pk):
    job = get_object_or_404(Job, pk=pk)  # Get the job by its primary key (ID)
    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)  # Prepopulate the form with existing job data
        if form.is_valid():
            sku_value = form.cleaned_data.get('sku')
            try:
                # Fetch the SKURecipe instance based on the SKU
                sku_recipe = SKURecipe.objects.get(sku_name=sku_value)
                # Populate the sku_code and related fields with the fetched recipe's data
                job.sku_code = sku_recipe.sku_code
                job.material_type = sku_recipe.material_type
                job.application_type = sku_recipe.application_type
                job.one_up_width = sku_recipe.one_up_width
                job.one_up_height = sku_recipe.one_up_height
                job.print_sheet_width = sku_recipe.print_sheet_width
                job.print_sheet_height = sku_recipe.print_sheet_height
                job.print_sheet_size = sku_recipe.print_sheet_size
                job.ups = sku_recipe.ups
                job.purchase_sheet_width = sku_recipe.purchase_sheet_width
                job.purchase_sheet_height = sku_recipe.purchase_sheet_height
                job.purchase_sheet_size = sku_recipe.purchase_sheet_size
                job.purchase_ups = sku_recipe.purchase_ups
            except SKURecipe.DoesNotExist:
                form.add_error('sku', 'SKU does not exist.')
                return render(request, 'jobs/job_edit.html', {'form': form, 'job': job})

            form.save()  # Save the updated job data
            return redirect('job-list')  # Redirect to the job list after successful update
    else:
        form = JobForm(instance=job)  # Prepopulate the form with the existing job data
    
    return render(request, 'jobs/job_edit.html', {'form': form, 'job': job})

def job_delete(request, pk):
    job = get_object_or_404(Job, pk=pk)
    job.delete()  # Delete the job
    return redirect('job-list')  # Redirect to the job list after successful deletion