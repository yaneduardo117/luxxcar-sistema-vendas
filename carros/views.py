from django.shortcuts import render, get_object_or_404, redirect
from .models import Car, CarImage, Sale, Notification
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from .forms import CarForm, CadastroUsuarioForm
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q, Sum
from django.db import transaction
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

def home(request):
    carros_disponiveis = Car.objects.filter(status='AVAILABLE').order_by('-created_at')

    # Captura os 3 possíveis filtros
    query = request.GET.get('q', '')
    body_type = request.GET.get('body_type', 'Todos')
    segment = request.GET.get('segment', 'Todos')

    # Filtro da barra de pesquisa (Marca ou Modelo)
    if query:
        carros_disponiveis = carros_disponiveis.filter(
            Q(brand__name__icontains=query) |
            Q(model_name__icontains=query)
        )

    # Filtro de Carroceria Exata
    if body_type and body_type != 'Todos':
        carros_disponiveis = carros_disponiveis.filter(body_type=body_type)

    # Filtro de Segmento Exato
    if segment and segment != 'Todos':
        carros_disponiveis = carros_disponiveis.filter(segment=segment)

    # Apenas os 6 primeiros na Home
    carros_vitrine = carros_disponiveis[:6]

    # Passa as choices do Model pro front-end criar os dropdowns dinamicamente
    context = {
        'cars': carros_vitrine,
        'query': query,
        'active_body': body_type,
        'active_segment': segment,
        'body_types': Car.BODY_TYPE_CHOICES,
        'segments': Car.SEGMENT_CHOICES,
    }
    return render(request, 'home.html', context)


@staff_member_required
def dashboard(request):
    todos_carros = Car.objects.all().order_by('-created_at')

    # Métricas de Estoque
    total_carros = todos_carros.count()
    carros_disponiveis = todos_carros.filter(status='AVAILABLE').count()
    total_reservados = todos_carros.filter(status='RESERVED').count()
    total_vendidos = todos_carros.filter(status='SOLD').count()

    # Métricas Financeiras
    receita_total = Sale.objects.filter(status='APPROVED').aggregate(Sum('sale_price'))['sale_price__sum'] or 0
    receita_pendente = Sale.objects.filter(status='PENDING').aggregate(Sum('sale_price'))['sale_price__sum'] or 0

    # Listas para a interface
    vendas_recentes = Sale.objects.all().order_by('-created_at')[:5]
    notificacoes_nao_lidas = Notification.objects.filter(is_read=False).count()

    form = CarForm()

    context = {
        'cars': todos_carros,
        'total_carros': total_carros,
        'carros_disponiveis': carros_disponiveis,
        'total_reservados': total_reservados,
        'total_vendidos': total_vendidos,
        'receita_total': receita_total,
        'receita_pendente': receita_pendente,
        'vendas_recentes': vendas_recentes,
        'notificacoes_nao_lidas': notificacoes_nao_lidas,
        'form': form,
    }
    return render(request, 'dashboard.html', context)

@staff_member_required
@require_http_methods(["POST"])
def criar_carro(request):
    form = CarForm(request.POST, request.FILES)
    if form.is_valid():
        carro = form.save()

        # Salvando as múltiplas fotos!
        fotos_extras = request.FILES.getlist('galeria')
        for foto in fotos_extras:
            CarImage.objects.create(car=carro, image=foto)

        response = HttpResponse()
        response['HX-Refresh'] = 'true'
        return response
    else:
        # Se der erro, formata os erros bonitinhos para mostrar no Modal
        erros_html = "<div class='bg-red-900/40 border border-red-500 text-red-200 p-4 rounded-lg text-sm mb-4'>"
        erros_html += "<p class='font-bold mb-2'>Verifique os seguintes erros:</p><ul class='list-disc pl-5 space-y-1'>"
        for campo, lista_erros in form.errors.items():
            erros_html += f"<li><strong>{campo}:</strong> {lista_erros[0]}</li>"
        erros_html += "</ul></div>"

        # Retorna status 200 pro HTMX poder injetar o erro na tela!
        return HttpResponse(erros_html, status=200)


