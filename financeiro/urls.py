from django.urls import path
from . import views

app_name = 'financeiro'

urlpatterns = [
    # Dashboard e Visão Geral
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('calendario/', views.CalendarioReservasView.as_view(), name='calendario'),
    path('relatorios/', views.RelatoriosView.as_view(), name='relatorios'),
    
    # Pagamentos
    path('pagamentos/', views.PagamentoListView.as_view(), name='pagamentos'),
    path('pagamentos/novo/', views.PagamentoCreateView.as_view(), name='pagamento_novo'),
    path('pagamentos/<int:pk>/', views.PagamentoDetailView.as_view(), name='pagamento_detalhe'),
    path('pagamentos/<int:pk>/editar/', views.PagamentoUpdateView.as_view(), name='pagamento_editar'),
    path('pagamentos/<int:pk>/aprovar/', views.aprovar_pagamento, name='aprovar_pagamento'),
    path('pagamentos/<int:pk>/rejeitar/', views.rejeitar_pagamento, name='rejeitar_pagamento'),
    path('pagamentos/<int:pk>/estornar/', views.estornar_pagamento, name='estornar_pagamento'),
    path('pagamentos/<int:pk>/recibo/', views.gerar_recibo, name='gerar_recibo'),
    
    # Despesas
    path('despesas/', views.DespesaListView.as_view(), name='despesas'),
    path('despesas/nova/', views.DespesaCreateView.as_view(), name='despesa_nova'),
    path('despesas/<int:pk>/', views.DespesaDetailView.as_view(), name='despesa_detalhe'),
    path('despesas/<int:pk>/editar/', views.DespesaUpdateView.as_view(), name='despesa_editar'),
    path('despesas/<int:pk>/marcar-como-pago/', views.marcar_despesa_como_paga, name='marcar_despesa_como_paga'),
    
    # Receitas
    path('receitas/', views.ReceitaListView.as_view(), name='receitas'),
    path('receitas/nova/', views.ReceitaCreateView.as_view(), name='receita_nova'),
    path('receitas/<int:pk>/', views.ReceitaDetailView.as_view(), name='receita_detalhe'),
    path('receitas/<int:pk>/editar/', views.ReceitaUpdateView.as_view(), name='receita_editar'),
    path('receitas/<int:pk>/marcar-como-recebido/', views.marcar_receita_como_recebida, name='marcar_receita_como_recebida'),
    
    # Alertas
    path('alertas/', views.AlertaListView.as_view(), name='alertas'),
    path('alertas/novo/', views.AlertaCreateView.as_view(), name='alerta_novo'),
    path('alertas/<int:pk>/', views.AlertaDetailView.as_view(), name='alerta_detalhe'),
    path('alertas/<int:pk>/editar/', views.AlertaUpdateView.as_view(), name='alerta_editar'),
    path('alertas/<int:pk>/resolver/', views.marcar_alerta_como_resolvido, name='alerta_resolver'),
    path('alertas/<int:pk>/visualizar/', views.marcar_alerta_como_visualizado, name='alerta_visualizar'),
] 