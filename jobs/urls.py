from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Home view (formerly Dashboard)
    path('jobs/create/', views.job_create, name='job-create'),  # Job creation page
    path('jobs/', views.job_list, name='job-list'),  # List of all jobs
    path('fetch-recipe/', views.fetch_recipe, name='fetch_recipe'),  # Fetch recipe via SKU
    path('jobs/<int:pk>/edit/', views.job_edit, name='job-edit'),  # Edit job
    path('jobs/<int:pk>/delete/', views.job_delete, name='job-delete'),  # Delete job
    path('get_last_job_code/', views.get_last_job_code, name='get_last_job_code'), # Last job card
]

