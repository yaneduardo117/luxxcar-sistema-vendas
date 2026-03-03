import requests
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.utils.text import slugify
from django.db import transaction
from carros.models import Brand, Car, CarImage
import time


class Command(BaseCommand):
    help = 'Popula o banco de dados com veículos de luxo e imagens de alta qualidade'

    def baixar_imagem(self, url):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return ContentFile(response.content)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Erro ao baixar imagem: {e}"))
        return None

    def handle(self, *args, **kwargs):
        galeria_urls = [
            "https://images.unsplash.com/photo-1614200179396-2bdb77ebf81b?q=80&w=1920&auto=format&fit=crop",
            "https://images.unsplash.com/photo-1600705722908-bab1e6191c94?q=80&w=1920&auto=format&fit=crop",
            "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?q=80&w=1920&auto=format&fit=crop",
            "https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?q=80&w=1920&auto=format&fit=crop"
        ]

        # OS 9 NOVOS CARROS
        frota = [
            {"brand": "Mercedes-Benz", "model": "G63 AMG", "year": 2023, "body": "SUV", "segment": "Premium",
             "price": 1800000.00, "hp": 585, "trans": "Automatic", "seats": 5, "zth": 4.5, "drive": "AWD",
             "img_url": "https://images.unsplash.com/photo-1520031441872-265e4ff70366?q=80&w=1920&auto=format&fit=crop"},
            {"brand": "McLaren", "model": "720S", "year": 2022, "body": "Coupe", "segment": "Sports",
             "price": 3200000.00, "hp": 720, "trans": "Automatic", "seats": 2, "zth": 2.9, "drive": "RWD",
             "img_url": "https://images.unsplash.com/photo-1620882814836-98a28f89b252?q=80&w=1920&auto=format&fit=crop"},
            {"brand": "Aston Martin", "model": "DB11", "year": 2023, "body": "Coupe", "segment": "Luxury",
             "price": 2800000.00, "hp": 630, "trans": "Automatic", "seats": 4, "zth": 3.7, "drive": "RWD",
             "img_url": "https://images.unsplash.com/photo-1603512966373-c15bc56722d3?q=80&w=1920&auto=format&fit=crop"},
            {"brand": "Bentley", "model": "Continental GT", "year": 2024, "body": "Coupe", "segment": "Luxury",
             "price": 3500000.00, "hp": 650, "trans": "Automatic", "seats": 4, "zth": 3.6, "drive": "AWD",
             "img_url": "https://images.unsplash.com/photo-1571216503901-4dd998e3fb35?q=80&w=1920&auto=format&fit=crop"},
            {"brand": "Porsche", "model": "Taycan Turbo S", "year": 2024, "body": "Sedan", "segment": "Sports",
             "price": 1600000.00, "hp": 761, "trans": "Automatic", "seats": 4, "zth": 2.8, "drive": "AWD",
             "img_url": "https://images.unsplash.com/photo-1614162692292-7ac56d7f7f1e?q=80&w=1920&auto=format&fit=crop"},
            {"brand": "Land Rover", "model": "Range Rover SV", "year": 2024, "body": "SUV", "segment": "Luxury",
             "price": 2200000.00, "hp": 606, "trans": "Automatic", "seats": 5, "zth": 4.3, "drive": "AWD",
             "img_url": "https://images.unsplash.com/photo-1606016159991-dfce9e09d803?q=80&w=1920&auto=format&fit=crop"},
            {"brand": "Ferrari", "model": "SF90 Stradale", "year": 2024, "body": "Coupe", "segment": "Sports",
             "price": 4500000.00, "hp": 1000, "trans": "Automatic", "seats": 2, "zth": 2.5, "drive": "AWD",
             "img_url": "https://images.unsplash.com/photo-1614377284368-a6d4f911edc7?q=80&w=1920&auto=format&fit=crop"},
            {"brand": "Lamborghini", "model": "Huracan EVO", "year": 2023, "body": "Coupe", "segment": "Sports",
             "price": 3100000.00, "hp": 640, "trans": "Automatic", "seats": 2, "zth": 2.9, "drive": "AWD",
             "img_url": "https://images.unsplash.com/photo-1603386329225-868f9b1ee6c9?q=80&w=1920&auto=format&fit=crop"},
            {"brand": "Audi", "model": "RS7 Sportback", "year": 2024, "body": "Sedan", "segment": "Premium",
             "price": 1100000.00, "hp": 600, "trans": "Automatic", "seats": 5, "zth": 3.6, "drive": "AWD",
             "img_url": "https://images.unsplash.com/photo-1607853202273-797f1c22a38e?q=80&w=1920&auto=format&fit=crop"}
        ]

        self.stdout.write(self.style.WARNING("Iniciando a importação da frota LuxxCar (Fase 2)..."))

        for dados in frota:
            self.stdout.write(f"\nBaixando e processando: {dados['brand']} {dados['model']}...")

            with transaction.atomic():
                marca, _ = Brand.objects.get_or_create(name=dados['brand'])

                if Car.objects.filter(model_name=dados['model']).exists():
                    self.stdout.write(self.style.NOTICE(f"--> {dados['model']} já existe no banco. Pulando."))
                    continue

                carro = Car(
                    brand=marca, model_name=dados['model'], year=dados['year'],
                    body_type=dados['body'], segment=dados['segment'], price=dados['price'],
                    horsepower=dados['hp'], transmission=dados['trans'], seats=dados['seats'],
                    zero_to_hundred=dados['zth'], drivetrain=dados['drive'], status='AVAILABLE'
                )

                imagem_principal = self.baixar_imagem(dados['img_url'])
                if imagem_principal:
                    nome_arquivo = f"{slugify(dados['brand'] + '-' + dados['model'])}.jpg"
                    carro.image.save(nome_arquivo, imagem_principal, save=False)

                carro.save()
                self.stdout.write(self.style.SUCCESS("--> Carro salvo com sucesso!"))

                for i, url in enumerate(galeria_urls):
                    img_galeria = self.baixar_imagem(url)
                    if img_galeria:
                        nome_galeria = f"{slugify(dados['model'])}-galeria-{i + 1}.jpg"
                        nova_foto = CarImage(car=carro)
                        nova_foto.image.save(nome_galeria, img_galeria, save=True)

                self.stdout.write(self.style.SUCCESS("--> Galeria de fotos adicionada!"))
                time.sleep(1)  # Pausa de segurança

        self.stdout.write(self.style.SUCCESS("\n✅ SEGUNDA FROTA IMPORTADA! O Catálogo está gigante."))