from django.contrib import admin
from .models import Hospede, Preferencia

class PreferenciaInline(admin.TabularInline):
    """
    Inline para exibir preferências de hóspedes na página de administração.
    """
    model = Preferencia
    extra = 1
    readonly_fields = ['data_registro']

@admin.register(Hospede)
class HospedeAdmin(admin.ModelAdmin):
    """
    Configuração do admin para o modelo Hospede.
    """
    list_display = ('nome', 'email', 'telefone', 'tipo_documento', 'documento', 'vip', 'ativo')
    list_filter = ('ativo', 'vip', 'estado_civil', 'cidade', 'estado')
    search_fields = ('nome', 'email', 'documento')
    list_editable = ('vip', 'ativo')
    readonly_fields = ('data_cadastro', 'data_atualizacao')
    inlines = [PreferenciaInline]
    
    fieldsets = (
        ('Informações Pessoais', {
            'fields': ('nome', 'email', 'telefone', 'data_nascimento', 'estado_civil')
        }),
        ('Documentação', {
            'fields': ('tipo_documento', 'documento')
        }),
        ('Endereço', {
            'fields': ('endereco', 'complemento', 'bairro', 'cidade', 'estado', 'cep')
        }),
        ('Observações', {
            'fields': ('observacoes', 'vip')
        }),
        ('Controle', {
            'fields': ('ativo', 'data_cadastro', 'data_atualizacao', 'ultima_hospedagem'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Preferencia)
class PreferenciaAdmin(admin.ModelAdmin):
    """
    Configuração do admin para o modelo Preferencia.
    """
    list_display = ('hospede', 'categoria', 'data_registro')
    list_filter = ('categoria', 'data_registro')
    search_fields = ('hospede__nome', 'categoria', 'descricao')
    readonly_fields = ['data_registro']
