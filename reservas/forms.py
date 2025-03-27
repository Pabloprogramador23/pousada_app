from django import forms
from .models import Reserva
from quartos.models import Quarto
import re
import logging
from datetime import date

logger = logging.getLogger(__name__)

class ReservaForm(forms.ModelForm):
    """
    Formulário para criação de reservas no sistema.
    """
    # Campo oculto para identificar hóspede existente
    hospede_id = forms.IntegerField(required=False, widget=forms.HiddenInput())
    
    # Campos extras que não estão no modelo
    nome = forms.CharField(max_length=100, required=True, 
                          widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome completo'}))
    
    email = forms.EmailField(max_length=100, required=True,
                            widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@exemplo.com'}))
    
    telefone = forms.CharField(max_length=15, required=True,
                              widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(00) 00000-0000'}))
    
    # CPF formatado com máscara
    cpf = forms.CharField(max_length=14, label="CPF", 
                          widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '000.000.000-00'}))
    
    class Meta:
        model = Reserva
        fields = ['check_in', 'check_out', 'quarto', 'quantidade_adultos', 'quantidade_criancas', 'observacoes']
        widgets = {
            'check_in': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'check_out': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'quarto': forms.Select(attrs={'class': 'form-control'}),
            'quantidade_adultos': forms.Select(attrs={'class': 'form-control'}),
            'quantidade_criancas': forms.Select(attrs={'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 
                                                'placeholder': 'Observações ou solicitações especiais'})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Opções para número de adultos
        self.fields['quantidade_adultos'].widget.choices = [(i, str(i)) for i in range(1, 6)]
        
        # Opções para número de crianças
        self.fields['quantidade_criancas'].widget.choices = [(i, str(i)) for i in range(0, 4)]
        
        # Filtra apenas quartos disponíveis
        self.fields['quarto'].queryset = Quarto.objects.filter(disponivel=True)
    
    def clean(self):
        """
        Valida os dados do formulário.
        """
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in')
        check_out = cleaned_data.get('check_out')
        quarto = cleaned_data.get('quarto')
        
        if check_in and check_out:
            # Valida que check-in é antes de check-out
            if check_in >= check_out:
                self.add_error('check_in', 'A data de check-in deve ser anterior à data de check-out')
            
            # Valida que check-in não é no passado
            hoje = date.today()
            if check_in < hoje:
                self.add_error('check_in', 'A data de check-in não pode ser no passado')
                
            # Verifica se o quarto está disponível para o período
            if quarto:
                reservas_sobrepostas = Reserva.objects.filter(
                    quarto=quarto,
                    check_in__lt=check_out,
                    check_out__gt=check_in,
                    status__in=['confirmada', 'pendente']
                )
                
                if reservas_sobrepostas.exists():
                    self.add_error('quarto', 'Este quarto não está disponível para o período selecionado')
        
        return cleaned_data
    
    def clean_telefone(self):
        """
        Remove formatação do telefone, mantendo apenas os números.
        """
        telefone = self.cleaned_data.get('telefone')
        if telefone:
            telefone = re.sub(r'\D', '', telefone)
        return telefone
    
    def clean_cpf(self):
        """
        Remove formatação do CPF, mantendo apenas os números.
        """
        cpf = self.cleaned_data.get('cpf')
        if cpf:
            cpf = re.sub(r'\D', '', cpf)
            
            # Validação básica de CPF (11 dígitos)
            if len(cpf) != 11:
                raise forms.ValidationError('CPF deve ter 11 dígitos')
                
        return cpf 