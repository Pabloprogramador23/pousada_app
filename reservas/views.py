from django.shortcuts import render
from django.views.generic import CreateView, UpdateView, DetailView, TemplateView
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from .models import Reserva, Historico
from quartos.models import Quarto, CategoriaQuarto
from hospedes.models import Hospede
import logging
import json
from datetime import date, timedelta
from .forms import ReservaForm

logger = logging.getLogger(__name__)

class NovaReservaView(CreateView):
    """
    View para criar uma nova reserva.
    
    Renderiza o formulário de reserva e processa o envio.
    """
    template_name = 'reservas/nova_reserva.html'
    form_class = ReservaForm
    success_url = reverse_lazy('website:home')
    
    def get_context_data(self, **kwargs):
        """
        Adiciona dados de contexto ao template.
        """
        context = super().get_context_data(**kwargs)
        context['today'] = date.today()
        context['tomorrow'] = date.today() + timedelta(days=1)
        
        # Se houver um tipo de quarto selecionado por GET
        tipo_quarto = self.request.GET.get('tipo')
        if tipo_quarto:
            context['tipo_quarto'] = tipo_quarto
            
        # Adiciona a lista de quartos disponíveis
        try:
            context['quartos'] = Quarto.objects.filter(disponivel=True)
        except:
            # Se o modelo Quarto ainda não estiver implementado
            pass
        
        return context
        
    def form_valid(self, form):
        """
        Processa o formulário quando é válido.
        """
        try:
            # Obtem dados do formulário
            nome = form.cleaned_data.get('nome')
            email = form.cleaned_data.get('email')
            telefone = form.cleaned_data.get('telefone')
            cpf = form.cleaned_data.get('cpf')
            
            # Verifica se já existe um hóspede com este CPF
            hospede = None
            try:
                hospede = Hospede.objects.get(cpf=cpf)
                # Atualiza os dados caso tenham mudado
                hospede.nome = nome
                hospede.email = email
                hospede.telefone = telefone
                hospede.save()
                logger.info(f'Hóspede existente atualizado: {hospede.id}')
            except Hospede.DoesNotExist:
                # Cria um novo hóspede
                hospede = Hospede.objects.create(
                    nome=nome,
                    email=email,
                    telefone=telefone,
                    cpf=cpf
                )
                logger.info(f'Novo hóspede criado: {hospede.id}')
            
            # Cria a reserva
            reserva = form.save(commit=False)
            reserva.hospede = hospede
            reserva.status = 'pendente'
            reserva.origem = 'site'
            
            # Define valores de preço
            quarto = reserva.quarto
            reserva.valor_diaria = quarto.preco_diaria
            dias = (reserva.check_out - reserva.check_in).days
            reserva.valor_total = reserva.valor_diaria * dias
            
            reserva.save()
            
            messages.success(self.request, 'Reserva solicitada com sucesso! Enviamos um e-mail de confirmação.')
            logger.info(f'Nova reserva criada: {reserva.codigo}')
            
            # Redireciona para a página de confirmação
            return redirect('reservas:confirmada', codigo=reserva.codigo)
        except Exception as e:
            messages.error(self.request, f'Erro ao processar sua reserva: {str(e)}')
            logger.error(f'Erro ao processar reserva: {str(e)}')
            return self.form_invalid(form)

class ReservaConfirmarView(UpdateView):
    """
    View para confirmar uma reserva existente.
    
    Permite que administradores confirmem reservas pendentes.
    """
    model = Reserva
    template_name = 'reservas/confirmar.html'
    fields = ['confirmada', 'observacoes_admin']
    
    def get_object(self):
        """
        Obtém a reserva pelo código.
        """
        return get_object_or_404(Reserva, codigo=self.kwargs['codigo'])
    
    def form_valid(self, form):
        """
        Processa a confirmação da reserva.
        """
        reserva = form.save(commit=False)
        reserva.confirmada = True
        reserva.data_confirmacao = timezone.now()
        reserva.save()
        
        messages.success(self.request, 'Reserva confirmada com sucesso!')
        logger.info(f'Reserva confirmada: {reserva.codigo}')
        
        return redirect('reservas:confirmada', codigo=reserva.codigo)

class ReservaConfirmadaView(DetailView):
    """
    View para exibir os detalhes de uma reserva confirmada.
    """
    model = Reserva
    template_name = 'reservas/confirmada.html'
    context_object_name = 'reserva'
    
    def get_object(self):
        """
        Obtém a reserva pelo código.
        """
        return get_object_or_404(Reserva, codigo=self.kwargs['codigo'])

class ReservaCancelarView(UpdateView):
    """
    View para cancelar uma reserva existente.
    """
    model = Reserva
    template_name = 'reservas/cancelar.html'
    fields = ['motivo_cancelamento']
    
    def get_object(self):
        """
        Obtém a reserva pelo código.
        """
        return get_object_or_404(Reserva, codigo=self.kwargs['codigo'])
    
    def form_valid(self, form):
        """
        Processa o cancelamento da reserva.
        """
        reserva = form.save(commit=False)
        reserva.cancelada = True
        reserva.data_cancelamento = timezone.now()
        reserva.save()
        
        messages.success(self.request, 'Reserva cancelada com sucesso!')
        logger.info(f'Reserva cancelada: {reserva.codigo}')
        
        return redirect('website:home')

def verificar_disponibilidade(request):
    """
    View para verificar a disponibilidade de quartos para um determinado período.
    
    Retorna um JsonResponse com os quartos disponíveis.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            check_in = data.get('check_in')
            check_out = data.get('check_out')
            
            # Aqui seria implementada a lógica para verificar quartos disponíveis
            # no período solicitado, consultando as reservas existentes
            
            # Por enquanto, retorna um mock de dados
            quartos_disponiveis = [
                {'id': 1, 'nome': 'Quarto Standard', 'preco': 120.00},
                {'id': 2, 'nome': 'Quarto Luxo', 'preco': 180.00},
                {'id': 3, 'nome': 'Suíte Família', 'preco': 250.00}
            ]
            
            logger.info(f'Verificação de disponibilidade para {check_in} a {check_out}')
            return JsonResponse({'disponibilidade': True, 'quartos': quartos_disponiveis})
        except Exception as e:
            logger.error(f'Erro ao verificar disponibilidade: {str(e)}')
            return JsonResponse({'disponibilidade': False, 'erro': str(e)}, status=400)
    
    return JsonResponse({'disponibilidade': False, 'erro': 'Método não permitido'}, status=405)
