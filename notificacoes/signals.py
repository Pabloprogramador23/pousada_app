from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from reservas.models import Reserva
from financeiro.models import Pagamento
from hospedes.models import Hospede
from quartos.models import Quarto
from notificacoes.models import Notificacao
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Reserva)
def criar_notificacao_reserva(sender, instance, created, **kwargs):
    """
    Cria notificações baseadas em eventos de reserva
    """
    try:
        if created:
            # Nova reserva criada
            Notificacao.objects.create(
                titulo='Nova Reserva',
                mensagem=f'Nova reserva criada para {instance.hospede.nome_completo} '
                        f'no quarto {instance.quarto.numero} de '
                        f'{instance.data_checkin.strftime("%d/%m/%Y")} '
                        f'até {instance.data_checkout.strftime("%d/%m/%Y")}.',
                categoria='reserva',
                tipo='info',
                url_acao=reverse('reservas:detalhe', kwargs={'pk': instance.pk})
            )
        else:
            # Verifica mudanças de status
            if instance.status_anterior != instance.status:
                status_map = {
                    'confirmada': {'msg': 'confirmada', 'tipo': 'success'},
                    'pendente': {'msg': 'marcada como pendente', 'tipo': 'warning'},
                    'cancelada': {'msg': 'cancelada', 'tipo': 'danger'},
                    'concluida': {'msg': 'concluída', 'tipo': 'success'},
                    'no_show': {'msg': 'marcada como no-show', 'tipo': 'danger'},
                }
                
                if instance.status in status_map:
                    status_info = status_map[instance.status]
                    Notificacao.objects.create(
                        titulo=f'Reserva {status_info["msg"].capitalize()}',
                        mensagem=f'A reserva de {instance.hospede.nome_completo} '
                                f'no quarto {instance.quarto.numero} foi {status_info["msg"]}.',
                        categoria='reserva',
                        tipo=status_info['tipo'],
                        url_acao=reverse('reservas:detalhe', kwargs={'pk': instance.pk})
                    )
            
            # Verifica se a data de check-in é hoje ou amanhã
            hoje = timezone.localdate()
            amanha = hoje + timezone.timedelta(days=1)
            
            if not hasattr(instance, '_checkin_notificado') and instance.data_checkin.date() == hoje:
                instance._checkin_notificado = True
                Notificacao.objects.create(
                    titulo='Check-in Hoje',
                    mensagem=f'Check-in de {instance.hospede.nome_completo} no quarto '
                            f'{instance.quarto.numero} programado para hoje.',
                    categoria='reserva',
                    tipo='warning',
                    url_acao=reverse('reservas:check_in', kwargs={'codigo': instance.codigo})
                )
                
            if not hasattr(instance, '_checkin_amanha_notificado') and instance.data_checkin.date() == amanha:
                instance._checkin_amanha_notificado = True
                Notificacao.objects.create(
                    titulo='Check-in Amanhã',
                    mensagem=f'Check-in de {instance.hospede.nome_completo} no quarto '
                            f'{instance.quarto.numero} programado para amanhã.',
                    categoria='reserva',
                    tipo='info',
                    url_acao=reverse('reservas:detalhe', kwargs={'pk': instance.pk})
                )
    except Exception as e:
        logger.error(f"Erro ao criar notificação de reserva: {e}")


@receiver(post_save, sender=Pagamento)
def criar_notificacao_pagamento(sender, instance, created, **kwargs):
    """
    Cria notificações para novos pagamentos
    """
    try:
        if created:
            Notificacao.objects.create(
                titulo='Novo Pagamento',
                mensagem=f'Pagamento de R$ {instance.valor:.2f} registrado para a reserva '
                        f'de {instance.reserva.hospede.nome_completo}.',
                categoria='pagamento',
                tipo='success',
                url_acao=reverse('reservas:detalhe', kwargs={'pk': instance.reserva.pk})
            )
            
            # Se o pagamento completou o valor da reserva
            if instance.reserva.valor_total <= instance.reserva.valor_pago:
                Notificacao.objects.create(
                    titulo='Reserva Totalmente Paga',
                    mensagem=f'A reserva de {instance.reserva.hospede.nome_completo} '
                            f'foi totalmente paga (R$ {instance.reserva.valor_pago:.2f}).',
                    categoria='pagamento',
                    tipo='success',
                    url_acao=reverse('reservas:detalhe', kwargs={'pk': instance.reserva.pk})
                )
    except Exception as e:
        logger.error(f"Erro ao criar notificação de pagamento: {e}")


@receiver(post_save, sender=Hospede)
def criar_notificacao_hospede(sender, instance, created, **kwargs):
    """
    Cria notificações para novos hóspedes
    """
    try:
        if created:
            Notificacao.objects.create(
                titulo='Novo Hóspede',
                mensagem=f'Novo hóspede cadastrado: {instance.nome_completo}',
                categoria='hospede',
                tipo='info',
                url_acao=reverse('hospedes:detalhe', kwargs={'pk': instance.pk})
            )
    except Exception as e:
        logger.error(f"Erro ao criar notificação de hóspede: {e}")


@receiver(post_save, sender=Quarto)
def criar_notificacao_quarto(sender, instance, created, **kwargs):
    """
    Cria notificações para alterações em quartos
    """
    try:
        if created:
            Notificacao.objects.create(
                titulo='Novo Quarto',
                mensagem=f'Quarto {instance.numero} foi adicionado ao sistema.',
                categoria='quarto',
                tipo='info',
                url_acao=reverse('quartos:detalhe', kwargs={'pk': instance.pk})
            )
        else:
            # Notificar sobre mudança de status do quarto
            if instance.status_anterior != instance.status:
                status_map = {
                    'disponivel': {'msg': 'disponível', 'tipo': 'success'},
                    'ocupado': {'msg': 'ocupado', 'tipo': 'warning'},
                    'manutencao': {'msg': 'em manutenção', 'tipo': 'danger'},
                    'limpeza': {'msg': 'em limpeza', 'tipo': 'warning'},
                }
                
                if instance.status in status_map:
                    status_info = status_map[instance.status]
                    Notificacao.objects.create(
                        titulo=f'Status do Quarto Alterado',
                        mensagem=f'O quarto {instance.numero} agora está {status_info["msg"]}.',
                        categoria='quarto',
                        tipo=status_info['tipo'],
                        url_acao=reverse('quartos:detalhe', kwargs={'pk': instance.pk})
                    )
    except Exception as e:
        logger.error(f"Erro ao criar notificação de quarto: {e}")


# Função para criar notificações do sistema
def criar_notificacao_sistema(titulo, mensagem, tipo='info', url_acao=None):
    """
    Cria uma notificação do sistema
    """
    try:
        Notificacao.objects.create(
            titulo=titulo,
            mensagem=mensagem,
            categoria='sistema',
            tipo=tipo,
            url_acao=url_acao
        )
        return True
    except Exception as e:
        logger.error(f"Erro ao criar notificação do sistema: {e}")
        return False 