@staff_member_required
@require_http_methods(["DELETE"])  # Só aceita requisições do tipo DELETE
def deletar_carro(request, carro_id):
    # Busca o carro pelo ID ou retorna erro 404 se não achar
    carro = get_object_or_404(Car, id=carro_id)
    carro.delete()

    # Retorna uma resposta HTTP vazia.
    # O HTMX vai pegar isso e remover a linha da tabela do HTML
    return HttpResponse("")


@staff_member_required
def editar_carro(request, carro_id):
    # Busca o carro no banco de dados
    carro = get_object_or_404(Car, id=carro_id)

    if request.method == 'POST':
        form = CarForm(request.POST, request.FILES, instance=carro)
        if form.is_valid():
            carro_salvo = form.save()
            fotos_extras = request.FILES.getlist('galeria')
            # Só mexe na galeria se o usuário tiver selecionado arquivos novos
            if fotos_extras:
                # 1. Apaga as fotos antigas para não acumular lixo no banco
                carro_salvo.galeria.all().delete()

                # 2. Salva as novas fotos na tabela CarImage
                for foto in fotos_extras:
                    CarImage.objects.create(car=carro_salvo, image=foto)

            # Dá um refresh suave na página para atualizar a tabela
            response = HttpResponse()
            response['HX-Refresh'] = 'true'
            return response
    else:
        # Se for GET, cria o formulário preenchido
        form = CarForm(instance=carro)

    # Retorna APENAS o HTML do modal de edição
    return render(request, 'modal_edicao.html', {'form': form, 'car': carro})

def cadastro(request):
    if request.method == 'POST':
        form = CadastroUsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CadastroUsuarioForm()

    return render(request, 'registration/cadastro.html', {'form': form})


def carro_detalhes(request, id):
    # Busca o carro pelo ID, se não achar, dá erro 404 (Página não encontrada)
    carro = get_object_or_404(Car, id=id)

    # O Django já manda as fotos da galeria junto automaticamente através do 'carro.galeria.all'
    return render(request, 'carro_detalhes.html', {'car': carro})


# ==========================================
# FLUXO DE CHECKOUT E VENDAS
# ==========================================
@login_required(login_url='login')
def checkout_prep(request, car_id):
    carro = get_object_or_404(Car, id=car_id)

    # Se já foi vendido ou reservado, bloqueia
    if carro.status != 'AVAILABLE':
        return render(request, 'erro_amigavel.html', {'mensagem': 'Este veículo já foi reservado ou vendido.'})

    if request.method == 'POST':
        # Captura os dados e salva na sessão temporariamente
        request.session[f'checkout_{car_id}'] = {
            'nome': request.POST.get('nome'),
            'telefone': request.POST.get('telefone'),
            'email': request.POST.get('email'),
            'pagamento': request.POST.get('pagamento', 'TED')
        }

    # Busca os dados da sessão para mostrar na tela de revisão
    dados_cliente = request.session.get(f'checkout_{car_id}')
    if not dados_cliente:
        return redirect('carro_detalhes', id=car_id)

    return render(request, 'checkout.html', {'car': carro, 'cliente': dados_cliente})

@login_required(login_url='login')
@transaction.atomic  # Garante que ou tudo salva, ou nada salva
def checkout_confirm(request, car_id):
    if request.method == 'POST':
        # SELECT FOR UPDATE: Tranca esta linha no banco de dados.
        # Ninguém mais consegue comprar enquanto essa função não terminar
        carro = get_object_or_404(Car.objects.select_for_update(), id=car_id)

        if carro.status != 'AVAILABLE':
            return render(request, 'erro_amigavel.html',
                          {'mensagem': 'Infelizmente alguém comprou este veículo milissegundos antes de você.'})

        # TRAVA: Impede múltiplos pedidos pendentes para o mesmo carro
        if Sale.objects.filter(car=carro, status='PENDING').exists():
            return render(request, 'erro_amigavel.html',
                          {'mensagem': 'Este veículo já possui uma reserva em andamento por outro cliente.'})

        dados_cliente = request.session.get(f'checkout_{car_id}')
        if not dados_cliente:
            return redirect('carro_detalhes', id=car_id)

        # 1. Cria a Venda
        nova_venda = Sale.objects.create(
            car=carro,
            customer_name=dados_cliente['nome'],
            customer_email=dados_cliente['email'],
            customer_phone=dados_cliente['telefone'],
            payment_method=dados_cliente['pagamento'],
            sale_price=carro.price,
            status='PENDING'
        )

        # 2. Muda o status do carro
        carro.status = 'RESERVED'
        carro.save()

        # 3. Cria a Notificação para o Admin
        Notification.objects.create(
            message=f"Nova reserva: {carro.brand.name} {carro.model_name} (R$ {carro.price})",
            notification_type='SALE',
            url=f"/dashboard/sales/{nova_venda.id}/"
        )

        # 4. Limpa a sessão
        del request.session[f'checkout_{car_id}']

        return redirect('compra_sucesso', sale_id=nova_venda.id)

    return redirect('home')

