from django.db import models
from django.contrib.auth.models import User

STATUS_CHOICES = [
    ('success', 'Успішно'),
    ('error', 'Помилка'),
]


class FileUploadLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='upload_logs')
    filename = models.CharField(max_length=500)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    error_type = models.CharField(max_length=1000, blank=True, default='')

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Лог завантаження'

    def __str__(self):
        return f"{self.filename} — {self.status}"


class DataRecord(models.Model):
    advertiser = models.CharField(max_length=500)
    brand = models.CharField(max_length=500)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    format = models.CharField(max_length=500)
    platform = models.CharField(max_length=500)
    impr = models.BigIntegerField(default=0)
    year = models.IntegerField(null=True, blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='data_records')
    upload_log = models.ForeignKey(FileUploadLog, on_delete=models.CASCADE, related_name='records')

    class Meta:
        ordering = ['-year', 'advertiser']
        verbose_name = 'Запис даних'

    def __str__(self):
        return f"{self.advertiser} / {self.brand} ({self.year})"
