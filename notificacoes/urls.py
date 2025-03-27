from django.urls import path
from . import views

app_name = 'notificacoes'

urlpatterns = [
    path('', views.listar_notificacoes, name='listar'),
    path('<int:pk>/marcar-como-lida/', views.marcar_como_lida, name='marcar_como_lida'),
    path('recentes/', views.notificacoes_recentes_json, name='recentes_json'),
] 