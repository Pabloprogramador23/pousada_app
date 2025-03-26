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
from datetime import date, timedelta, datetime
from .forms import ReservaForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q

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
                hospede = Hospede.objects.get(documento=cpf, tipo_documento='cpf')
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
                    documento=cpf,
                    tipo_documento='cpf'
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
            
            # Converte as datas para objetos datetime
            check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
            check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()
            
            # Busca IDs de quartos que têm reservas no período solicitado
            # Um quarto está indisponível se existir qualquer reserva que:
            # 1. Começa antes do check-out solicitado E
            # 2. Termina depois do check-in solicitado
            # 3. Não está cancelada (pendente, confirmada ou em andamento)
            reservas_no_periodo = Reserva.objects.filter(
                check_in__lt=check_out_date,
                check_out__gt=check_in_date,
                status__in=['pendente', 'confirmada', 'em_andamento']
            )
            
            # Obtém IDs dos quartos já reservados no período
            quartos_ocupados_ids = reservas_no_periodo.values_list('quarto_id', flat=True)
            
            # Se o check-in é para hoje, também elimina quartos que não estão disponíveis agora
            if check_in_date == timezone.now().date():
                quartos_indisponiveis_hoje_ids = Quarto.objects.exclude(
                    status='disponivel'
                ).values_list('id', flat=True)
                # Combina os dois conjuntos de IDs
                quartos_indisponiveis_ids = list(set(quartos_ocupados_ids) | set(quartos_indisponiveis_hoje_ids))
            else:
                quartos_indisponiveis_ids = list(quartos_ocupados_ids)
            
            # Busca quartos que estão disponíveis (não estão na lista de indisponíveis)
            quartos_disponiveis = Quarto.objects.exclude(id__in=quartos_indisponiveis_ids)
            
            # Formata os dados dos quartos
            quartos_data = [{
                'id': quarto.id,
                'numero': quarto.numero,
                'categoria': quarto.categoria.nome if hasattr(quarto, 'categoria') else 'Sem categoria',
                'preco': float(quarto.preco_diaria)
            } for quarto in quartos_disponiveis]
            
            # Log para depuração
            logger.info(f'Verificação de disponibilidade para {check_in} a {check_out}. '
                        f'Encontrados {len(quartos_data)} quartos disponíveis. '
                        f'Quartos indisponíveis: {quartos_indisponiveis_ids}')
            
            return JsonResponse({
                'disponibilidade': True, 
                'quartos': quartos_data
            })
        except Exception as e:
            logger.error(f'Erro ao verificar disponibilidade: {str(e)}')
            return JsonResponse({
                'disponibilidade': False, 
                'erro': str(e)
            }, status=400)
    
    return JsonResponse({
        'disponibilidade': False, 
        'erro': 'Método não permitido'
    }, status=405)

class CheckInView(TemplateView):
    """
    View para realizar o check-in de hóspedes.
    
    Permite buscar reservas e registrar a chegada do hóspede.
    """
    template_name = 'reservas/check_in.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Verifica se foi feita uma busca
        tipo_busca = self.request.GET.get('tipo_busca')
        busca_termo = self.request.GET.get('busca_termo')
        busca_realizada = False
        
        # Adiciona as reservas com check-in para hoje
        hoje = date.today()
        context['hoje_chegadas'] = Reserva.objects.filter(
            check_in=hoje, 
            status__in=['pendente', 'confirmada']
        ).order_by('codigo')
        
        context['hora_atual'] = timezone.now()
        
        # Se for uma busca, procura a reserva
        if tipo_busca and busca_termo:
            busca_realizada = True
            context['tipo_busca'] = tipo_busca
            context['busca_termo'] = busca_termo
            
            try:
                # Busca por diferentes critérios
                if tipo_busca == 'codigo':
                    reserva = Reserva.objects.get(codigo=busca_termo)
                    context['reserva'] = reserva
                elif tipo_busca == 'cpf':
                    # Remove caracteres não numéricos do CPF
                    cpf_limpo = ''.join(filter(str.isdigit, busca_termo))
                    hospede = Hospede.objects.get(documento=cpf_limpo, tipo_documento='cpf')
                    # Pega a reserva mais recente deste hóspede
                    reserva = Reserva.objects.filter(
                        hospede=hospede
                    ).order_by('-check_in').first()
                    context['reserva'] = reserva
                elif tipo_busca == 'nome':
                    # Busca por nome parcial
                    hospedes = Hospede.objects.filter(nome__icontains=busca_termo)
                    if hospedes.exists():
                        # Pega o primeiro hóspede e sua reserva mais recente
                        hospede = hospedes.first()
                        reserva = Reserva.objects.filter(
                            hospede=hospede
                        ).order_by('-check_in').first()
                        context['reserva'] = reserva
            except (Reserva.DoesNotExist, Hospede.DoesNotExist):
                # Nenhuma reserva encontrada
                pass
        
        context['busca_realizada'] = busca_realizada
        return context

