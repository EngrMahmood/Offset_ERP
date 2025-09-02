from django.contrib import admin
from django.urls import path, include
from recipes import views as recipe_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", recipe_views.home, name="home"),   # ✅ Clean home page with tabs
    path("recipes/", include("recipes.urls")), # ✅ Recipes app URLs
]
