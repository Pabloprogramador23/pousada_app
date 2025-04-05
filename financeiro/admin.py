from django.contrib import admin
from .models import Despesa, EntradaExtra
from django.db.models import Sum
from django.utils.html import format_html
from datetime import datetime


@admin.register(Despesa)
class DespesaAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'valor', 'data', 'descricao')
    list_filter = ('tipo', 'data')
    search_fields = ('descricao',)


@admin.register(EntradaExtra)
class EntradaExtraAdmin(admin.ModelAdmin):
    list_display = ('origem', 'valor', 'data', 'descricao')
    list_filter = ('origem', 'data')
    search_fields = ('descricao',)

    change_list_template = 'admin/financeiro/entradaextra_change_list.html'

    def changelist_view(self, request, extra_context=None):
        # Get year and month from query
        try:
            year = int(request.GET.get('year', datetime.today().year))
            month = int(request.GET.get('month', datetime.today().month))
        except (ValueError, TypeError):
            year = datetime.today().year
            month = datetime.today().month

        despesas_total = Despesa.objects.filter(
            data__year=year, data__month=month
        ).aggregate(total=Sum('valor'))['total'] or 0

        entradas_total = EntradaExtra.objects.filter(
            data__year=year, data__month=month
        ).aggregate(total=Sum('valor'))['total'] or 0

        saldo = entradas_total - despesas_total

        extra_context = extra_context or {}
        extra_context['entradas'] = entradas_total
        extra_context['despesas'] = despesas_total
        extra_context['saldo'] = saldo
        extra_context['ano'] = year
        extra_context['mes'] = month

        return super().changelist_view(request, extra_context=extra_context)
