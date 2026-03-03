from django.contrib import admin
from django.contrib import messages
from .models import Brand, Car, CarImage, Sale, Notification

# ==========================================
# 1. PERSONALIZAÇÃO VISUAL DO PAINEL
# ==========================================
admin.site.site_header = "LuxxCar | Gestão Premium"
admin.site.site_title = "Admin LuxxCar"
admin.site.index_title = "Painel de Controle Executivo"


# ==========================================
# 2. CONFIGURAÇÃO DE MARCAS E FOTOS
# ==========================================
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


# Isso permite adicionar as fotos da galeria DE DENTRO da página de criar o carro no Admin
class CarImageInline(admin.TabularInline):
    model = CarImage
    extra = 1


# ==========================================
# 3. CONFIGURAÇÃO DO ESTOQUE (CARROS)
# ==========================================
@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    # Colunas que aparecem na tabela
    list_display = ('brand', 'model_name', 'year', 'price_format', 'status', 'body_type')
    # Filtros laterais mágicos
    list_filter = ('status', 'brand', 'body_type', 'segment', 'year')
    # Barra de pesquisa
    search_fields = ('model_name', 'brand__name')
    inlines = [CarImageInline]

    # Formata o preço para ficar bonito na tabela
    def price_format(self, obj):
        return f"R$ {obj.price:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

    price_format.short_description = 'Preço de Venda'


# ==========================================
# 4. CONFIGURAÇÃO DE VENDAS (O CORAÇÃO DO SISTEMA)
# ==========================================
@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('id', 'car', 'customer_name', 'sale_price_format', 'status', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('customer_name', 'customer_email', 'car__model_name')
    readonly_fields = ('created_at',)

    # AÇÕES CUSTOMIZADAS NO ADMIN (Aparecem no dropdown superior)
    actions = ['action_approve_sales', 'action_cancel_sales']

    def sale_price_format(self, obj):
        return f"R$ {obj.sale_price:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

    sale_price_format.short_description = 'Valor Fechado'

    @admin.action(description='Aprovar pedidos selecionados')
    def action_approve_sales(self, request, queryset):
        aprovados = 0
        for sale in queryset:
            if sale.approve():  # Usa aquela nossa função segura que atualiza o carro junto!
                aprovados += 1
        self.message_user(request, f"{aprovados} pedidos foram aprovados com sucesso.", messages.SUCCESS)

    @admin.action(description='Cancelar pedidos selecionados')
    def action_cancel_sales(self, request, queryset):
        cancelados = 0
        for sale in queryset:
            if sale.cancel():  # Usa a função que devolve o carro pro estoque!
                cancelados += 1
        self.message_user(request, f"{cancelados} pedidos foram cancelados e os veículos voltaram ao estoque.",
                          messages.WARNING)


# ==========================================
# 5. CONFIGURAÇÃO DE NOTIFICAÇÕES
# ==========================================
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('message', 'notification_type', 'is_read', 'created_at')
    list_filter = ('is_read', 'notification_type')

    actions = ['action_mark_as_read']

    @admin.action(description='Marcar notificações como lidas')
    def action_mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
        self.message_user(request, "Notificações atualizadas.", messages.SUCCESS)