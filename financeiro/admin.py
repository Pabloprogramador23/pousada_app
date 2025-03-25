from django.contrib import admin
from .models import Pagamento, Despesa, Receita, Alerta

@admin.register(Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
    """
    Configuração do admin para o modelo Pagamento.
    """
    list_display = ('id', 'reserva', 'valor', 'tipo', 'status', 'data_pagamento')
    list_filter = ('status', 'tipo', 'data_pagamento')
    search_fields = ('reserva__codigo', 'reserva__hospede__nome', 'valor')
    date_hierarchy = 'data_pagamento'
    readonly_fields = ('data_criacao', 'data_atualizacao')
    
    fieldsets = (
        ('Informações de Pagamento', {
            'fields': ('reserva', 'valor', 'tipo', 'status')
        }),
        ('Detalhes do Pagamento', {
            'fields': ('data_pagamento', 'codigo_transacao', 'comprovante', 'observacoes')
        }),
        ('Informações do Sistema', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Despesa)
class DespesaAdmin(admin.ModelAdmin):
    """
    Configuração do admin para o modelo Despesa.
    """
    list_display = ('id', 'descricao', 'valor', 'categoria', 'status', 'data_despesa', 'data_vencimento')
    list_filter = ('categoria', 'status', 'data_despesa', 'data_vencimento')
    search_fields = ('descricao', 'observacoes')
    date_hierarchy = 'data_vencimento'
    readonly_fields = ('data_criacao', 'data_atualizacao')
    
    fieldsets = (
        ('Informações da Despesa', {
            'fields': ('descricao', 'valor', 'categoria', 'status')
        }),
        ('Datas', {
            'fields': ('data_despesa', 'data_vencimento', 'data_pagamento')
        }),
        ('Detalhes Adicionais', {
            'fields': ('comprovante', 'observacoes')
        }),
        ('Informações do Sistema', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )
    actions = ['marcar_como_pago']
    
    def marcar_como_pago(self, request, queryset):
        import datetime
        rows_updated = queryset.update(status='pago', data_pagamento=datetime.date.today())
        if rows_updated == 1:
            message_bit = "1 despesa foi"
        else:
            message_bit = f"{rows_updated} despesas foram"
        self.message_user(request, f"{message_bit} marcada(s) como paga(s).")
    marcar_como_pago.short_description = "Marcar despesas selecionadas como pagas"

@admin.register(Receita)
class ReceitaAdmin(admin.ModelAdmin):
    list_display = ('id', 'descricao', 'valor', 'categoria', 'status', 'data_receita', 'recorrente')
    list_filter = ('categoria', 'status', 'data_receita', 'recorrente')
    search_fields = ('descricao', 'observacoes')
    date_hierarchy = 'data_receita'
    readonly_fields = ('data_criacao', 'data_atualizacao')
    fieldsets = (
        ('Informações da Receita', {
            'fields': ('descricao', 'valor', 'categoria', 'status', 'recorrente')
        }),
        ('Datas', {
            'fields': ('data_receita', 'data_recebimento')
        }),
        ('Detalhes Adicionais', {
            'fields': ('comprovante', 'observacoes')
        }),
        ('Informações do Sistema', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )
    actions = ['marcar_como_recebido']
    
    def marcar_como_recebido(self, request, queryset):
        import datetime
        rows_updated = queryset.update(status='recebido', data_recebimento=datetime.date.today())
        if rows_updated == 1:
            message_bit = "1 receita foi"
        else:
            message_bit = f"{rows_updated} receitas foram"
        self.message_user(request, f"{message_bit} marcada(s) como recebida(s).")
    marcar_como_recebido.short_description = "Marcar receitas selecionadas como recebidas"

@admin.register(Alerta)
class AlertaAdmin(admin.ModelAdmin):
    list_display = ('id', 'titulo', 'tipo', 'prioridade', 'data_criacao', 'visualizado', 'resolvido')
    list_filter = ('tipo', 'prioridade', 'visualizado', 'resolvido', 'data_criacao')
    search_fields = ('titulo', 'mensagem')
    date_hierarchy = 'data_criacao'
    readonly_fields = ('data_criacao', 'data_resolucao')
    fieldsets = (
        ('Informações do Alerta', {
            'fields': ('titulo', 'mensagem', 'tipo', 'prioridade')
        }),
        ('Referências', {
            'fields': ('reserva', 'despesa', 'receita')
        }),
        ('Status', {
            'fields': ('visualizado', 'resolvido', 'data_vencimento', 'data_resolucao')
        }),
        ('Informações do Sistema', {
            'fields': ('data_criacao',),
            'classes': ('collapse',)
        }),
    )
    actions = ['marcar_como_resolvido', 'marcar_como_visualizado']
    
    def marcar_como_resolvido(self, request, queryset):
        for alerta in queryset:
            alerta.marcar_como_resolvido()
        if queryset.count() == 1:
            message_bit = "1 alerta foi"
        else:
            message_bit = f"{queryset.count()} alertas foram"
        self.message_user(request, f"{message_bit} marcado(s) como resolvido(s).")
    marcar_como_resolvido.short_description = "Marcar alertas selecionados como resolvidos"
    
    def marcar_como_visualizado(self, request, queryset):
        rows_updated = queryset.update(visualizado=True)
        if rows_updated == 1:
            message_bit = "1 alerta foi"
        else:
            message_bit = f"{rows_updated} alertas foram"
        self.message_user(request, f"{message_bit} marcado(s) como visualizado(s).")
    marcar_como_visualizado.short_description = "Marcar alertas selecionados como visualizados"
