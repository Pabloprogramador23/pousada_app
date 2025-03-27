from django.contrib import admin
from .models import CategoriaQuarto, Quarto, FotoQuarto, LimpezaManutencao, ChecklistLimpeza

class FotoQuartoInline(admin.TabularInline):
    """
    Inline para exibir fotos dos quartos na página de administração de quartos.
    """
    model = FotoQuarto
    extra = 1
    readonly_fields = ['data_upload']

class ChecklistLimpezaInline(admin.TabularInline):
    """
    Inline para gerenciar itens do checklist de limpeza na página de administração de tarefas.
    """
    model = ChecklistLimpeza
    extra = 3
    
@admin.register(CategoriaQuarto)
class CategoriaQuartoAdmin(admin.ModelAdmin):
    """
    Configuração do admin para o modelo CategoriaQuarto.
    """
    list_display = ('nome', 'preco_base', 'capacidade', 'data_criacao')
    list_filter = ('capacidade',)
    search_fields = ('nome', 'descricao')
    readonly_fields = ('data_criacao', 'data_atualizacao')
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'descricao', 'preco_base', 'capacidade')
        }),
        ('Datas', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Quarto)
class QuartoAdmin(admin.ModelAdmin):
    """
    Configuração do admin para o modelo Quarto.
    """
    list_display = ('numero', 'categoria', 'andar', 'status', 'preco_diaria', 'desconto_porcentagem', 'preco_com_desconto', 'data_ultima_limpeza')
    list_filter = ('categoria', 'andar', 'status', 'tem_ar_condicionado', 'tem_varanda')
    search_fields = ('numero', 'observacoes')
    list_editable = ('status', 'desconto_porcentagem')
    readonly_fields = ('data_criacao', 'data_atualizacao', 'data_ultima_limpeza')
    inlines = [FotoQuartoInline]
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('numero', 'categoria', 'andar', 'area', 'status')
        }),
        ('Preços e Descontos', {
            'fields': ('preco_diaria', 'desconto_porcentagem'),
            'description': 'Configure o preço base do quarto e aplique descontos especiais (até 50%)'
        }),
        ('Comodidades', {
            'fields': ('tem_ar_condicionado', 'tem_tv', 'tem_frigobar', 
                      'tem_varanda', 'tem_banheira')
        }),
        ('Limpeza e Manutenção', {
            'fields': ('data_ultima_limpeza', 'proxima_manutencao')
        }),
        ('Observações', {
            'fields': ('observacoes',)
        }),
        ('Datas', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )
    
    def preco_com_desconto(self, obj):
        """
        Retorna o preço com desconto formatado para exibição no admin.
        """
        if obj.preco_diaria and obj.desconto_porcentagem > 0:
            preco = obj.preco_com_desconto()
            return f'R$ {preco:.2f}'
        return '-'
    preco_com_desconto.short_description = 'Preço c/ Desconto'

@admin.register(FotoQuarto)
class FotoQuartoAdmin(admin.ModelAdmin):
    """
    Configuração do admin para o modelo FotoQuarto.
    """
    list_display = ('quarto', 'legenda', 'destaque', 'data_upload')
    list_filter = ('destaque', 'quarto__categoria')
    search_fields = ('quarto__numero', 'legenda')
    list_editable = ('destaque',)
    readonly_fields = ('data_upload',)

@admin.register(LimpezaManutencao)
class LimpezaManutencaoAdmin(admin.ModelAdmin):
    """
    Configuração do admin para o modelo LimpezaManutencao.
    """
    list_display = ('quarto', 'tipo', 'status', 'prioridade', 'responsavel', 'data_agendamento', 'data_conclusao')
    list_filter = ('tipo', 'status', 'prioridade', 'data_agendamento')
    search_fields = ('quarto__numero', 'descricao', 'responsavel')
    list_editable = ('status', 'prioridade')
    readonly_fields = ('data_criacao', 'data_atualizacao', 'data_inicio', 'data_conclusao')
    inlines = [ChecklistLimpezaInline]
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('quarto', 'tipo', 'descricao', 'status', 'prioridade')
        }),
        ('Datas', {
            'fields': ('data_agendamento', 'data_inicio', 'data_conclusao', 'tempo_estimado')
        }),
        ('Detalhes da Execução', {
            'fields': ('responsavel', 'observacoes', 'custo', 'checklist_completo', 'aprovado')
        }),
        ('Controle', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """
        Sobrescreve o método save_model para atualizar o checklist_completo baseado nos itens.
        """
        super().save_model(request, obj, form, change)
        
        # Verifica se todos os itens do checklist estão concluídos
        if obj.itens_checklist.exists():
            todos_concluidos = all(item.concluido for item in obj.itens_checklist.all())
            if todos_concluidos != obj.checklist_completo:
                obj.checklist_completo = todos_concluidos
                obj.save(update_fields=['checklist_completo'])

@admin.register(ChecklistLimpeza)
class ChecklistLimpezaAdmin(admin.ModelAdmin):
    """
    Configuração do admin para o modelo ChecklistLimpeza.
    """
    list_display = ('tarefa', 'item', 'concluido', 'observacao')
    list_filter = ('concluido', 'tarefa__tipo')
    search_fields = ('item', 'observacao', 'tarefa__quarto__numero')
    list_editable = ('concluido',)
