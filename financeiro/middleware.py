from django.utils.deprecation import MiddlewareMixin
#from .models import Alerta

class AlertasMiddleware(MiddlewareMixin):
    """
    Middleware para adicionar a contagem de alertas não visualizados ao contexto da requisição.
    Isso permite que o template base tenha acesso a essa informação para exibir um contador.
    """
    
    def process_request(self, request):
        """
        Processa a requisição e adiciona a contagem de alertas não visualizados.
        """
        if request.user.is_authenticated:
            # Conta alertas não visualizados e não resolvidos
            alertas_nao_visualizados = Alerta.objects.filter(
                visualizado=False,
                resolvido=False
            ).count()
            
            # Adiciona ao atributo da requisição para uso no template
            request.alertas_nao_visualizados = alertas_nao_visualizados
        
        return None 