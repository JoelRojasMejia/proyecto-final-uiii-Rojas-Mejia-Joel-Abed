from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario, Producto, Pedido

class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True)
    nombre = forms.CharField(max_length=100, required=True)
    apellido = forms.CharField(max_length=100, required=True)
    numero_telefonico = forms.CharField(max_length=15, required=False)

    class Meta:
        model = Usuario
        fields = ['username', 'nombre', 'apellido', 'email', 'numero_telefonico', 'password1', 'password2']

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre_producto', 'precio', 'cantidad', 'descripcion', 'categoria', 'imagen']

class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['metodo_de_pago']