def realizar_check_in(request, codigo):
    """
    View para processar o formulário de check-in.
    """
    reserva = get_object_or_404(Reserva, codigo=codigo)
    
    # Verifica se já foi feito check-in
    if reserva.hora_checkin:
        messages.warning(request, 'Check-in já realizado para esta reserva.')
        return redirect('reservas:check_in')
    
    # Verifica se a reserva está cancelada
    if reserva.status == 'cancelada':
        messages.error(request, 'Não é possível fazer check-in de uma reserva cancelada.')
        return redirect('reservas:check_in')
    
    # Verifica se existem outras reservas conflitantes para o mesmo quarto
    # (pode ter sido criada depois que esta reserva foi feita)
    hoje = date.today()
    reservas_conflitantes = Reserva.objects.filter(
        quarto=reserva.quarto,
        check_in__lt=reserva.check_out,
        check_out__gt=reserva.check_in,
        status__in=['em_andamento'],
    ).exclude(id=reserva.id)
    
    if reservas_conflitantes.exists():
        conflito = reservas_conflitantes.first()
        messages.error(
            request, 
            f'Não é possível fazer check-in pois o quarto {reserva.quarto.numero} '
            f'já está ocupado por {conflito.hospede.nome} '
            f'até {conflito.check_out.strftime("%d/%m/%Y")}.'
        )
        return redirect('reservas:check_in')
    
    # Verifica se a data de check-in já passou
    if reserva.check_in < hoje:
        messages.warning(
            request, 
            f'Atenção: A data de check-in ({reserva.check_in.strftime("%d/%m/%Y")}) '
            f'é anterior à data atual ({hoje.strftime("%d/%m/%Y")}).'
        )
    
    if request.method == 'POST':
        try:
            hora_checkin = request.POST.get('hora_checkin')
            acompanhantes = request.POST.get('acompanhantes', '0')
            forma_pagamento = request.POST.get('forma_pagamento')
            
            # Processa o desconto
            try:
                desconto_diaria_str = request.POST.get('desconto_diaria', '0')
                desconto_diaria = float(desconto_diaria_str) if desconto_diaria_str.strip() else 0.0
            except (ValueError, TypeError):
                desconto_diaria = 0.0
                
            # Processa o valor pago
            try:
                valor_pago_str = request.POST.get('valor_pago', '0')
                valor_pago = float(valor_pago_str) if valor_pago_str.strip() else 0.0
            except (ValueError, TypeError):
                valor_pago = 0.0
                
            observacoes = request.POST.get('observacoes', '')
            
            # Atualiza a reserva
            reserva.hora_checkin = hora_checkin
            reserva.desconto_diaria = desconto_diaria
            
            if acompanhantes and acompanhantes.isdigit():
                reserva.acompanhantes = int(acompanhantes)
                
            if observacoes:
                reserva.observacoes = f"{reserva.observacoes or ''}\n\nCheck-in: {observacoes}"
            
            # Recalcula o valor total considerando o desconto
            if desconto_diaria > 0:
                # Calcula o número de dias
                delta = (reserva.check_out - reserva.check_in).days
                if delta > 0:
                    # Valor da diária com desconto (não pode ser menor que R$100)
                    valor_diaria_com_desconto = max(100, reserva.valor_diaria - desconto_diaria)
                    # Atualiza o valor total
                    reserva.valor_total = valor_diaria_com_desconto * delta
            
            # Atualiza o status da reserva
            reserva.status = 'em_andamento'
            reserva.save()
            
            # Registra o histórico
            info_desconto = f", Desconto: R$ {desconto_diaria:.2f} por diária" if desconto_diaria > 0 else ""
            Historico.objects.create(
                reserva=reserva,
                status_anterior='pendente' if not reserva.data_confirmacao else 'confirmada',
                status_novo='em_andamento',
                descricao=f"Check-in realizado às {hora_checkin}. Forma de pagamento: {forma_pagamento}. Valor pago: R$ {valor_pago}{info_desconto}"
            )
            
            # Registra o pagamento no módulo financeiro (se existir)
            try:
                from financeiro.models import Pagamento
                Pagamento.objects.create(
                    reserva=reserva,
                    valor=float(valor_pago),
                    forma_pagamento=forma_pagamento,
                    data_pagamento=timezone.now(),
                    status='pago',
                    descricao=f"Pagamento de hospedagem - Check-in reserva {reserva.codigo}"
                )
                logger.info(f"Pagamento registrado para reserva {reserva.codigo}")
            except (ImportError, Exception) as e:
                logger.warning(f"Não foi possível registrar o pagamento no módulo financeiro: {str(e)}")
            
            # Registra a disponibilidade do quarto
            quarto = reserva.quarto
            quarto.status = 'ocupado'
            quarto.save()
            
            # Cria alerta para limpeza na data de check-out (se o módulo quartos estiver disponível)
            try:
                from quartos.models import LimpezaManutencao
                from django.contrib.auth.models import User
                
                # Encontra o primeiro usuário admin para ser o responsável
                admin = User.objects.filter(is_staff=True).first() 
                
                LimpezaManutencao.objects.create(
                    quarto=reserva.quarto,
                    tipo='limpeza',
                    status='pendente',
                    prioridade='media',
                    data_agendada=reserva.check_out,
                    descricao=f"Limpeza pós check-out da reserva {reserva.codigo}",
                    responsavel=admin
                )
                logger.info(f"Tarefa de limpeza agendada para check-out da reserva {reserva.codigo}")
            except (ImportError, Exception) as e:
                logger.warning(f"Não foi possível agendar tarefa de limpeza: {str(e)}")
            
            messages.success(request, f'Check-in realizado com sucesso para {reserva.hospede.nome}!')
            logger.info(f"Check-in realizado para reserva {reserva.codigo}")
            
            return redirect('reservas:check_in')
            
        except Exception as e:
            messages.error(request, f'Erro ao processar check-in: {str(e)}')
            logger.error(f"Erro no check-in da reserva {reserva.codigo}: {str(e)}")
            return redirect('reservas:check_in')
    
    return redirect('reservas:check_in')

class CheckInDiretoView(LoginRequiredMixin, TemplateView):
    """
    View para realizar check-in direto de hóspedes sem reserva prévia.
    """
    template_name = 'reservas/check_in_direto.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hoje'] = date.today()
        context['amanha'] = date.today() + timedelta(days=1)
        context['hora_atual'] = timezone.now()
        
        # Busca todos os quartos com suas informações de ocupação
        quartos = Quarto.objects.all().select_related('categoria')
        
        # Para cada quarto, verifica se está ocupado e adiciona informações
        quartos_info = []
        for quarto in quartos:
            # Busca reserva atual (se houver)
            reserva_atual = Reserva.objects.filter(
                quarto=quarto,
                check_in__lte=timezone.now(),
                check_out__gte=timezone.now(),
                status='em_andamento'
            ).first()
            
            quartos_info.append({
                'quarto': quarto,
                'ocupado': reserva_atual is not None,
                'reserva_atual': reserva_atual,
                'proxima_disponibilidade': reserva_atual.check_out if reserva_atual else None
            })
        
        context['quartos_info'] = quartos_info
        
        return context

def processar_check_in_direto(request):
    """
    View para processar o formulário de check-in direto (sem reserva prévia).
    """
    if request.method != 'POST':
        return redirect('reservas:check_in')
    
    try:
        # Extrai dados do formulário
        nome = request.POST.get('nome')
        cpf = request.POST.get('cpf')
        email = request.POST.get('email', '')
        telefone = request.POST.get('telefone')
        data_nascimento = request.POST.get('data_nascimento')
        
        quarto_id = request.POST.get('quarto')
        check_in_date = request.POST.get('check_in')
        check_out_date = request.POST.get('check_out')
        hora_checkin = request.POST.get('hora_checkin')
        adultos = int(request.POST.get('adultos', 1))
        criancas = int(request.POST.get('criancas', 0))
        
        # Trata valores numéricos com cuidado
        try:
            valor_diaria_str = request.POST.get('valor_diaria', '0')
            valor_diaria = float(valor_diaria_str) if valor_diaria_str.strip() else 0.0
        except (ValueError, TypeError):
            valor_diaria = 0.0
            
        try:
            desconto_diaria_str = request.POST.get('desconto_diaria', '0')
            desconto_diaria = float(desconto_diaria_str) if desconto_diaria_str.strip() else 0.0
        except (ValueError, TypeError):
            desconto_diaria = 0.0
            
        forma_pagamento = request.POST.get('forma_pagamento')
        
        try:
            valor_pago_str = request.POST.get('valor_pago', '0')
            valor_pago = float(valor_pago_str) if valor_pago_str.strip() else 0.0
        except (ValueError, TypeError):
            valor_pago = 0.0
            
        observacoes = request.POST.get('observacoes', '')
        
        # Valida dados obrigatórios
        if not all([nome, cpf, quarto_id, check_in_date, check_out_date, data_nascimento, forma_pagamento]):
            messages.error(request, 'Preencha todos os campos obrigatórios.')
            return redirect('reservas:check_in_direto')
            
        # Remove caracteres não numéricos do CPF
        cpf_limpo = ''.join(filter(str.isdigit, cpf))
        
        # Verifica se o hóspede já existe
        try:
            hospede = Hospede.objects.get(documento=cpf_limpo, tipo_documento='cpf')
            # Atualiza informações se necessário
            if hospede.nome != nome or hospede.email != email or hospede.telefone != telefone or not hospede.data_nascimento:
                hospede.nome = nome
                hospede.email = email
                hospede.telefone = telefone
                if not hospede.data_nascimento and data_nascimento:
                    hospede.data_nascimento = data_nascimento
                hospede.save()
        except Hospede.DoesNotExist:
            # Cria um novo hóspede
            hospede = Hospede.objects.create(
                nome=nome,
                documento=cpf_limpo,
                tipo_documento='cpf',
                email=email,
                telefone=telefone,
                data_nascimento=data_nascimento
            )
        
        # Busca o quarto selecionado
        quarto = get_object_or_404(Quarto, id=quarto_id)
        
        # Converte as datas para objetos date
        check_in_date_obj = datetime.strptime(check_in_date, '%Y-%m-%d').date()
        check_out_date_obj = datetime.strptime(check_out_date, '%Y-%m-%d').date()
        
        # Validação das datas
        if check_in_date_obj >= check_out_date_obj:
            messages.error(request, 'A data de check-in deve ser anterior à data de check-out.')
            return redirect('reservas:check_in_direto')
            
        hoje = date.today()
        if check_in_date_obj < hoje:
            messages.error(request, 'A data de check-in não pode ser anterior a hoje.')
            return redirect('reservas:check_in_direto')
        
        # Verificação mais rigorosa de disponibilidade
        # Verifica se há reservas que se sobrepõem ao período solicitado
        reservas_conflitantes = Reserva.objects.filter(
            quarto=quarto,
            check_in__lt=check_out_date_obj,
            check_out__gt=check_in_date_obj,
            status__in=['pendente', 'confirmada', 'em_andamento']
        )
        
        if reservas_conflitantes.exists():
            # Para fornecer uma mensagem de erro mais detalhada
            primeira_reserva = reservas_conflitantes.first()
            messages.error(
                request, 
                f'Quarto {quarto.numero} não está disponível no período selecionado. '
                f'Já existe uma reserva para {primeira_reserva.hospede.nome} '
                f'de {primeira_reserva.check_in.strftime("%d/%m/%Y")} '
                f'até {primeira_reserva.check_out.strftime("%d/%m/%Y")}.'
            )
            return redirect('reservas:check_in_direto')
        
        # Verifica o status atual do quarto (importante para check-ins no mesmo dia)
        if check_in_date_obj == hoje and quarto.status != 'disponivel':
            messages.error(
                request, 
                f'O quarto {quarto.numero} está {quarto.get_status_display().lower()} '
                f'e não pode ser utilizado hoje.'
            )
            return redirect('reservas:check_in_direto')
        
        # Cria a reserva
        reserva = Reserva.objects.create(
            quarto=quarto,
            hospede=hospede,
            check_in=check_in_date,
            check_out=check_out_date,
            hora_checkin=hora_checkin,
            adultos=adultos,
            criancas=criancas,
            valor_diaria=valor_diaria,
            desconto_diaria=desconto_diaria,
            valor_total=valor_pago,
            status='em_andamento',
            origem='presencial',
            confirmada=True,
            observacoes=observacoes
        )
        
        # Se o check-in é para hoje, atualiza o status do quarto
        if check_in_date_obj == hoje:
            quarto.status = 'ocupado'
            quarto.save()
        
        # Registra o histórico
        info_desconto = f", Desconto: R$ {desconto_diaria:.2f} por diária" if desconto_diaria > 0 else ""
        Historico.objects.create(
            reserva=reserva,
            status_anterior=None,
            status_novo='em_andamento',
            descricao=f"Check-in direto realizado às {hora_checkin}. Forma de pagamento: {forma_pagamento}. Valor pago: R$ {valor_pago}{info_desconto}"
        )
        
        # Registra o pagamento no módulo financeiro (se existir)
        try:
            from financeiro.models import Pagamento
            Pagamento.objects.create(
                reserva=reserva,
                valor=valor_pago,
                forma_pagamento=forma_pagamento,
                data_pagamento=timezone.now(),
                status='pago',
                descricao=f"Pagamento de hospedagem - Check-in direto, reserva {reserva.codigo}"
            )
            logger.info(f"Pagamento registrado para reserva {reserva.codigo}")
        except (ImportError, Exception) as e:
            logger.warning(f"Não foi possível registrar o pagamento no módulo financeiro: {str(e)}")
        
        # Cria alerta para limpeza na data de check-out (se o módulo quartos estiver disponível)
        try:
            from quartos.models import LimpezaManutencao
            from django.contrib.auth.models import User
            
            # Encontra o primeiro usuário admin para ser o responsável
            admin = User.objects.filter(is_staff=True).first() 
            
            LimpezaManutencao.objects.create(
                quarto=quarto,
                tipo='limpeza',
                status='pendente',
                prioridade='media',
                data_agendada=reserva.check_out,
                descricao=f"Limpeza pós check-out da reserva {reserva.codigo}",
                responsavel=admin
            )
            logger.info(f"Tarefa de limpeza agendada para check-out da reserva {reserva.codigo}")
        except (ImportError, Exception) as e:
            logger.warning(f"Não foi possível agendar tarefa de limpeza: {str(e)}")
        
        messages.success(request, f'Check-in direto realizado com sucesso para {hospede.nome}! Código da reserva: {reserva.codigo}')
        logger.info(f"Check-in direto realizado para reserva {reserva.codigo}")
        
        return redirect('reservas:check_in')
        
    except Exception as e:
        messages.error(request, f'Erro ao processar check-in direto: {str(e)}')
        logger.error(f"Erro no check-in direto: {str(e)}")
        return redirect('reservas:check_in_direto')

