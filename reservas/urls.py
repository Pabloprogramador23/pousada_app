from django.urls import path
from . import views

app_name = 'reservas'

urlpatterns = [
    path('', views.NovaReservaView.as_view(), name='criar'),
    path('confirmar/<str:codigo>/', views.ReservaConfirmarView.as_view(), name='confirmar'),
    path('confirmada/<str:codigo>/', views.ReservaConfirmadaView.as_view(), name='confirmada'),
    path('cancelar/<str:codigo>/', views.ReservaCancelarView.as_view(), name='cancelar'),
    path('verificar-disponibilidade/', views.verificar_disponibilidade, name='verificar_disponibilidade'),
    
    # Check-in e Check-out
    path('check-in/', views.CheckInView.as_view(), name='check_in'),
    path('check-in/realizar/<str:codigo>/', views.realizar_check_in, name='realizar_check_in'),
    path('check-in/direto/', views.CheckInDiretoView.as_view(), name='check_in_direto'),
    path('check-in/direto/processar/', views.processar_check_in_direto, name='processar_check_in_direto'),
    path('check-out/<str:codigo>/', views.realizar_check_out, name='realizar_check_out'),
    
    # Detalhes e Histórico
    path('detalhe/<str:codigo>/', views.DetalheReservaView.as_view(), name='detalhe_reserva'),
    
    # Calendário
    path('eventos-calendario/', views.eventos_calendario, name='eventos_calendario'),
    path('detalhes-dia/', views.detalhes_dia, name='detalhes_dia'),
    path('dias-com-reservas/', views.dias_com_reservas, name='dias_com_reservas'),
    path('cancelar-reserva-ajax/', views.cancelar_reserva_ajax, name='cancelar_reserva_ajax'),
    path('checkout-reserva-ajax/', views.checkout_reserva_ajax, name='checkout_reserva_ajax'),
    path('registrar-pagamento-ajax/', views.registrar_pagamento_ajax, name='registrar_pagamento_ajax'),
] 