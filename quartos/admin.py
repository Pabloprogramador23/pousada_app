from django.contrib import admin
from .models import Quarto

@admin.register(Quarto)
class QuartoAdmin(admin.ModelAdmin):
    list_display = ('numero', 'tem_ventilador')
    list_filter = ('tem_ventilador',)
    search_fields = ('numero',)
