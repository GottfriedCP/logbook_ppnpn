from django.contrib import admin
from . import models


@admin.register(models.Catatan)
class CatatanAdmin(admin.ModelAdmin):
    pass
