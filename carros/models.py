from django.db import models
from django.contrib.auth.models import User
from django.db import transaction


# Modelo de Marca para categorizar
class Brand(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nome da Marca")

    def __str__(self):
        return self.name


# Entidade Principal: Carro
class Car(models.Model):
    # Opções para o tipo de combustível e transmissão
    FUEL_CHOICES = [
        ('Electric', 'Elétrico'),
        ('Gasoline', 'Gasolina'),
        ('Hybrid', 'Híbrido'),
    ]

    TRANSMISSION_CHOICES = [
        ('Automatic', 'Automático'),
        ('Manual', 'Manual'),
    ]

    # --- DIMENSÕES ESTRUTURAIS ---
    BODY_TYPE_CHOICES = [
        ('SUV', 'SUV'),
        ('Sedan', 'Sedan'),
        ('Hatch', 'Hatchback'),
        ('Coupe', 'Coupé'),
        ('Convertible', 'Conversível'),
        ('Pickup', 'Picape'),
        ('Wagon', 'Perua/Wagon'),
    ]

    SEGMENT_CHOICES = [
        ('Luxury', 'Luxo'),
        ('Premium', 'Premium'),
        ('Sports', 'Esportivo Puro'),
        ('Standard', 'Padrão'),
    ]

    STATUS_CHOICES = [
        ('AVAILABLE', 'Disponível'),
        ('RESERVED', 'Reservado'),
        ('SOLD', 'Vendido'),
    ]


    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='cars', verbose_name="Marca")
    model_name = models.CharField(max_length=200, verbose_name="Modelo")
    year = models.IntegerField(verbose_name="Ano")
    body_type = models.CharField(max_length=20, choices=BODY_TYPE_CHOICES, null=True, blank=True,verbose_name="Carroceria")
    segment = models.CharField(max_length=20, choices=SEGMENT_CHOICES, null=True, blank=True, verbose_name="Segmento")

    # Preço de venda
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço de Venda")

    # Especificações técnicas
    horsepower = models.IntegerField(verbose_name="Cavalos de Potência (HP)")
    transmission = models.CharField(max_length=20, choices=TRANSMISSION_CHOICES, default='Automatic')
    seats = models.IntegerField(verbose_name="Assentos")
    zero_to_hundred = models.DecimalField(max_digits=4, decimal_places=1, verbose_name="0-100 km/h (Segundos)",null=True, blank=True)
    drivetrain = models.CharField(max_length=50, verbose_name="Tração (Ex: AWD, RWD)", default="AWD")

    # Imagem de destaque do carro
    image = models.ImageField(upload_to='cars/', verbose_name="Foto do Veículo")

    # Controle de sistema
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AVAILABLE',verbose_name="Status do Veículo")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.brand.name} {self.model_name} ({self.year})"


class CarImage(models.Model):
    # Conecta a imagem ao Carro. O related_name='galeria' permite acessar as fotos facilmente depois
    car = models.ForeignKey(Car, related_name='galeria', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='cars/gallery/')

    def __str__(self):
        return f"Foto da galeria: {self.car.model_name}"


class Sale(models.Model):
    PAYMENT_CHOICES = [
        ('PIX', 'Pix (Desconto de 5%)'),
        ('CREDIT', 'Cartão de Crédito (Até 12x)'),
        ('FINANCE', 'Financiamento Bancário'),
        ('TED', 'Transferência TED/DOC'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pendente (Aguardando Pagamento)'),
        ('APPROVED', 'Aprovado (Pago)'),
        ('CANCELLED', 'Cancelado'),
    ]

    car = models.ForeignKey(Car, on_delete=models.PROTECT, related_name='sales', verbose_name="Carro")
    customer_name = models.CharField(max_length=200, verbose_name="Comprador")
    customer_email = models.EmailField(verbose_name="E-mail")
    customer_phone = models.CharField(max_length=20, verbose_name="Telefone")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, verbose_name="Pagamento")
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor Fechado")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', verbose_name="Status da Venda")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Venda #{self.id} - {self.car.model_name}"

    # LÓGICA DE NEGÓCIO CENTRALIZADA (Tranca o banco, atualiza pedido, carro e notifica)
    def approve(self):
        with transaction.atomic():
            sale = Sale.objects.select_for_update().get(id=self.id)
            car = Car.objects.select_for_update().get(id=sale.car.id)

            if sale.status != 'PENDING': return False

            sale.status = 'APPROVED'
            sale.save()
            car.status = 'SOLD'
            car.save()

            Notification.objects.create(
                message=f"Pedido #{sale.id} Aprovado! {car.model_name} vendido.",
                notification_type='APPROVED',
                url=f"/dashboard/sales/{sale.id}/"
            )
            return True

    def cancel(self):
        with transaction.atomic():
            sale = Sale.objects.select_for_update().get(id=self.id)
            car = Car.objects.select_for_update().get(id=sale.car.id)

            if sale.status != 'PENDING': return False

            sale.status = 'CANCELLED'
            sale.save()
            car.status = 'AVAILABLE'
            car.save()

            Notification.objects.create(
                message=f"Pedido #{sale.id} Cancelado. {car.model_name} voltou ao estoque.",
                notification_type='EDIT',
                url=f"/dashboard/sales/{sale.id}/"
            )
            return True


class Notification(models.Model):
    TYPE_CHOICES = [
        ('SALE', 'Venda/Reserva Realizada'),
        ('APPROVED', 'Venda Aprovada'),
        ('EDIT', 'Veículo Atualizado'),
        ('DELETE', 'Veículo Excluído'),
    ]

    message = models.CharField(max_length=255)
    notification_type = models.CharField(max_length=15, choices=TYPE_CHOICES, default='SALE')
    is_read = models.BooleanField(default=False)
    url = models.CharField(max_length=255, blank=True, null=True, verbose_name="Link de Destino")  # NOVO CAMPO
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']