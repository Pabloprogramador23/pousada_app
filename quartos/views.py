from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.utils import timezone
from django.db.models import Q, Count, Sum
import logging

from .models import Quarto, LimpezaManutencao, ChecklistLimpeza

logger = logging.getLogger(__name__)

class QuartoListView(ListView):
    """
    View para listar todos os quartos.
    """
    model = Quarto
    template_name = 'quartos/quarto_list.html'
    context_object_name = 'quartos'
    
    def get_queryset(self):
        """
        Filtra os quartos com base nos parâmetros da URL.
        """
        queryset = Quarto.objects.all()
        
        # Filtra por status se especificado
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        # Filtra por andar se especificado
        andar = self.request.GET.get('andar')
        if andar:
            queryset = queryset.filter(andar=andar)
            
        # Filtra por categoria se especificado
        categoria = self.request.GET.get('categoria')
        if categoria:
            queryset = queryset.filter(categoria__id=categoria)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        """
        Adiciona contadores de status ao contexto.
        """
        context = super().get_context_data(**kwargs)
        
        # Adiciona contadores de quartos por status
        context['total_quartos'] = Quarto.objects.count()
        context['quartos_disponiveis'] = Quarto.objects.filter(status='disponivel').count()
        context['quartos_ocupados'] = Quarto.objects.filter(status='ocupado').count()
        context['quartos_manutencao'] = Quarto.objects.filter(status='manutencao').count()
        context['quartos_limpeza'] = Quarto.objects.filter(status='limpeza').count()
        
        return context

class QuartoDetailView(DetailView):
    """
    View para exibir detalhes de um quarto específico.
    """
    model = Quarto
    template_name = 'quartos/quarto_detail.html'
    context_object_name = 'quarto'
    
    def get_context_data(self, **kwargs):
        """
        Adiciona histórico de limpeza e manutenção ao contexto.
        """
        context = super().get_context_data(**kwargs)
        
        # Adiciona histórico de tarefas de limpeza e manutenção
        context['tarefas'] = LimpezaManutencao.objects.filter(
            quarto=self.object
        ).order_by('-data_agendamento')[:10]
        
        # Calcula dias desde a última limpeza
        if self.object.ultima_limpeza:
            dias = (timezone.now() - self.object.ultima_limpeza).days
            context['dias_ultima_limpeza'] = dias
        
        return context

class LimpezaManutencaoListView(ListView):
    """
    View para listar tarefas de limpeza e manutenção.
    """
    model = LimpezaManutencao
    template_name = 'quartos/limpeza_manutencao_list.html'
    context_object_name = 'tarefas'
    
    def get_queryset(self):
        """
        Filtra as tarefas com base nos parâmetros da URL.
        """
        queryset = LimpezaManutencao.objects.all()
        
        # Filtra por tipo se especificado
        tipo = self.request.GET.get('tipo')
        if tipo:
            queryset = queryset.filter(tipo=tipo)
            
        # Filtra por status se especificado
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        # Filtra por prioridade se especificado
        prioridade = self.request.GET.get('prioridade')
        if prioridade:
            queryset = queryset.filter(prioridade=prioridade)
            
        # Filtra por quarto se especificado
        quarto = self.request.GET.get('quarto')
        if quarto:
            queryset = queryset.filter(quarto__id=quarto)
            
        # Filtra por período se especificado
        data_inicio = self.request.GET.get('data_inicio')
        if data_inicio:
            queryset = queryset.filter(data_agendamento__gte=data_inicio)
            
        data_fim = self.request.GET.get('data_fim')
        if data_fim:
            queryset = queryset.filter(data_agendamento__lte=data_fim)
            
        return queryset.order_by('-data_agendamento')
    
    def get_context_data(self, **kwargs):
        """
        Adiciona contadores e filtros ao contexto.
        """
        context = super().get_context_data(**kwargs)
        
        # Adiciona contadores de tarefas por status
        context['total_tarefas'] = LimpezaManutencao.objects.count()
        context['tarefas_agendadas'] = LimpezaManutencao.objects.filter(status='agendada').count()
        context['tarefas_em_andamento'] = LimpezaManutencao.objects.filter(status='em_andamento').count()
        context['tarefas_concluidas'] = LimpezaManutencao.objects.filter(status='concluida').count()
        
        # Adiciona quartos para filtro
        context['quartos'] = Quarto.objects.all()
        
        # Adiciona opções de tipo, status e prioridade
        context['tipos'] = LimpezaManutencao.TIPO_CHOICES
        context['status_options'] = LimpezaManutencao.STATUS_CHOICES
        context['prioridades'] = LimpezaManutencao.PRIORIDADE_CHOICES
        
        return context

