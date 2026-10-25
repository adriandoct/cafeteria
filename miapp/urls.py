from django.urls import path
from . import views

urlpatterns = [
    # Vistas de Roles Principales
    path('', views.menu_cliente, name='menu_cliente'),
    path('caja/', views.modulo_cajero, name='modulo_cajero'),
    path('kds/', views.pantalla_kds, name='pantalla_kds'),
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),

    # Autenticación y Demostración Rápida
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('demo/rol/<str:nuevo_rol>/', views.cambiar_rol_demo, name='cambiar_rol_demo'),

    # APIs Transaccionales y Pasarela de Pago
    path('api/pedido/crear/', views.api_crear_pedido_cliente, name='api_crear_pedido_cliente'),
    path('api/mercadopago/webhook/', views.api_webhook_mercadopago, name='api_webhook_mercadopago'),
    path('api/pos/venta/', views.api_procesar_venta_mostrador, name='api_procesar_venta_mostrador'),
    path('api/kds/actualizar/', views.api_actualizar_estado_kds, name='api_actualizar_estado_kds'),
    path('api/corte-z/arqueo/', views.api_cierre_arqueo_ciego, name='api_cierre_arqueo_ciego'),
    path('api/corte-z/abrir/', views.api_abrir_turno, name='api_abrir_turno'),
    path('api/inventario/reabastecer/', views.api_reabastecer_inventario, name='api_reabastecer_inventario'),
    path('api/pedido/<str:order_id>/', views.api_consultar_pedido, name='api_consultar_pedido'),
]