@login_required(login_url='login')
def compra_sucesso(request, sale_id):
    venda = get_object_or_404(Sale, id=sale_id)
    return render(request, 'sucesso.html', {'venda': venda})

# ==========================================
# GESTÃO DE PEDIDOS E NOTIFICAÇÕES (DASHBOARD)
# ==========================================

@staff_member_required
def sale_detail(request, sale_id):
    venda = get_object_or_404(Sale, id=sale_id)
    return render(request, 'sale_detail.html', {'venda': venda})

@staff_member_required
@require_http_methods(["POST"])
def approve_sale(request, sale_id):
    venda = get_object_or_404(Sale, id=sale_id)
    venda.approve() # Chama a regra de negócio blindada no models.py
    response = HttpResponse()
    response['HX-Refresh'] = 'true' # Atualiza a página inteira para recalcular as receitas
    return response

@staff_member_required
@require_http_methods(["POST"])
def cancel_sale(request, sale_id):
    venda = get_object_or_404(Sale, id=sale_id)
    venda.cancel() # Chama a regra de negócio que volta o carro pro estoque
    response = HttpResponse()
    response['HX-Refresh'] = 'true'
    return response

@staff_member_required
def notifications_dropdown(request):
    notificacoes = Notification.objects.all()[:10]
    return render(request, 'partials/notification_list.html', {'notificacoes': notificacoes})

@staff_member_required
@require_http_methods(["POST"])
def mark_all_read(request):
    Notification.objects.filter(is_read=False).update(is_read=True)
    return HttpResponse("") # HTMX vai apagar a bolinha vermelha e atualizar a lista


# ==========================================
# CATÁLOGO DE VEÍCULOS (PAGINADO)
# ==========================================
def catalogo_veiculos(request):
    carros_disponiveis = Car.objects.filter(status='AVAILABLE').order_by('-created_at')

    # Captura os filtros
    query = request.GET.get('q', '')
    body_type = request.GET.get('body_type', 'Todos')
    segment = request.GET.get('segment', 'Todos')

    if query:
        carros_disponiveis = carros_disponiveis.filter(
            Q(brand__name__icontains=query) | Q(model_name__icontains=query)
        )
    if body_type and body_type != 'Todos':
        carros_disponiveis = carros_disponiveis.filter(body_type=body_type)
    if segment and segment != 'Todos':
        carros_disponiveis = carros_disponiveis.filter(segment=segment)

    # PAGINAÇÃO: Exibe 9 carros por vez
    paginator = Paginator(carros_disponiveis, 9)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj, # Envia o page_obj ao invés da lista completa
        'query': query,
        'active_body': body_type,
        'active_segment': segment,
        'body_types': Car.BODY_TYPE_CHOICES,
        'segments': Car.SEGMENT_CHOICES,
    }

    # SE A REQUISIÇÃO VIER DO HTMX (Botão Carregar Mais ou Filtros)
    if request.headers.get('HX-Request'):
        return render(request, 'partials/car_grid.html', context)

    # SE FOR O ACESSO NORMAL (Digitando a URL)
    return render(request, 'catalogo.html', context)

# ==========================================
# PÁGINAS INSTITUCIONAIS
# ==========================================

def sobre(request):
    return render(request, 'sobre.html')

def contato(request):
    return render(request, 'contato.html')