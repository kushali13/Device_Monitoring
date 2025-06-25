from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('monitor.urls')),
    path('admin-site/', include('admin_ui.urls')),  # Custom admin site

]
