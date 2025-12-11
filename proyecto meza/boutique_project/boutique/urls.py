from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('productos/', views.productos, name='productos'),
    path('ofertas/', views.ofertas, name='ofertas'),
    path('ubicaciones/', views.ubicaciones, name='ubicaciones'),
    path('registro/', views.registro, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('perfil/', views.perfil, name='perfil'),
    path('carrito/', views.carrito, name='carrito'),
    path('agregar-carrito/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('actualizar-carrito/<int:item_id>/', views.actualizar_carrito, name='actualizar_carrito'),
    path('eliminar-carrito/<int:item_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('realizar-pedido/', views.realizar_pedido, name='realizar_pedido'),
    path('contacto/', views.contacto, name='contacto'),
    path('acerca-de/', views.acerca_de, name='acerca_de'),
]