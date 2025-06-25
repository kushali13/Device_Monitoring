from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_login, name='login'),
    path('login/', views.index, name='index'),
    path('regInfo/', views.regInfo, name='regInfo'),
    path('school/', views.school, name='school'),
    path('livestatus/', views.livestatus, name='livestatus'),
    path('schoolLogs/', views.schoolLogs, name='schoolLogs'),
    path('reportDevicetime/', views.reportDevicetime, name='reportDevicetime'),
    path('reportActivitytime/', views.reportActivitytime, name='reportActivitytime'),
    path('download_csv_device/', views.download_csv_device, name='download_csv_device'),
    path('download_csv_activity/', views.download_csv_activity, name='download_csv_activity'),
    path('download_csv_asset/', views.download_csv_asset, name='download_csv_asset'),
    path('download_pdf_device/', views.download_pdf_device, name='download_pdf_device'),
    path('download_pdf_activity/', views.download_pdf_activity, name='download_pdf_activity'),

]
