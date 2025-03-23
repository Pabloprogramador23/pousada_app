from django.contrib import admin
from .models import CategoriaQuarto, Quarto, FotoQuarto

class FotoQuartoInline(admin.TabularInline):
    """
    Inline para exibir fotos dos quartos na página de administração de quartos.
    """
    model = FotoQuarto
    extra = 1
    readonly_fields = ['data_upload']

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
    list_display = ('numero', 'categoria', 'andar', 'status')
    list_filter = ('categoria', 'andar', 'status', 'possui_ar_condicionado', 'possui_varanda')
    search_fields = ('numero', 'observacoes')
    list_editable = ('status',)
    readonly_fields = ('data_criacao', 'data_atualizacao')
    inlines = [FotoQuartoInline]
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('numero', 'categoria', 'andar', 'area', 'status')
        }),
        ('Comodidades', {
            'fields': ('possui_ar_condicionado', 'possui_tv', 'possui_frigobar', 
                      'possui_cofre', 'possui_varanda')
        }),
        ('Observações', {
            'fields': ('observacoes',)
        }),
        ('Datas', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )

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
