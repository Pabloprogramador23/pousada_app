from django.db import models
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
import logging

logger = logging.getLogger(__name__)

class Notificacao(models.Model):
    """
    Modelo para gerenciar notificações do sistema.
    Pode ser associado a qualquer modelo através do GenericForeignKey.
    """
    TIPO_CHOICES = [
        ('info', 'Informação'),
        ('success', 'Sucesso'),
        ('warning', 'Aviso'),
        ('danger', 'Alerta'),
    ]
    
    CATEGORIA_CHOICES = [
        ('reserva', 'Reserva'),
        ('pagamento', 'Pagamento'),
        ('hospede', 'Hóspede'),
        ('quarto', 'Quarto'),
        ('sistema', 'Sistema'),
    ]
    
    titulo = models.CharField(max_length=100)
    mensagem = models.TextField()
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='info')
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES, default='sistema')
    lida = models.BooleanField(default=False)
    
    # Campos para relacionamento genérico
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # URL para ação
    url_acao = models.CharField(max_length=255, blank=True, null=True)
    texto_acao = models.CharField(max_length=50, blank=True, null=True)
    
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Notificação'
        verbose_name_plural = 'Notificações'
        ordering = ['-data_criacao']
    
    def __str__(self):
        return self.titulo
    
    @classmethod
    def criar_notificacao(cls, titulo, mensagem, tipo='info', categoria='sistema', obj=None, url_acao=None, texto_acao=None):
        """
        Método de classe para facilitar a criação de notificações.
        """
        notificacao = cls(
            titulo=titulo,
            mensagem=mensagem,
            tipo=tipo,
            categoria=categoria,
            url_acao=url_acao,
            texto_acao=texto_acao
        )
        
        # Se houver um objeto associado
        if obj:
            notificacao.content_object = obj
        
        notificacao.save()
        logger.info(f"Notificação criada: {titulo}")
        return notificacao
    
    def marcar_como_lida(self):
        """
        Marca a notificação como lida.
        """
        self.lida = True
        self.save()
        
    @classmethod
    def notificar_pagamento_pendente(cls, reserva):
        """
        Cria uma notificação de pagamento pendente para uma reserva.
        """
        from reservas.models import Reserva
        
        if not isinstance(reserva, Reserva):
            raise ValueError("O objeto deve ser uma instância de Reserva")
        
        # Calcula o saldo pendente
        saldo_pendente = reserva.get_saldo_pendente()
        
        if saldo_pendente > 0:
            return cls.criar_notificacao(
                titulo=f"Pagamento pendente - Reserva {reserva.codigo}",
                mensagem=f"A reserva {reserva.codigo} possui um saldo pendente de R$ {saldo_pendente:.2f}.",
                tipo='warning',
                categoria='pagamento',
                obj=reserva,
                url_acao=f"/reservas/detalhe/{reserva.codigo}/",
                texto_acao="Ver Detalhes"
            )
        return None
    
    @classmethod
    def notificar_check_in_hoje(cls):
        """
        Cria notificações para reservas com check-in hoje.
        """
        from reservas.models import Reserva
        
        hoje = timezone.now().date()
        # Busca reservas com check-in hoje, filtrando pelo campo date da datetime
        reservas = Reserva.objects.filter(
            check_in__date=hoje, 
            status='confirmada'
        )
        
        contador = 0
        for reserva in reservas:
            cls.criar_notificacao(
                titulo=f"Check-in hoje - {reserva.hospede.nome}",
                mensagem=f"Reserva {reserva.codigo} tem check-in programado para hoje.",
                tipo='info',
                categoria='reserva',
                obj=reserva,
                url_acao=f"/reservas/realizar-check-in/{reserva.codigo}/",
                texto_acao="Realizar Check-in"
            )
            contador += 1
        
        return contador
    
    @classmethod
    def notificar_check_out_hoje(cls):
        """
        Cria notificações para reservas com check-out hoje.
        """
        from reservas.models import Reserva
        
        hoje = timezone.now().date()
        # Busca reservas com check-out hoje, filtrando pelo campo date da datetime
        reservas = Reserva.objects.filter(
            check_out__date=hoje, 
            status='em_andamento'
        )
        
        contador = 0
        for reserva in reservas:
            cls.criar_notificacao(
                titulo=f"Check-out hoje - {reserva.hospede.nome}",
                mensagem=f"Reserva {reserva.codigo} tem check-out programado para hoje.",
                tipo='info',
                categoria='reserva',
                obj=reserva,
                url_acao=f"/reservas/realizar-check-out/{reserva.codigo}/",
                texto_acao="Realizar Check-out"
            )
            contador += 1
        
        return contador 