from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import FileUploadLog, DataRecord
from accounts.models import UserProfile


def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        try:
            if not request.user.profile.is_admin():
                return redirect('dashboard')
        except Exception:
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


@admin_required
def admin_panel(request):
    context = {
        'total_files': FileUploadLog.objects.count(),
        'total_records': DataRecord.objects.count(),
        'total_users': UserProfile.objects.count(),
        'errors': FileUploadLog.objects.filter(status='error').count(),
    }
    return render(request, 'uploads/admin/panel.html', context)


@admin_required
def file_logs(request):
    logs = FileUploadLog.objects.select_related('user').all()
    return render(request, 'uploads/admin/file_logs.html', {'logs': logs})


@admin_required
def access_status(request):
    profiles = UserProfile.objects.select_related('user').all()
    return render(request, 'uploads/admin/access_status.html', {'profiles': profiles})


@admin_required
def full_data(request):
    records = DataRecord.objects.select_related('uploaded_by', 'upload_log').all()
    return render(request, 'uploads/admin/full_data.html', {'records': records})
