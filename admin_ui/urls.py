from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='admin_home'),
    path('insert/', views.insert_view, name='insert'),
    path('update/', views.update_view, name='update'),
    path('delete/', views.delete_view, name='delete'),
    path('delete-data/', views.delete_data, name='delete_data'),
    path('load-school-data/', views.load_school_data, name='load_school_data'),
    path('loadUpdate-school-data/', views.loadUpdate_school_data, name='loadUpdate_school_data'),
    path('insert-data/', views.insert_data, name='insert_data'), # <--- Add this
    path('update-data/',views.update_data,name='update_data'),
    
]
