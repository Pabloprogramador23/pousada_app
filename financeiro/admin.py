from django.contrib import admin
from .models import Pagamento, Despesa

@admin.register(Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
    """
    Configuração do admin para o modelo Pagamento.
    """
    list_display = ('id', 'reserva', 'valor', 'tipo', 'status', 'data_pagamento')
    list_filter = ('status', 'tipo', 'data_pagamento')
    search_fields = ('reserva__codigo', 'reserva__hospede__nome', 'observacoes')
    list_editable = ('status',)
    readonly_fields = ('data_criacao', 'data_atualizacao')
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('reserva', 'valor', 'tipo', 'status')
        }),
        ('Detalhes do Pagamento', {
            'fields': ('data_pagamento', 'codigo_transacao', 'comprovante')
        }),
        ('Observações', {
            'fields': ('observacoes',)
        }),
        ('Controle', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Despesa)
class DespesaAdmin(admin.ModelAdmin):
    """
    Configuração do admin para o modelo Despesa.
    """
    list_display = ('id', 'descricao', 'valor', 'categoria', 'data_despesa', 'data_pagamento')
    list_filter = ('categoria', 'data_despesa', 'data_pagamento')
    search_fields = ('descricao', 'observacoes')
    readonly_fields = ('data_criacao', 'data_atualizacao')
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('descricao', 'valor', 'categoria')
        }),
        ('Datas', {
            'fields': ('data_despesa', 'data_pagamento')
        }),
        ('Detalhes', {
            'fields': ('comprovante', 'observacoes')
        }),
        ('Controle', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )
