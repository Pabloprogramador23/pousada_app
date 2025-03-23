from django import forms
from .models import Contato

class ContatoForm(forms.ModelForm):
    """
    Formulário para envio de mensagens de contato.
    
    Baseado no modelo Contato, permite aos usuários enviarem mensagens
    através da página de contato do site.
    """
    class Meta:
        model = Contato
        fields = ['nome', 'email', 'telefone', 'assunto', 'mensagem']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite seu nome completo'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Digite seu e-mail'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control telefone-mask', 'placeholder': '(00) 00000-0000'}),
            'assunto': forms.Select(attrs={'class': 'form-select'}),
            'mensagem': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Digite sua mensagem', 'maxlength': 1000}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adiciona as opções de assunto
        self.fields['assunto'].choices = [
            ('', 'Selecione'),
            ('Informações', 'Informações'),
            ('Reservas', 'Reservas'),
            ('Sugestões', 'Sugestões'),
            ('Reclamações', 'Reclamações'),
            ('Outros', 'Outros'),
        ]
        
    def clean_telefone(self):
        """
        Padroniza o formato do número de telefone, removendo caracteres não numéricos.
        """
        telefone = self.cleaned_data.get('telefone', '')
        # Remove todos os caracteres não numéricos
        telefone = ''.join(filter(str.isdigit, telefone))
        return telefone 