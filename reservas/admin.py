from django.contrib import admin
from .models import Reserva, Historico

class HistoricoInline(admin.TabularInline):
    """
    Inline para exibir o histórico de alterações da reserva na página de administração.
    """
    model = Historico
    extra = 0
    readonly_fields = ['data_hora', 'status_anterior', 'status_novo', 'descricao']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    """
    Configuração do admin para o modelo Reserva.
    """
    list_display = ('codigo', 'hospede', 'quarto', 'check_in', 'check_out', 'status', 'valor_total')
    list_filter = ('status', 'origem', 'check_in', 'check_out')
    search_fields = ('codigo', 'hospede__nome', 'quarto__numero', 'observacoes')
    list_editable = ('status',)
    readonly_fields = ('codigo', 'data_criacao', 'data_atualizacao')
    inlines = [HistoricoInline]
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('codigo', 'hospede', 'quarto')
        }),
        ('Período', {
            'fields': ('check_in', 'check_out', 'hora_checkin', 'hora_checkout')
        }),
        ('Status e Origem', {
            'fields': ('status', 'origem', 'data_cancelamento')
        }),
        ('Valores', {
            'fields': ('valor_diaria', 'valor_total', 'valor_sinal')
        }),
        ('Observações', {
            'fields': ('observacoes', 'observacoes_admin', 'solicitacoes_especiais')
        }),
        ('Controle', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """
        Sobrescreve o método save_model para registrar alterações no histórico.
        """
        if change and 'status' in form.changed_data:
            # Registra a alteração de status no histórico
            status_anterior = Reserva.objects.get(pk=obj.pk).status
            Historico.objects.create(
                reserva=obj,
                status_anterior=status_anterior,
                status_novo=obj.status,
                descricao=f'Status alterado de {status_anterior} para {obj.status}.'
            )
        
        super().save_model(request, obj, form, change)

@admin.register(Historico)
class HistoricoAdmin(admin.ModelAdmin):
    """
    Configuração do admin para o modelo Historico.
    """
    list_display = ('reserva', 'data_hora', 'status_anterior', 'status_novo')
    list_filter = ('data_hora', 'status_novo')
    search_fields = ('reserva__codigo', 'descricao')
    readonly_fields = ('reserva', 'data_hora', 'status_anterior', 'status_novo', 'descricao')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
