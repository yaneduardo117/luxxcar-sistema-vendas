from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Car
import re
from decimal import Decimal


# 1. Widget para habilitar o "múltiplos arquivos" no HTML
class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


# 2. CAMPO PERSONALIZADO: Ensina o Django a validar uma LISTA de arquivos
class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


# 3. Formulário de Veículos
class CarForm(forms.ModelForm):
    price = forms.CharField(label="Preço de Venda")

    # Transforma em CharField para o Django não barrar a vírgula antes da hora
    zero_to_hundred = forms.CharField(label="0-100 km/h (Segundos)")

    # Usando o novo campo inteligente
    galeria = MultipleFileField(
        required=False,
        label="Outras Fotos (Galeria)"
    )


    class Meta:
        model = Car
        exclude = ['created_at']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['body_type'].choices = [('', 'Selecione a Carroceria')] + Car.BODY_TYPE_CHOICES
        self.fields['segment'].choices = [('', 'Selecione o Segmento')] + Car.SEGMENT_CHOICES
        self.fields['image'].label = "Foto da Capa (Principal)"
        self.fields['brand'].empty_label = "Selecione a marca"

        campos_positivos = ['year', 'horsepower', 'seats']
        for campo in campos_positivos:
            self.fields[campo].widget.attrs['min'] = '0'

        # Máscara do Preço
        self.fields['price'].widget.attrs[
            'x-on:input'] = "let v = $event.target.value.replace(/\\D/g, ''); $event.target.value = (v / 100).toLocaleString('pt-BR', {style: 'currency', currency: 'BRL'});"
        self.fields['price'].widget.attrs['placeholder'] = "R$ 0,00"

        if self.instance and self.instance.pk and self.instance.price:
            valor_formatado = "{:,.2f}".format(self.instance.price)
            valor_formatado = valor_formatado.replace(",", "X").replace(".", ",").replace("X", ".")
            self.initial['price'] = f"R$ {valor_formatado}"

    # Limpeza do Preço
    def clean_price(self):
        price_str = self.cleaned_data.get('price')
        if price_str:
            cleaned_str = re.sub(r'[^\d,]', '', str(price_str))
            cleaned_str = cleaned_str.replace(',', '.')
            try:
                return Decimal(cleaned_str)
            except:
                raise forms.ValidationError("Valor de preço inválido.")
        return price_str


    # LIMPEZA DA VÍRGULA: Converte o "2,5" para "2.5" pro banco aceitar de boa
    def clean_zero_to_hundred(self):
        zth = self.cleaned_data.get('zero_to_hundred')
        if zth:
            try:
                # Transforma a string, garantindo que use ponto
                val_str = str(zth).replace(',', '.')
                # Converte para Decimal e força 1 casa decimal com o round()
                return round(Decimal(val_str), 1)

            except Exception:
                raise forms.ValidationError("Use apenas números e vírgula. Ex: 2,5")
        return zth


# Formulário de Cadastro de Usuários
class CadastroUsuarioForm(UserCreationForm):
    email = forms.EmailField(label="E-mail", required=True)

    class Meta:
        model = User
        fields = ("email",)

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este e-mail já está registado em nosso sistema.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data["email"]
        if commit:
            user.save()
        return user