def realizar_check_out(request, codigo):
    """
    View para processar o check-out de hóspedes.
    """
    reserva = get_object_or_404(Reserva, codigo=codigo)
    
    # Verifica se a reserva está em andamento
    if reserva.status != 'em_andamento':
        messages.warning(request, 'Esta reserva não está em andamento.')
        return redirect('reservas:check_in')
    
    # Verifica se a reserva teve check-in registrado
    if not reserva.hora_checkin:
        messages.error(request, 'Não é possível fazer check-out de uma reserva que não teve check-in.')
        return redirect('reservas:check_in')
    
    # Verifica se a data de check-in é futura
    hoje = date.today()
    if reserva.check_in > hoje:
        messages.error(
            request, 
            f'Não é possível fazer check-out de uma reserva futura (check-in: {reserva.check_in.strftime("%d/%m/%Y")}).'
        )
        return redirect('reservas:check_in')
    
    if request.method == 'POST':
        try:
            hora_checkout = request.POST.get('hora_checkout')
            observacoes = request.POST.get('observacoes', '')
            
            # Atualiza a reserva
            reserva.hora_checkout = hora_checkout
            reserva.status = 'concluida'
            if observacoes:
                reserva.observacoes = f"{reserva.observacoes or ''}\n\nCheck-out: {observacoes}"
            reserva.save()
            
            # Registra o histórico
            Historico.objects.create(
                reserva=reserva,
                status_anterior='em_andamento',
                status_novo='concluida',
                descricao=f"Check-out realizado às {hora_checkout}"
            )
            
            # Atualiza o status do quarto
            quarto = reserva.quarto
            quarto.status = 'disponivel'
            quarto.save()
            
            # Cria alerta para limpeza
            try:
                from quartos.models import LimpezaManutencao
                from django.contrib.auth.models import User
                
                admin = User.objects.filter(is_staff=True).first()
                
                LimpezaManutencao.objects.create(
                    quarto=quarto,
                    tipo='limpeza',
                    status='pendente',
                    prioridade='alta',
                    data_agendada=timezone.now(),
                    descricao=f"Limpeza pós check-out da reserva {reserva.codigo}",
                    responsavel=admin
                )
                logger.info(f"Tarefa de limpeza criada para quarto {quarto.numero}")
            except Exception as e:
                logger.warning(f"Não foi possível criar tarefa de limpeza: {str(e)}")
            
            messages.success(request, f'Check-out realizado com sucesso para {reserva.hospede.nome}!')
            logger.info(f"Check-out realizado para reserva {reserva.codigo}")
            
            return redirect('reservas:check_in')
            
        except Exception as e:
            messages.error(request, f'Erro ao processar check-out: {str(e)}')
            logger.error(f"Erro no check-out da reserva {reserva.codigo}: {str(e)}")
            return redirect('reservas:check_in')
    
    return redirect('reservas:check_in')

