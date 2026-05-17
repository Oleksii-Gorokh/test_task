from django.urls import path
from . import views, admin_views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('upload/', views.upload_file, name='upload'),
    path('stats/', views.stats, name='stats'),
    path('admin-panel/', admin_views.admin_panel, name='admin_panel'),
    path('admin-panel/logs/', admin_views.file_logs, name='file_logs'),
    path('admin-panel/access/', admin_views.access_status, name='access_status'),
    path('admin-panel/data/', admin_views.full_data, name='full_data'),
]
