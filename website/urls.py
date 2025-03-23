from django.urls import path
from . import views

app_name = 'website'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('quartos/', views.QuartosView.as_view(), name='quartos_lista'),
    path('sobre/', views.SobreView.as_view(), name='sobre'),
    path('contato/', views.ContatoView.as_view(), name='contato'),
    path('estrutura/', views.PaginaView.as_view(), {'tipo': 'estrutura'}, name='estrutura'),
] 