def eventos_calendario(request):
    """
    View para fornecer os eventos do calendário.
    """
    start = request.GET.get('start')
    end = request.GET.get('end')
    
    try:
        start_date = datetime.strptime(start, '%Y-%m-%d').date()
        end_date = datetime.strptime(end, '%Y-%m-%d').date()
        
        # Busca reservas no período
        reservas = Reserva.objects.filter(
            check_in__lte=end_date,
            check_out__gte=start_date
        ).select_related('quarto', 'hospede')
        
        # Formata os eventos
        eventos = []
        for reserva in reservas:
            # Define título mais informativo com número do quarto
            quarto_numero = reserva.quarto.numero
            status_abreviado = {
                'pendente': 'PEND',
                'confirmada': 'CONF',
                'em_andamento': 'CHECK-IN',
                'concluida': 'CONC',
                'cancelada': 'CANC',
                'no_show': 'NS'
            }.get(reserva.status, '')
            
            titulo = f'Q{quarto_numero} - {status_abreviado}'
            
            # Define textColor com base na cor de fundo para garantir legibilidade
            textColor = '#fff'  # branco para fundos escuros
            bgColor = reserva.get_status_color()
            
            # Para cores claras como amarelo (pendente), usar texto escuro
            if reserva.status == 'pendente':
                textColor = '#333'
            
            eventos.append({
                'id': reserva.codigo,
                'title': titulo,
                'start': reserva.check_in.isoformat(),
                'end': reserva.check_out.isoformat(),
                'backgroundColor': bgColor,
                'borderColor': bgColor,
                'textColor': textColor,
                'classNames': [f'status-{reserva.status}', f'quarto-{quarto_numero}'],
                'extendedProps': {
                    'quarto': f'Quarto {quarto_numero}',
                    'hospede': reserva.hospede.nome,
                    'status': reserva.get_status_display(),
                    'check_in': reserva.check_in.strftime('%d/%m/%Y'),
                    'check_out': reserva.check_out.strftime('%d/%m/%Y'),
                    'codigo': reserva.codigo
                }
            })
        
        return JsonResponse(eventos, safe=False)
    except Exception as e:
        logger.error(f'Erro ao buscar eventos do calendário: {str(e)}')
        return JsonResponse({'error': str(e)}, status=400)

