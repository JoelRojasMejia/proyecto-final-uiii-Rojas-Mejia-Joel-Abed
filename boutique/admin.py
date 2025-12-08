from django.contrib import admin
from .models import Categoria, Producto, Carrito, Pedido, ItemPedido, Oferta

class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'precio', 'categoria', 'cantidad', 'disponible', 'fecha_creacion']
    list_filter = ['categoria', 'disponible', 'fecha_creacion']
    search_fields = ['nombre', 'descripcion']
    list_editable = ['precio', 'cantidad', 'disponible']
    readonly_fields = ['fecha_creacion']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'descripcion', 'categoria')
        }),
        ('Precio y Stock', {
            'fields': ('precio', 'cantidad', 'disponible')
        }),
        ('Imagen', {
            'fields': ('imagen',),
            'classes': ('collapse',)
        }),
    )

class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'descripcion_corta']
    search_fields = ['nombre', 'descripcion']
    
    def descripcion_corta(self, obj):
        return obj.descripcion[:50] + '...' if len(obj.descripcion) > 50 else obj.descripcion
    descripcion_corta.short_description = 'Descripción'

class PedidoAdmin(admin.ModelAdmin):
    list_display = ['id', 'usuario', 'estado', 'total', 'fecha_pedido', 'metodo_pago']
    list_filter = ['estado', 'metodo_pago', 'fecha_pedido']
    search_fields = ['usuario__username', 'usuario__first_name', 'usuario__last_name']
    readonly_fields = ['fecha_pedido', 'fecha_actualizacion', 'total']
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ['usuario']
        return self.readonly_fields

class OfertaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo_descuento', 'valor_descuento', 'fecha_inicio', 'fecha_fin', 'activa', 'esta_activa']
    list_filter = ['activa', 'tipo_descuento', 'fecha_inicio']
    list_editable = ['activa']
    filter_horizontal = ['productos']
    
    def esta_activa(self, obj):
        return obj.esta_activa()
    esta_activa.boolean = True
    esta_activa.short_description = 'Vigente'

class CarritoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'producto', 'cantidad', 'subtotal', 'fecha_agregado']
    list_filter = ['fecha_agregado']
    search_fields = ['usuario__username', 'producto__nombre']

# Registrar modelos en el admin
admin.site.register(Categoria, CategoriaAdmin)
admin.site.register(Producto, ProductoAdmin)
admin.site.register(Carrito, CarritoAdmin)
admin.site.register(Pedido, PedidoAdmin)
admin.site.register(ItemPedido)
admin.site.register(Oferta, OfertaAdmin)