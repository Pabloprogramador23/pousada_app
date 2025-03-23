from django.contrib import admin
from .models import Banner, PaginaConteudo, Contato

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    """
    Configuração do admin para o modelo Banner.
    """
    list_display = ('titulo', 'ordem', 'ativo', 'data_criacao')
    list_filter = ('ativo',)
    search_fields = ('titulo', 'subtitulo')
    list_editable = ('ordem', 'ativo')
    readonly_fields = ('data_criacao', 'data_atualizacao')
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('titulo', 'subtitulo', 'imagem')
        }),
        ('Link', {
            'fields': ('link', 'texto_botao')
        }),
        ('Configurações', {
            'fields': ('ativo', 'ordem')
        }),
        ('Controle', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )

@admin.register(PaginaConteudo)
class PaginaConteudoAdmin(admin.ModelAdmin):
    """
    Configuração do admin para o modelo PaginaConteudo.
    """
    list_display = ('titulo', 'tipo', 'slug', 'ativo', 'mostrar_no_menu', 'ordem_menu')
    list_filter = ('tipo', 'ativo', 'mostrar_no_menu')
    search_fields = ('titulo', 'conteudo')
    list_editable = ('ativo', 'mostrar_no_menu', 'ordem_menu')
    prepopulated_fields = {'slug': ('titulo',)}
    readonly_fields = ('data_criacao', 'data_atualizacao')
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('titulo', 'tipo', 'slug', 'conteudo')
        }),
        ('Imagem', {
            'fields': ('imagem_destaque',)
        }),
        ('SEO', {
            'fields': ('meta_descricao',)
        }),
        ('Configurações', {
            'fields': ('ativo', 'mostrar_no_menu', 'ordem_menu')
        }),
        ('Controle', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Contato)
class ContatoAdmin(admin.ModelAdmin):
    """
    Configuração do admin para o modelo Contato.
    """
    list_display = ('nome', 'email', 'assunto', 'data_envio', 'lido', 'respondido')
    list_filter = ('lido', 'respondido', 'data_envio')
    search_fields = ('nome', 'email', 'assunto', 'mensagem')
    list_editable = ('lido', 'respondido')
    readonly_fields = ('nome', 'email', 'telefone', 'assunto', 'mensagem', 'data_envio')
    
    fieldsets = (
        ('Informações do Contato', {
            'fields': ('nome', 'email', 'telefone')
        }),
        ('Mensagem', {
            'fields': ('assunto', 'mensagem', 'data_envio')
        }),
        ('Status', {
            'fields': ('lido', 'respondido')
        }),
    )
    
    def has_add_permission(self, request):
        return False