def detalhes_dia(request):
    """
    View para fornecer os detalhes das reservas de um dia específico.
    """
    data = request.GET.get('data')
    
    try:
        data = datetime.strptime(data, '%Y-%m-%d').date()
        
        # Busca reservas para o dia
        reservas = Reserva.objects.filter(
            check_in__lte=data,
            check_out__gte=data
        ).select_related('quarto', 'hospede')
        
        # Importa o modelo de Pagamento, se disponível
        try:
            from financeiro.models import Pagamento
            pagamentos_disponiveis = True
        except ImportError:
            pagamentos_disponiveis = False
        
        # Formata os dados
        reservas_data = []
        for reserva in reservas:
            # Determina se a reserva já teve check-in e se pode ter check-out
            tem_checkin = bool(reserva.hora_checkin)
            pode_checkout = tem_checkin and reserva.status == 'em_andamento' and reserva.check_in <= date.today()
            
            # Calcula pagamentos e saldo, se disponível
            pagamentos_totais = 0
            saldo_pendente = 0
            if pagamentos_disponiveis:
                try:
                    pagamentos_totais = Pagamento.objects.filter(reserva=reserva).aggregate(
                        total=models.Sum('valor')
                    )['total'] or 0
                    saldo_pendente = float(reserva.valor_total) - float(pagamentos_totais)
                except Exception as e:
                    logger.warning(f"Erro ao calcular pagamentos para reserva {reserva.codigo}: {str(e)}")
            
            reservas_data.append({
                'id': reserva.id,
                'codigo': reserva.codigo,
                'hospede': reserva.hospede.nome,
                'quarto': f'Quarto {reserva.quarto.numero}',
                'quarto_id': reserva.quarto.id,
                'quarto_numero': reserva.quarto.numero,
                'status': reserva.get_status_display(),
                'status_raw': reserva.status,
                'status_color': reserva.get_status_color(),
                'check_in': reserva.check_in.strftime('%d/%m/%Y'),
                'check_out': reserva.check_out.strftime('%d/%m/%Y'),
                'valor_total': float(reserva.valor_total),
                'valor_diaria': float(reserva.valor_diaria),
                'tem_checkin': tem_checkin,
                'pode_checkout': pode_checkout,
                'pagamentos_totais': float(pagamentos_totais),
                'saldo_pendente': float(saldo_pendente),
                'tem_saldo_pendente': saldo_pendente > 0,
                'permite_pagamento': reserva.status in ['pendente', 'confirmada', 'em_andamento']
            })
        
        return JsonResponse({'reservas': reservas_data})
    except Exception as e:
        logger.error(f'Erro ao buscar detalhes do dia: {str(e)}')
        return JsonResponse({'error': str(e)}, status=400)