class LimpezaManutencaoDetailView(DetailView):
    """
    View para exibir detalhes de uma tarefa específica.
    """
    model = LimpezaManutencao
    template_name = 'quartos/limpeza_manutencao_detail.html'
    context_object_name = 'tarefa'
    
    def get_context_data(self, **kwargs):
        """
        Adiciona itens do checklist ao contexto.
        """
        context = super().get_context_data(**kwargs)
        context['itens_checklist'] = self.object.itens_checklist.all()
        
        # Calcula tempo decorrido desde o início ou tempo até o agendamento
        if self.object.status == 'em_andamento' and self.object.data_inicio:
            minutos = (timezone.now() - self.object.data_inicio).total_seconds() / 60
            context['tempo_decorrido'] = round(minutos)
        elif self.object.status == 'agendada':
            minutos = (self.object.data_agendamento - timezone.now()).total_seconds() / 60
            context['tempo_ate_agendamento'] = round(minutos)
            
        return context

class LimpezaManutencaoCreateView(CreateView):
    """
    View para criar uma nova tarefa de limpeza ou manutenção.
    """
    model = LimpezaManutencao
    template_name = 'quartos/limpeza_manutencao_form.html'
    fields = ['quarto', 'tipo', 'descricao', 'prioridade', 'data_agendamento', 
              'tempo_estimado', 'responsavel', 'observacoes']
    success_url = reverse_lazy('quartos:limpeza_manutencao_list')
    
    def form_valid(self, form):
        """
        Processa o formulário válido.
        """
        messages.success(self.request, 'Tarefa registrada com sucesso!')
        return super().form_valid(form)

