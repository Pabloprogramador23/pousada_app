from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import Notificacao
import logging

logger = logging.getLogger(__name__)

@login_required
def listar_notificacoes(request):
    """
    View para listar todas as notificações do sistema.
    Exibe as não lidas primeiro, seguidas das lidas.
    """
    # Busca notificações não lidas
    notificacoes_nao_lidas = Notificacao.objects.filter(
        lida=False
    ).order_by('-data_criacao')
    
    # Busca notificações lidas (limitadas às últimas 50)
    notificacoes_lidas = Notificacao.objects.filter(
        lida=True
    ).order_by('-data_criacao')[:50]
    
    # Conta total de não lidas por categoria
    contagem_categorias = {}
    for categoria, _ in Notificacao.CATEGORIA_CHOICES:
        contagem_categorias[categoria] = Notificacao.objects.filter(
            categoria=categoria, 
            lida=False
        ).count()
    
    # Verifica notificações de hoje
    hoje = timezone.now().date()
    try:
        # Tenta criar notificações para check-ins de hoje
        checkins_hoje = Notificacao.notificar_check_in_hoje()
        
        # Tenta criar notificações para check-outs de hoje
        checkouts_hoje = Notificacao.notificar_check_out_hoje()
        
        if checkins_hoje > 0 or checkouts_hoje > 0:
            logger.info(f"Notificações criadas: {checkins_hoje} check-ins e {checkouts_hoje} check-outs")
    except Exception as e:
        logger.error(f"Erro ao verificar check-ins/check-outs de hoje: {e}")
    
    contexto = {
        'notificacoes_nao_lidas': notificacoes_nao_lidas,
        'notificacoes_lidas': notificacoes_lidas,
        'contagem_categorias': contagem_categorias,
        'title': 'Notificações',
        'total_nao_lidas': notificacoes_nao_lidas.count()
    }
    
    return render(request, 'notificacoes/listar.html', contexto)

@require_POST
@login_required
def marcar_como_lida(request, pk):
    """
    View para marcar uma notificação como lida.
    """
    notificacao = get_object_or_404(Notificacao, pk=pk)
    notificacao.marcar_como_lida()
    
    # Se for uma requisição AJAX, retorna JSON
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    
    # Caso contrário, redireciona para a lista de notificações
    return redirect('notificacoes:listar')

@login_required
def notificacoes_recentes_json(request):
    """
    View para retornar as notificações recentes em formato JSON.
    Usado para atualizar a interface sem recarregar a página.
    """
    notificacoes = Notificacao.objects.filter(
        lida=False
    ).order_by('-data_criacao')[:10]
    
    data = [{
        'id': n.id,
        'titulo': n.titulo,
        'mensagem': n.mensagem,
        'tipo': n.tipo,
        'categoria': n.categoria,
        'data_criacao': n.data_criacao.strftime('%d/%m/%Y %H:%M'),
        'url_acao': n.url_acao,
        'texto_acao': n.texto_acao
    } for n in notificacoes]
    
    return JsonResponse({
        'notificacoes': data,
        'total': notificacoes.count()
    }) 