def cancelar_reserva_ajax(request):
    """
    View para cancelar uma reserva via AJAX.
    Usada pelo calendário.
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Método não permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        codigo = data.get('codigo')
        motivo = data.get('motivo', 'Cancelamento via calendário')
        
        if not codigo:
            return JsonResponse({'status': 'error', 'message': 'Código da reserva não fornecido'}, status=400)
        
        # Obtém a reserva
        reserva = get_object_or_404(Reserva, codigo=codigo)
        
        # Verifica se a reserva já está cancelada
        if reserva.status == 'cancelada':
            return JsonResponse({'status': 'error', 'message': 'Esta reserva já está cancelada'}, status=400)
            
        # Verifica se a reserva já foi finalizada
        if reserva.status == 'concluida':
            return JsonResponse({'status': 'error', 'message': 'Não é possível cancelar uma reserva já concluída'}, status=400)
            
        # Cancela a reserva
        reserva.status = 'cancelada'
        reserva.cancelada = True
        reserva.motivo_cancelamento = motivo
        reserva.data_cancelamento = timezone.now()
        reserva.save()
        
        # Registra o histórico
        Historico.objects.create(
            reserva=reserva,
            status_anterior=reserva.status,
            status_novo='cancelada',
            descricao=f"Reserva cancelada pelo calendário. Motivo: {motivo}"
        )
        
        # Se o quarto estava ocupado, libera-o
        if reserva.hora_checkin and reserva.quarto.status == 'ocupado':
            quarto = reserva.quarto
            quarto.status = 'disponivel'
            quarto.save()
        
        logger.info(f"Reserva {reserva.codigo} cancelada via calendário. Motivo: {motivo}")
        
        return JsonResponse({
            'status': 'success', 
            'message': 'Reserva cancelada com sucesso'
        })
    except Exception as e:
        logger.error(f'Erro ao cancelar reserva: {str(e)}')
        return JsonResponse({
            'status': 'error', 
            'message': f'Erro ao cancelar reserva: {str(e)}'
        }, status=500)

def checkout_reserva_ajax(request):
    """
    View para realizar o checkout de uma reserva via AJAX.
    Usada pelo calendário.
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Método não permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        codigo = data.get('codigo')
        observacoes = data.get('observacoes', '')
        
        if not codigo:
            return JsonResponse({'status': 'error', 'message': 'Código da reserva não fornecido'}, status=400)
        
        # Obtém a reserva
        reserva = get_object_or_404(Reserva, codigo=codigo)
        
        # Verifica se a reserva está em andamento (teve check-in)
        if reserva.status != 'em_andamento':
            return JsonResponse({
                'status': 'error', 
                'message': f'Não é possível fazer check-out. Status atual: {reserva.get_status_display()}'
            }, status=400)
        
        # Verifica se a reserva teve check-in registrado
        if not reserva.hora_checkin:
            return JsonResponse({
                'status': 'error', 
                'message': 'Não é possível fazer check-out de uma reserva que não teve check-in'
            }, status=400)
        
        # Verifica se a data de check-in é futura
        hoje = date.today()
        if reserva.check_in > hoje:
            return JsonResponse({
                'status': 'error', 
                'message': f'Não é possível fazer check-out de uma reserva futura (check-in: {reserva.check_in.strftime("%d/%m/%Y")})'
            }, status=400)
            
        # Realiza o checkout
        hora_atual = timezone.localtime().time().strftime('%H:%M')
        reserva.hora_checkout = hora_atual
        reserva.status = 'concluida'
        
        if observacoes:
            reserva.observacoes = f"{reserva.observacoes or ''}\n\nCheck-out: {observacoes}"
            
        reserva.save()
        
        # Registra o histórico
        Historico.objects.create(
            reserva=reserva,
            status_anterior='em_andamento',
            status_novo='concluida',
            descricao=f"Check-out realizado às {hora_atual} via calendário"
        )
        
        # Atualiza o status do quarto
        quarto = reserva.quarto
        quarto.status = 'disponivel'
        quarto.save()
        
        # Cria alerta para limpeza
        try:
            from quartos.models import LimpezaManutencao
            from django.contrib.auth.models import User
            
            admin = User.objects.filter(is_staff=True).first()
            
            LimpezaManutencao.objects.create(
                quarto=quarto,
                tipo='limpeza',
                status='pendente',
                prioridade='alta',
                data_agendada=timezone.now(),
                descricao=f"Limpeza pós check-out da reserva {reserva.codigo}",
                responsavel=admin
            )
            logger.info(f"Tarefa de limpeza criada para quarto {quarto.numero}")
        except Exception as e:
            logger.warning(f"Não foi possível criar tarefa de limpeza: {str(e)}")
        
        logger.info(f"Check-out da reserva {reserva.codigo} realizado via calendário")
        
        return JsonResponse({
            'status': 'success', 
            'message': 'Check-out realizado com sucesso'
        })
    except Exception as e:
        logger.error(f'Erro ao realizar check-out: {str(e)}')
        return JsonResponse({
            'status': 'error', 
            'message': f'Erro ao realizar check-out: {str(e)}'
        }, status=500)

def dias_com_reservas(request):
    """
    View para fornecer os dias que têm reservas em um determinado período.
    Retorna um objeto com a data e quantidade de reservas por dia.
    """
    start = request.GET.get('start')
    end = request.GET.get('end')
    
    try:
        start_date = datetime.strptime(start, '%Y-%m-%d').date()
        end_date = datetime.strptime(end, '%Y-%m-%d').date()
        
        # Busca reservas no período
        reservas = Reserva.objects.filter(
            check_in__lte=end_date,
            check_out__gte=start_date
        )
        
        # Mapeia os dias com reservas
        dias_reservas = {}
        
        # Para cada reserva, contabiliza todos os dias entre check-in e check-out
        for reserva in reservas:
            # Ajusta o intervalo para estar dentro do período solicitado
            data_inicio = max(reserva.check_in, start_date)
            data_fim = min(reserva.check_out, end_date)
            
            # Para cada dia deste intervalo
            dia_atual = data_inicio
            while dia_atual <= data_fim:
                dia_str = dia_atual.isoformat()  # formato 'YYYY-MM-DD'
                
                # Incrementa a contagem para este dia
                if dia_str in dias_reservas:
                    dias_reservas[dia_str] += 1
                else:
                    dias_reservas[dia_str] = 1
                
                # Avança para o próximo dia
                dia_atual += timedelta(days=1)
        
        # Converte o mapa em uma lista formatada para o frontend
        resultado = [{'data': data, 'quantidade': quantidade} for data, quantidade in dias_reservas.items()]
        
        logger.info(f'Consulta de dias com reservas para {start} a {end}: {len(resultado)} dias encontrados.')
        
        return JsonResponse({'dias': resultado})
    except Exception as e:
        logger.error(f'Erro ao buscar dias com reservas: {str(e)}')
        return JsonResponse({'error': str(e)}, status=400)

