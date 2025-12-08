from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'

class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    precio = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    cantidad = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    descripcion = models.TextField()
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)
    disponible = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.nombre} - ${self.precio}"
    
    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['nombre']

class Carrito(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    fecha_agregado = models.DateTimeField(auto_now_add=True)
    
    def subtotal(self):
        return self.cantidad * self.producto.precio
    
    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} - {self.usuario.username}"
    
    class Meta:
        verbose_name = 'Carrito'
        verbose_name_plural = 'Carritos'
        unique_together = ['usuario', 'producto']

class Pedido(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('confirmado', 'Confirmado'),
        ('preparando', 'Preparando'),
        ('listo', 'Listo para recoger'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]
    
    METODO_PAGO_CHOICES = [
        ('efectivo', 'Efectivo'),
        ('tarjeta', 'Tarjeta de crédito/débito'),
        ('transferencia', 'Transferencia bancaria'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    metodo_pago = models.CharField(max_length=20, choices=METODO_PAGO_CHOICES, default='efectivo')
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notas = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Pedido #{self.id} - {self.usuario.username} - ${self.total}"
    
    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-fecha_pedido']

class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField(validators=[MinValueValidator(1)])
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    
    def subtotal(self):
        return self.cantidad * self.precio
    
    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} - Pedido #{self.pedido.id}"
    
    class Meta:
        verbose_name = 'Item de Pedido'
        verbose_name_plural = 'Items de Pedido'

class Oferta(models.Model):
    TIPO_DESCUENTO_CHOICES = [
        ('porcentaje', 'Porcentaje'),
        ('monto_fijo', 'Monto fijo'),
    ]
    
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    tipo_descuento = models.CharField(max_length=20, choices=TIPO_DESCUENTO_CHOICES)
    valor_descuento = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_inicio = models.DateTimeField(default=timezone.now)
    fecha_fin = models.DateTimeField()
    productos = models.ManyToManyField(Producto, blank=True, related_name='ofertas')
    imagen = models.ImageField(upload_to='ofertas/', null=True, blank=True)
    activa = models.BooleanField(default=True)
    
    def __str__(self):
        return self.nombre
    
    def esta_activa(self):
        ahora = timezone.now()
        return self.activa and self.fecha_inicio <= ahora <= self.fecha_fin
    
    class Meta:
        verbose_name = 'Oferta'
        verbose_name_plural = 'Ofertas'
        ordering = ['-fecha_inicio']