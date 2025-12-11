from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import connection
from django.http import JsonResponse
from django.db import transaction
from django.contrib.auth.models import User
from .models import Producto, Carrito, Pedido, ItemPedido, Categoria, Oferta

# Verificar si las tablas existen
def check_tables_exist():
    """Verifica si las tablas existen en la base de datos"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'cafeteria_%'")
            tables = cursor.fetchall()
            return len(tables) > 0
    except:
        return False

# Vistas principales
def inicio(request):
    try:
        productos = Producto.objects.filter(disponible=True, cantidad__gt=0)[:6]
        ofertas = Oferta.objects.filter(activa=True)[:3]
    except Exception as e:
        print(f"Error cargando datos: {e}")
        productos = []
        ofertas = []
    
    return render(request, 'inicio.html', {
        'productos': productos,
        'ofertas': ofertas
    })

def productos(request):
    try:
        categoria_id = request.GET.get('categoria')
        productos = Producto.objects.filter(disponible=True, cantidad__gt=0)
        
        if categoria_id:
            productos = productos.filter(categoria_id=categoria_id)
        
        categorias = Categoria.objects.all()
    except Exception as e:
        print(f"Error cargando productos: {e}")
        productos = []
        categorias = []
    
    return render(request, 'productos.html', {
        'productos': productos,
        'categorias': categorias
    })

def ofertas(request):
    try:
        ofertas = Oferta.objects.filter(activa=True)
    except Exception as e:
        print(f"Error cargando ofertas: {e}")
        ofertas = []
    
    return render(request, 'ofertas.html', {'ofertas': ofertas})

def ubicaciones(request):
    return render(request, 'ubicaciones.html')

# Autenticación
def registro(request):
    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            email = request.POST.get('email')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            
            # Validaciones
            if not all([username, password1, password2, email, first_name, last_name]):
                messages.error(request, 'Todos los campos son obligatorios')
                return redirect('registro')
            
            if password1 != password2:
                messages.error(request, 'Las contraseñas no coinciden')
                return redirect('registro')
            
            if len(password1) < 8:
                messages.error(request, 'La contraseña debe tener al menos 8 caracteres')
                return redirect('registro')
            
            if User.objects.filter(username=username).exists():
                messages.error(request, 'El nombre de usuario ya existe')
                return redirect('registro')
            
            if User.objects.filter(email=email).exists():
                messages.error(request, 'El correo electrónico ya está registrado')
                return redirect('registro')
            
            # Crear usuario
            user = User.objects.create_user(
                username=username,
                password=password1,
                email=email,
                first_name=first_name,
                last_name=last_name
            )
            
            login(request, user)
            messages.success(request, f'¡Registro exitoso! Bienvenido/a {first_name}')
            return redirect('inicio')
            
        except Exception as e:
            messages.error(request, f'Error en el registro: {str(e)}')
    
    return render(request, 'registro.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'¡Bienvenido/a {user.first_name or user.username}!')
            return redirect('inicio')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión correctamente')
    return redirect('inicio')

# Vistas protegidas (requieren login)
@login_required
def perfil(request):
    try:
        pedidos = Pedido.objects.filter(usuario=request.user).order_by('-fecha_pedido')[:10]
    except Exception as e:
        print(f"Error cargando pedidos: {e}")
        pedidos = []
    
    return render(request, 'perfil.html', {'pedidos': pedidos})

@login_required
def carrito(request):
    try:
        items_carrito = Carrito.objects.filter(usuario=request.user)
        total = sum(item.subtotal() for item in items_carrito)
        
        # Debug en consola
        print(f"DEBUG CARRITO - Usuario: {request.user.username}")
        print(f"DEBUG CARRITO - Items encontrados: {items_carrito.count()}")
        for item in items_carrito:
            print(f"DEBUG CARRITO - {item.cantidad} x {item.producto.nombre} = ${item.subtotal()}")
            
    except Exception as e:
        print(f"Error cargando carrito: {e}")
        items_carrito = []
        total = 0
    
    return render(request, 'carrito.html', {
        'items_carrito': items_carrito,
        'total': total
    })

@login_required
def agregar_al_carrito(request, producto_id):
    try:
        producto = get_object_or_404(Producto, id=producto_id, disponible=True)
        
        # Verificar stock
        if producto.cantidad <= 0:
            messages.error(request, f'"{producto.nombre}" no tiene stock disponible')
            return redirect('productos')
        
        # Usar get_or_create para manejar el carrito
        carrito_item, created = Carrito.objects.get_or_create(
            usuario=request.user,
            producto=producto,
            defaults={'cantidad': 1}
        )
        
        if not created:
            carrito_item.cantidad += 1
            carrito_item.save()
            messages.success(request, f'Se agregó otra unidad de "{producto.nombre}" al carrito')
        else:
            messages.success(request, f'"{producto.nombre}" agregado al carrito')
        
        # Debug
        print(f"DEBUG AGREGAR - Usuario: {request.user.username}")
        print(f"DEBUG AGREGAR - Producto: {producto.nombre}")
        print(f"DEBUG AGREGAR - Creado: {created}")
        print(f"DEBUG AGREGAR - Carrito count: {Carrito.objects.filter(usuario=request.user).count()}")
        
        return redirect('carrito')
        
    except Producto.DoesNotExist:
        messages.error(request, 'Producto no encontrado')
        return redirect('productos')
    except Exception as e:
        messages.error(request, f'Error al agregar al carrito: {str(e)}')
        return redirect('productos')

@login_required
def actualizar_carrito(request, item_id):
    if request.method == 'POST':
        try:
            item = get_object_or_404(Carrito, id=item_id, usuario=request.user)
            cantidad = int(request.POST.get('cantidad', 1))
            
            if cantidad <= 0:
                item.delete()
                messages.success(request, 'Producto eliminado del carrito')
            else:
                item.cantidad = cantidad
                item.save()
                messages.success(request, 'Carrito actualizado')
                
        except Exception as e:
            messages.error(request, f'Error al actualizar carrito: {str(e)}')
    
    return redirect('carrito')

@login_required
def eliminar_del_carrito(request, item_id):
    try:
        item = get_object_or_404(Carrito, id=item_id, usuario=request.user)
        item.delete()
        messages.success(request, 'Producto eliminado del carrito')
    except Exception as e:
        messages.error(request, f'Error al eliminar del carrito: {str(e)}')
    
    return redirect('carrito')

@login_required
@transaction.atomic
def realizar_pedido(request):
    try:
        items_carrito = Carrito.objects.filter(usuario=request.user)
        
        if not items_carrito.exists():
            messages.error(request, 'Tu carrito está vacío')
            return redirect('carrito')
        
        # Calcular total
        total = sum(item.subtotal() for item in items_carrito)
        
        # Crear pedido
        pedido = Pedido.objects.create(
            usuario=request.user,
            total=total,
            estado='pendiente',
            metodo_pago='efectivo'
        )
        
        # Crear items del pedido y actualizar stock
        for item_carrito in items_carrito:
            ItemPedido.objects.create(
                pedido=pedido,
                producto=item_carrito.producto,
                cantidad=item_carrito.cantidad,
                precio=item_carrito.producto.precio
            )
            
            # Actualizar stock del producto
            producto = item_carrito.producto
            producto.cantidad -= item_carrito.cantidad
            producto.save()
        
        # Vaciar carrito
        items_carrito.delete()
        
        messages.success(request, f'¡Pedido realizado exitosamente! Número de pedido: #{pedido.id}')
        return redirect('perfil')
        
    except Exception as e:
        messages.error(request, f'Error al realizar pedido: {str(e)}')
        return redirect('carrito')

# Vistas adicionales
def contacto(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        mensaje = request.POST.get('mensaje')
        
        messages.success(request, '¡Mensaje enviado! Te contactaremos pronto.')
        return redirect('contacto')
    
    return render(request, 'contacto.html')

def acerca_de(request):
    return render(request, 'acerca_de.html')

# API simple para AJAX
def api_productos(request):
    try:
        productos = Producto.objects.filter(disponible=True).values('id', 'nombre', 'precio', 'descripcion')[:10]
        return JsonResponse({'productos': list(productos)})
    except:
        return JsonResponse({'productos': []})

# Manejo de errores
def handler404(request, exception):
    return render(request, '404.html', status=404)

def handler500(request):
    return render(request, '500.html', status=500)