class LimpezaManutencaoUpdateView(UpdateView):
    """
    View para atualizar uma tarefa existente.
    """
    model = LimpezaManutencao
    template_name = 'quartos/limpeza_manutencao_form.html'
    fields = ['tipo', 'descricao', 'status', 'prioridade', 'data_agendamento',
              'responsavel', 'observacoes', 'custo', 'aprovado']
    
    def get_success_url(self):
        """
        Redireciona para a página de detalhes da tarefa.
        """
        return reverse_lazy('quartos:limpeza_manutencao_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        """
        Processa o formulário válido.
        """
        messages.success(self.request, 'Tarefa atualizada com sucesso!')
        return super().form_valid(form)

@login_required
def iniciar_tarefa(request, pk):
    """
    View para iniciar uma tarefa agendada.
    """
    tarefa = get_object_or_404(LimpezaManutencao, pk=pk)
    
    if tarefa.status != 'agendada':
        messages.warning(request, 'Esta tarefa não pode ser iniciada porque não está agendada.')
        return redirect('quartos:limpeza_manutencao_detail', pk=pk)
        
    tarefa.status = 'em_andamento'
    tarefa.data_inicio = timezone.now()
    tarefa.save()
    
    # Atualiza o status do quarto
    if tarefa.tipo == 'limpeza':
        tarefa.quarto.status = 'limpeza'
    elif tarefa.tipo in ['manutencao', 'reparo']:
        tarefa.quarto.status = 'manutencao'
    tarefa.quarto.save()
    
    messages.success(request, f'Tarefa de {tarefa.get_tipo_display()} iniciada com sucesso!')
    return redirect('quartos:limpeza_manutencao_detail', pk=pk)

@login_required
def concluir_tarefa(request, pk):
    """
    View para concluir uma tarefa em andamento.
    """
    tarefa = get_object_or_404(LimpezaManutencao, pk=pk)
    
    if tarefa.status != 'em_andamento':
        messages.warning(request, 'Esta tarefa não pode ser concluída porque não está em andamento.')
        return redirect('quartos:limpeza_manutencao_detail', pk=pk)
        
    tarefa.status = 'concluida'
    tarefa.data_conclusao = timezone.now()
    
    # Verifica se todos os itens do checklist estão concluídos
    if tarefa.itens_checklist.exists():
        todos_concluidos = all(item.concluido for item in tarefa.itens_checklist.all())
        tarefa.checklist_completo = todos_concluidos
        
        if not todos_concluidos:
            messages.warning(request, 'Existem itens do checklist que não foram concluídos.')
    
    tarefa.save()
    
    # Atualiza o status do quarto e a data da última limpeza
    if tarefa.tipo == 'limpeza':
        tarefa.quarto.status = 'disponivel'
        tarefa.quarto.ultima_limpeza = timezone.now()
        tarefa.quarto.save()
        messages.success(request, f'Limpeza do quarto {tarefa.quarto.numero} concluída com sucesso!')
    elif tarefa.tipo in ['manutencao', 'reparo'] and tarefa.aprovado:
        tarefa.quarto.status = 'disponivel'
        tarefa.quarto.save()
        messages.success(request, f'Manutenção do quarto {tarefa.quarto.numero} concluída com sucesso!')
    
    return redirect('quartos:limpeza_manutencao_detail', pk=pk)

@login_required
def atualizar_checklist(request, pk):
    """
    View para atualizar os itens do checklist de uma tarefa.
    """
    tarefa = get_object_or_404(LimpezaManutencao, pk=pk)
    
    if request.method == 'POST':
        # Processa os itens existentes
        for item in tarefa.itens_checklist.all():
            concluido = request.POST.get(f'concluido_{item.pk}') == 'on'
            observacao = request.POST.get(f'observacao_{item.pk}', '')
            
            item.concluido = concluido
            item.observacao = observacao
            item.save()
            
        # Adiciona novos itens
        novo_item = request.POST.get('novo_item')
        if novo_item:
            ChecklistLimpeza.objects.create(
                tarefa=tarefa,
                item=novo_item,
                concluido=False
            )
            
        # Verifica se todos os itens do checklist estão concluídos
        todos_concluidos = all(item.concluido for item in tarefa.itens_checklist.all())
        if todos_concluidos != tarefa.checklist_completo:
            tarefa.checklist_completo = todos_concluidos
            tarefa.save(update_fields=['checklist_completo'])
            
            if todos_concluidos:
                messages.success(request, 'Todos os itens do checklist foram concluídos.')
            
        messages.success(request, 'Checklist atualizado com sucesso!')
        return redirect('quartos:limpeza_manutencao_detail', pk=pk)
        
    return redirect('quartos:limpeza_manutencao_detail', pk=pk)

@login_required
def aplicar_desconto(request, pk):
    """
    View para aplicar ou remover desconto em um quarto.
    """
    quarto = get_object_or_404(Quarto, pk=pk)
    
    if request.method == 'POST':
        desconto = int(request.POST.get('desconto', 0))
        
        if desconto < 0 or desconto > 50:
            messages.error(request, 'O desconto deve estar entre 0% e 50%.')
        else:
            quarto.desconto_porcentagem = desconto
            quarto.save()
            
            if desconto > 0:
                messages.success(request, f'Desconto de {desconto}% aplicado com sucesso ao quarto {quarto.numero}!')
            else:
                messages.success(request, f'Desconto removido do quarto {quarto.numero}.')
                
    return redirect('quartos:quarto_detail', pk=pk)
