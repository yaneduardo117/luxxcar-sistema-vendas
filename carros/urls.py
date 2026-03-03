from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('veiculos/', views.catalogo_veiculos, name='catalogo_veiculos'),
    path('sobre/', views.sobre, name='sobre'),
    path('contato/', views.contato, name='contato'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('carro/<int:carro_id>/deletar/', views.deletar_carro, name='deletar_carro'),
    path('carro/novo/', views.criar_carro, name='criar_carro'),
    path('carro/<int:carro_id>/editar/', views.editar_carro, name='editar_carro'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('carro/<int:id>/', views.carro_detalhes, name='carro_detalhes'),
    path('checkout/<int:car_id>/', views.checkout_prep, name='checkout_prep'),
    path('checkout/<int:car_id>/confirm/', views.checkout_confirm, name='checkout_confirm'),
    path('sucesso/<int:sale_id>/', views.compra_sucesso, name='compra_sucesso'),

    # Gestão de Pedidos
    path('dashboard/sales/<int:sale_id>/', views.sale_detail, name='sale_detail'),
    path('dashboard/sales/<int:sale_id>/approve/', views.approve_sale, name='approve_sale'),
    path('dashboard/sales/<int:sale_id>/cancel/', views.cancel_sale, name='cancel_sale'),

    # Central de Notificações
    path('notificacoes/dropdown/', views.notifications_dropdown, name='notifications_dropdown'),
    path('notificacoes/ler-todas/', views.mark_all_read, name='mark_all_read'),
]