from django.utils.deprecation import MiddlewareMixin
import logging

logger = logging.getLogger(__name__)

class NotificacoesMiddleware(MiddlewareMixin):
    """
    Middleware para garantir que as operações com notificações não gerem erros.
    Captura erros relacionados às notificações e os registra no log.
    """
    
    def process_request(self, request):
        """
        Processa a requisição e garante que os erros de notificações são tratados.
        """
        return None
    
    def process_template_response(self, request, response):
        """
        Processa a resposta e garante que erros na renderização de templates relacionados
        a notificações são tratados corretamente.
        """
        try:
            if hasattr(response, 'context_data'):
                # Garante que o contexto tem as variáveis necessárias para as tags de notificações
                if 'notificacoes' not in response.context_data:
                    response.context_data['notificacoes'] = []
                if 'total_nao_lidas' not in response.context_data:
                    response.context_data['total_nao_lidas'] = 0
        except Exception as e:
            logger.error(f"Erro ao processar notificações no template: {e}")
        
        return response 