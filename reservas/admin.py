from django.contrib import admin
from .models import Reserva

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = (
        'cliente',
        'quarto',
        'data_checkin',
        'data_checkout',
        'numero_pessoas',
        'confirmado',
        'pago_50',
        'valor_total',
    )
    list_filter = ('confirmado', 'pago_50', 'quarto')
    search_fields = ('cliente__nome', 'quarto__numero')
    ordering = ('-data_checkin',)
