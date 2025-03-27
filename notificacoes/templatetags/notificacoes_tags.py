from django import template
from django.utils.safestring import mark_safe
from django.db.models import Count
from notificacoes.models import Notificacao
import logging

register = template.Library()
logger = logging.getLogger(__name__)

@register.simple_tag
def notificacoes_nao_lidas():
    """
    Retorna o número total de notificações não lidas.
    """
    try:
        return Notificacao.objects.filter(lida=False).count()
    except Exception as e:
        logger.error(f"Erro ao contar notificações não lidas: {e}")
        return 0

@register.simple_tag
def notificacoes_nao_lidas_por_categoria(categoria=None):
    """
    Retorna o número de notificações não lidas por categoria.
    Se categoria for None, retorna um dicionário com todas as categorias.
    """
    try:
        if categoria:
            return Notificacao.objects.filter(lida=False, categoria=categoria).count()
        
        contagem = Notificacao.objects.filter(lida=False).values('categoria').annotate(
            total=Count('id')
        ).order_by('categoria')
        
        return {item['categoria']: item['total'] for item in contagem}
    except Exception as e:
        logger.error(f"Erro ao contar notificações por categoria: {e}")
        return 0 if categoria else {}

@register.simple_tag
def notificacoes_recentes(limit=5):
    """
    Retorna as notificações mais recentes não lidas.
    """
    try:
        return Notificacao.objects.filter(lida=False).order_by('-data_criacao')[:limit]
    except Exception as e:
        logger.error(f"Erro ao buscar notificações recentes: {e}")
        return []

@register.inclusion_tag('notificacoes/partials/menu_notificacoes.html')
def menu_notificacoes():
    """
    Renderiza o menu dropdown de notificações para uso no cabeçalho.
    Inclui contagem total e as 5 notificações mais recentes.
    """
    try:
        notificacoes = Notificacao.objects.filter(lida=False).order_by('-data_criacao')[:5]
        total = notificacoes.count()
        
        categorias = {
            'reserva': {
                'count': Notificacao.objects.filter(lida=False, categoria='reserva').count(),
                'icon': 'calendar-alt',
                'color': 'primary'
            },
            'pagamento': {
                'count': Notificacao.objects.filter(lida=False, categoria='pagamento').count(),
                'icon': 'money-bill-wave',
                'color': 'success'
            },
            'hospede': {
                'count': Notificacao.objects.filter(lida=False, categoria='hospede').count(),
                'icon': 'user',
                'color': 'info'
            },
            'quarto': {
                'count': Notificacao.objects.filter(lida=False, categoria='quarto').count(),
                'icon': 'bed',
                'color': 'warning'
            },
            'sistema': {
                'count': Notificacao.objects.filter(lida=False, categoria='sistema').count(),
                'icon': 'cog',
                'color': 'secondary'
            }
        }
        
        return {
            'notificacoes': notificacoes,
            'total': total,
            'categorias': categorias
        }
    except Exception as e:
        logger.error(f"Erro ao renderizar menu de notificações: {e}")
        return {
            'notificacoes': [],
            'total': 0,
            'categorias': {}
        } 