from django.contrib import admin
from .models import Notificacao

@admin.register(Notificacao)
class NotificacaoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'categoria', 'tipo', 'lida', 'data_criacao')
    list_filter = ('lida', 'categoria', 'tipo', 'data_criacao')
    search_fields = ('titulo', 'mensagem')
    readonly_fields = ('data_criacao',)
    actions = ['marcar_como_lida', 'marcar_como_nao_lida']
    
    def marcar_como_lida(self, request, queryset):
        queryset.update(lida=True)
        self.message_user(request, f"{queryset.count()} notificações marcadas como lidas.")
    marcar_como_lida.short_description = "Marcar selecionadas como lidas"
    
    def marcar_como_nao_lida(self, request, queryset):
        queryset.update(lida=False)
        self.message_user(request, f"{queryset.count()} notificações marcadas como não lidas.")
    marcar_como_nao_lida.short_description = "Marcar selecionadas como não lidas" 