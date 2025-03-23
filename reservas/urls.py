from django.urls import path
from . import views

app_name = 'reservas'

urlpatterns = [
    path('nova/', views.NovaReservaView.as_view(), name='criar'),
    path('confirmar/<str:codigo>/', views.ReservaConfirmarView.as_view(), name='confirmar'),
    path('confirmada/<str:codigo>/', views.ReservaConfirmadaView.as_view(), name='confirmada'),
    path('cancelar/<str:codigo>/', views.ReservaCancelarView.as_view(), name='cancelar'),
    path('verificar-disponibilidade/', views.verificar_disponibilidade, name='verificar_disponibilidade'),
] 