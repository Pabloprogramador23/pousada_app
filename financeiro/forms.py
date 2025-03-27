from django import forms
from django.utils import timezone
from .models import Pagamento, Despesa, Receita, Alerta
from reservas.models import Reserva

class PagamentoForm(forms.ModelForm):
    """
    Formulário para registro de pagamentos associados a reservas.
    """
    class Meta:
        model = Pagamento
        fields = ['reserva', 'valor', 'tipo', 'status', 'data_pagamento', 'codigo_transacao', 'comprovante', 'observacoes']
        widgets = {
            'reserva': forms.Select(attrs={'class': 'form-select'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'data_pagamento': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'codigo_transacao': forms.TextInput(attrs={'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super(PagamentoForm, self).__init__(*args, **kwargs)
        
        # Limita as reservas mostradas para aquelas que ainda estão pendentes ou confirmadas
        self.fields['reserva'].queryset = Reserva.objects.filter(
            status__in=['pendente', 'confirmada', 'em_andamento']
        )
        
        # Se já existir uma reserva selecionada, define o valor padrão para o valor total dela
        if 'initial' in kwargs and 'reserva' in kwargs['initial']:
            reserva_id = kwargs['initial']['reserva']
            try:
                reserva = Reserva.objects.get(id=reserva_id)
                self.fields['valor'].initial = reserva.valor_total
            except Reserva.DoesNotExist:
                pass


class DespesaForm(forms.ModelForm):
    """
    Formulário para registro de despesas da pousada.
    """
    class Meta:
        model = Despesa
        fields = ['descricao', 'valor', 'categoria', 'status', 'data_despesa', 'data_vencimento', 
                 'data_pagamento', 'comprovante', 'observacoes']
        widgets = {
            'descricao': forms.TextInput(attrs={'class': 'form-control'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'data_despesa': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'data_vencimento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'data_pagamento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super(DespesaForm, self).__init__(*args, **kwargs)
        # Define data padrão como hoje
        if not self.instance.pk:
            self.fields['data_despesa'].initial = timezone.now().date()
            
    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        data_pagamento = cleaned_data.get('data_pagamento')
        
        # Se o status for "pago", exige data de pagamento
        if status == 'pago' and not data_pagamento:
            self.add_error('data_pagamento', 'A data de pagamento é obrigatória quando a despesa está paga.')
            
        # Verifica se a data de vencimento é posterior à data da despesa
        data_despesa = cleaned_data.get('data_despesa')
        data_vencimento = cleaned_data.get('data_vencimento')
        if data_despesa and data_vencimento and data_vencimento < data_despesa:
            self.add_error('data_vencimento', 'A data de vencimento não pode ser anterior à data da despesa.')
            
        return cleaned_data


class ReceitaForm(forms.ModelForm):
    """
    Formulário para registro de receitas da pousada.
    """
    class Meta:
        model = Receita
        fields = ['descricao', 'valor', 'categoria', 'status', 'data_receita', 
                 'data_recebimento', 'comprovante', 'observacoes', 'recorrente']
        widgets = {
            'descricao': forms.TextInput(attrs={'class': 'form-control'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'data_receita': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'data_recebimento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'recorrente': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super(ReceitaForm, self).__init__(*args, **kwargs)
        # Define data padrão como hoje
        if not self.instance.pk:
            self.fields['data_receita'].initial = timezone.now().date()
            
    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        data_recebimento = cleaned_data.get('data_recebimento')
        
        # Se o status for "recebido", exige data de recebimento
        if status == 'recebido' and not data_recebimento:
            self.add_error('data_recebimento', 'A data de recebimento é obrigatória quando a receita foi recebida.')
            
        return cleaned_data


class AlertaForm(forms.ModelForm):
    """
    Formulário para registro de alertas financeiros.
    """
    class Meta:
        model = Alerta
        fields = ['titulo', 'mensagem', 'tipo', 'prioridade', 'data_vencimento', 
                 'reserva', 'despesa', 'receita']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'mensagem': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'prioridade': forms.Select(attrs={'class': 'form-select'}),
            'data_vencimento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'reserva': forms.Select(attrs={'class': 'form-select'}),
            'despesa': forms.Select(attrs={'class': 'form-select'}),
            'receita': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super(AlertaForm, self).__init__(*args, **kwargs)
        
        # Filtra as opções para mostrar apenas os itens relevantes
        self.fields['reserva'].queryset = Reserva.objects.filter(status__in=['pendente', 'confirmada'])
        self.fields['despesa'].queryset = Despesa.objects.filter(status__in=['pendente', 'atrasado'])
        self.fields['receita'].queryset = Receita.objects.filter(status__in=['pendente', 'atrasado'])
        
        # Torna os campos de relacionamento não obrigatórios
        self.fields['reserva'].required = False
        self.fields['despesa'].required = False
        self.fields['receita'].required = False


class FiltroPeriodoForm(forms.Form):
    """
    Formulário para filtrar relatórios por período.
    """
    data_inicio = forms.DateField(
        label='Data inicial',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    data_fim = forms.DateField(
        label='Data final',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    
    def __init__(self, *args, **kwargs):
        super(FiltroPeriodoForm, self).__init__(*args, **kwargs)
        # Define datas padrão como início do mês atual até hoje
        hoje = timezone.now().date()
        inicio_mes = hoje.replace(day=1)
        
        if not self.is_bound:  # Se o formulário não foi submetido
            self.fields['data_inicio'].initial = inicio_mes
            self.fields['data_fim'].initial = hoje
    
    def clean(self):
        cleaned_data = super().clean()
        data_inicio = cleaned_data.get('data_inicio')
        data_fim = cleaned_data.get('data_fim')
        
        if data_inicio and data_fim and data_inicio > data_fim:
            self.add_error('data_inicio', 'A data inicial não pode ser posterior à data final.')
            
        return cleaned_data 