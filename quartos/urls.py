from django.urls import path
from . import views

app_name = 'quartos'

urlpatterns = [
    # Quartos
    path('', views.QuartoListView.as_view(), name='quarto_list'),
    path('<int:pk>/', views.QuartoDetailView.as_view(), name='quarto_detail'),
    path('<int:pk>/desconto/', views.aplicar_desconto, name='aplicar_desconto'),
    
    # Limpeza e Manutenção
    path('limpeza-manutencao/', views.LimpezaManutencaoListView.as_view(), name='limpeza_manutencao_list'),
    path('limpeza-manutencao/nova/', views.LimpezaManutencaoCreateView.as_view(), name='limpeza_manutencao_create'),
    path('limpeza-manutencao/<int:pk>/', views.LimpezaManutencaoDetailView.as_view(), name='limpeza_manutencao_detail'),
    path('limpeza-manutencao/<int:pk>/editar/', views.LimpezaManutencaoUpdateView.as_view(), name='limpeza_manutencao_update'),
    path('limpeza-manutencao/<int:pk>/iniciar/', views.iniciar_tarefa, name='iniciar_tarefa'),
    path('limpeza-manutencao/<int:pk>/concluir/', views.concluir_tarefa, name='concluir_tarefa'),
    path('limpeza-manutencao/<int:pk>/checklist/', views.atualizar_checklist, name='atualizar_checklist'),
] 