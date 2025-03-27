from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Hospede
from django.contrib import messages
import logging

logger = logging.getLogger(__name__)

@login_required
def lista_hospedes(request):
    """
    Exibe a lista de todos os hóspedes cadastrados no sistema.
    """
    hospedes = Hospede.objects.all().order_by('-data_cadastro')
    
    context = {
        'hospedes': hospedes,
        'title': 'Lista de Hóspedes'
    }
    
    return render(request, 'hospedes/lista_hospedes.html', context)

@login_required
def detalhes_hospede(request, hospede_id):
    """
    Exibe detalhes de um hóspede específico, incluindo suas reservas.
    """
    hospede = get_object_or_404(Hospede, id=hospede_id)
    
    # Busca as reservas do hóspede
    reservas = hospede.reservas.all().order_by('-check_in')
    
    context = {
        'hospede': hospede,
        'reservas': reservas,
        'title': f'Detalhes do Hóspede: {hospede.nome}'
    }
    
    return render(request, 'hospedes/detalhes_hospede.html', context)
