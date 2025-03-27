from django.urls import path
from . import views

app_name = 'hospedes'

urlpatterns = [
    # URL base para listagem de hóspedes
    path('', views.lista_hospedes, name='lista_hospedes'),
    
    # Detalhes de hóspede específico
    path('<int:hospede_id>/', views.detalhes_hospede, name='detalhes_hospede'),
] 