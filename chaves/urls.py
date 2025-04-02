# chaves/urls.py
from django.urls import path
from .views import custom_login, janus_view, gerenciar_chaves, editar_chave, view_importar_chaves, view_atribuir_projetista, solicitacao_chave_view, pagina_de_sucesso_view, buscar_chave

urlpatterns = [
    path('login/', custom_login, name='login'),
    path('menu/', janus_view, name='janus_view'),
    path('gerenciar_chaves', gerenciar_chaves, name='gerenciar_chaves'),
    path('chaves/editar/<int:id>/', editar_chave, name='editar_chave'),
    path('importar-chaves/', view_importar_chaves, name='view_importar_chaves'),
    path('atribuir_projetista/', view_atribuir_projetista, name='atribuir_projetista'),
    path('solicitar-chaves/', solicitacao_chave_view, name='solicitar_chaves'),
    path('pagina-de-sucesso/', pagina_de_sucesso_view, name='pagina_de_sucesso'),
    path('buscar-chave/', buscar_chave, name='buscar_chave'),

]