def registrar_pagamento_ajax(request):
    """
    View para registrar um pagamento para uma reserva via AJAX.
    Permite registrar pagamentos a qualquer momento durante a estadia.
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Método não permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        codigo_reserva = data.get('codigo_reserva')
        valor = float(data.get('valor', 0))
        forma_pagamento = data.get('forma_pagamento')
        observacoes = data.get('observacoes', '')
        
        # Validação básica
        if not codigo_reserva:
            return JsonResponse({'status': 'error', 'message': 'Código da reserva é obrigatório'}, status=400)
            
        if valor <= 0:
            return JsonResponse({'status': 'error', 'message': 'Valor do pagamento deve ser maior que zero'}, status=400)
            
        if not forma_pagamento:
            return JsonResponse({'status': 'error', 'message': 'Forma de pagamento é obrigatória'}, status=400)
        
        # Obtém a reserva
        reserva = get_object_or_404(Reserva, codigo=codigo_reserva)
        
        # Verifica se a reserva está ativa (pendente, confirmada ou em andamento)
        if reserva.status not in ['pendente', 'confirmada', 'em_andamento']:
            return JsonResponse({
                'status': 'error', 
                'message': f'Não é possível registrar pagamento. Status atual: {reserva.get_status_display()}'
            }, status=400)
        
        # Obtém o valor pendente (valor total - pagamentos já feitos)
        try:
            from financeiro.models import Pagamento
            pagamentos_anteriores = Pagamento.objects.filter(reserva=reserva).aggregate(
                total=models.Sum('valor')
            )['total'] or 0
            
            valor_pendente = float(reserva.valor_total) - float(pagamentos_anteriores)
            
            # Verifica se o valor do pagamento é maior que o pendente
            if valor > valor_pendente:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Valor do pagamento (R$ {valor:.2f}) excede o valor pendente (R$ {valor_pendente:.2f})'
                }, status=400)
                
            # Registra o pagamento
            pagamento = Pagamento.objects.create(
                reserva=reserva,
                valor=valor,
                tipo=forma_pagamento,
                status='aprovado',
                data_pagamento=timezone.now(),
                observacoes=observacoes
            )
            
            # Também registra como receita, se a reserva estiver em andamento
            if reserva.status == 'em_andamento':
                try:
                    from financeiro.models import Receita
                    Receita.objects.create(
                        descricao=f"Receita de hospedagem - Reserva {reserva.codigo}",
                        valor=valor,
                        categoria='hospedagem',  # Adicionar esta categoria nas opções
                        status='recebido',
                        data_receita=timezone.now().date(),
                        data_recebimento=timezone.now().date(),
                        observacoes=f"Pagamento registrado durante a estadia. Forma: {forma_pagamento}. {observacoes}".strip()
                    )
                    logger.info(f"Receita registrada para reserva {reserva.codigo}: R$ {valor}")
                except Exception as e:
                    logger.warning(f"Não foi possível registrar receita: {str(e)}")
            
            # Registra no histórico da reserva
            Historico.objects.create(
                reserva=reserva,
                status_anterior=reserva.status,
                status_novo=reserva.status,
                descricao=f"Pagamento de R$ {valor:.2f} registrado. Forma: {forma_pagamento}. {observacoes}"
            )
            
            # Retorna informações atualizadas
            novo_total_pago = float(pagamentos_anteriores) + valor
            valor_restante = float(reserva.valor_total) - novo_total_pago
            
            logger.info(f"Pagamento de R$ {valor:.2f} registrado para reserva {reserva.codigo}")
            
            return JsonResponse({
                'status': 'success',
                'message': 'Pagamento registrado com sucesso',
                'dados': {
                    'valor_total': float(reserva.valor_total),
                    'total_pago': novo_total_pago,
                    'valor_restante': valor_restante
                }
            })
            
        except Exception as e:
            logger.error(f"Erro ao processar pagamento: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': f'Erro ao registrar pagamento: {str(e)}'
            }, status=500)
            
    except Exception as e:
        logger.error(f'Erro ao processar requisição de pagamento: {str(e)}')
        return JsonResponse({
            'status': 'error',
            'message': f'Erro ao processar requisição: {str(e)}'
        }, status=500)
