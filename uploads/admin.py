from django.contrib import admin
from .models import FileUploadLog, DataRecord

admin.site.register(FileUploadLog)
admin.site.register(DataRecord)
