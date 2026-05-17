from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from .models import FileUploadLog, DataRecord
from .utils import read_file, parse_dataframe


@login_required
def dashboard(request):
    return render(request, 'uploads/dashboard.html')


@login_required
def upload_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        filename = file.name
        df, read_error = read_file(file, filename)
        if read_error:
            FileUploadLog.objects.create(
                user=request.user,
                filename=filename,
                status='error',
                error_type=read_error,
            )
            messages.error(request, read_error)
            return render(request, 'uploads/upload.html')
        records, parse_error = parse_dataframe(df)
        if parse_error:
            FileUploadLog.objects.create(
                user=request.user,
                filename=filename,
                status='error',
                error_type=parse_error,
            )
            messages.error(request, parse_error)
            return render(request, 'uploads/upload.html')
        log = FileUploadLog.objects.create(
            user=request.user,
            filename=filename,
            status='success',
            error_type='',
        )
        DataRecord.objects.bulk_create([
            DataRecord(
                advertiser=r['advertiser'],
                brand=r['brand'],
                start_date=r['start_date'],
                end_date=r['end_date'],
                format=r['format'],
                platform=r['platform'],
                impr=r['impr'],
                year=r['year'],
                uploaded_by=request.user,
                upload_log=log,
            )
            for r in records
        ])
        messages.success(request, f'Файл успішно завантажено. Оброблено записів: {len(records)}')
        return redirect('stats')
    return render(request, 'uploads/upload.html')


@login_required
def stats(request):
    stats_data = (
        DataRecord.objects
        .filter(year__isnull=False)
        .values('year')
        .annotate(total_impr=Sum('impr'))
        .order_by('year')
    )
    total = DataRecord.objects.count()
    return render(request, 'uploads/stats.html', {'stats': stats_data, 'total': total})
