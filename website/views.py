from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView, DetailView, FormView
from django.views.generic.base import ContextMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from quartos.models import CategoriaQuarto, Quarto
from .models import Banner, PaginaConteudo, Contato
from .forms import ContatoForm
import logging

logger = logging.getLogger(__name__)

class BannersContextMixin(ContextMixin):
    """
    Mixin para adicionar os banners ativos ao contexto das views.
    """
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['banners'] = Banner.objects.filter(ativo=True).order_by('ordem')
        return context

class HomeView(BannersContextMixin, TemplateView):
    """
    View para a página inicial do site.
    
    Renderiza o template principal com as informações de destaque.
    """
    template_name = 'website/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        logger.info('Página inicial acessada')
        context['categorias'] = CategoriaQuarto.objects.all()
        return context

class QuartosListView(BannersContextMixin, ListView):
    """
    View para listar todas as categorias de quartos.
    """
    model = CategoriaQuarto
    template_name = 'website/quartos_lista.html'
    context_object_name = 'categorias'
    
    def get_queryset(self):
        return CategoriaQuarto.objects.all()

class QuartosCategoriaView(BannersContextMixin, DetailView):
    """
    View para exibir detalhes de uma categoria de quarto.
    """
    model = CategoriaQuarto
    template_name = 'website/quartos_categoria.html'
    context_object_name = 'categoria'
    slug_field = 'nome'
    slug_url_kwarg = 'categoria'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['quartos'] = Quarto.objects.filter(categoria=self.object, status='disponivel')
        return context

class PaginaView(BannersContextMixin, DetailView):
    """
    View para exibir páginas de conteúdo como Sobre, Estrutura, etc.
    """
    model = PaginaConteudo
    template_name = 'website/pagina.html'
    context_object_name = 'pagina'
    
    def get_object(self):
        if 'slug' in self.kwargs:
            return get_object_or_404(PaginaConteudo, slug=self.kwargs['slug'], ativo=True)
        elif 'tipo' in self.kwargs:
            return get_object_or_404(PaginaConteudo, tipo=self.kwargs['tipo'], ativo=True)
        return None

class QuartosView(TemplateView):
    """
    View para a página de quartos.
    
    Renderiza a lista de tipos de quartos disponíveis na pousada.
    """
    template_name = 'website/quartos.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        logger.info('Página de quartos acessada')
        return context

class SobreView(TemplateView):
    """
    View para a página sobre nós.
    
    Renderiza informações sobre a pousada, história e valores.
    """
    template_name = 'website/sobre.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        logger.info('Página sobre acessada')
        return context

class ContatoView(FormView):
    """
    View para a página de contato.
    
    Renderiza o formulário de contato e processa o envio de mensagens.
    """
    template_name = 'website/contato.html'
    form_class = ContatoForm
    success_url = reverse_lazy('website:contato')

    def form_valid(self, form):
        """
        Salva a mensagem de contato e exibe confirmação.
        """
        try:
            form.save()
            messages.success(self.request, 'Sua mensagem foi enviada com sucesso! Em breve entraremos em contato.')
            logger.info('Nova mensagem de contato enviada')
        except Exception as e:
            messages.error(self.request, 'Ocorreu um erro ao enviar sua mensagem. Por favor, tente novamente.')
            logger.error(f'Erro ao salvar contato: {str(e)}')
        return super().form_valid(form)
