from django.shortcuts import render, redirect, get_object_or_404
from .forms import MateriaPrimaForm, CompraMateriaPrimaForm
from .models import CompraMateriaPrima, Estoque, Produto, Venda, Despesa, CustoFixo, MaterialUsado
from .forms import ProdutoForm, MaterialUsadoForm, CustoFixoForm
from django.forms import modelformset_factory
from django.contrib import messages
from django.http import JsonResponse, HttpResponseBadRequest
from decimal import Decimal
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.views.decorators.http import require_POST
import json


# Create your views here.
def index(request):
    return render(request, 'index.html')

def registradora(request):
    form_mp = MateriaPrimaForm(request.POST or None)
    form_compra = CompraMateriaPrimaForm(request.POST or None)

    if request.method == 'POST':
        if 'salvar_materia' in request.POST and form_mp.is_valid():
            form_mp.save()
            return redirect('registradora')

        elif 'salvar_compra' in request.POST and form_compra.is_valid():
            form_compra.save()
            return redirect('registradora')

    return render(request, 'registradora.html', {
        'form_mp': form_mp,
        'form_compra': form_compra
    })


def cadastrar_produto(request):
    """
    View para cadastro completo de produtos
    """

    # Cria o formset para MaterialUsado
    MaterialFormSet = modelformset_factory(
        MaterialUsado,
        form=MaterialUsadoForm,
        extra=1,
        can_delete=True
    )

    # 🔹 Busca o último custo fixo salvo
    ultimo_custo_fixo = CustoFixo.objects.last()

    # Inicializa os formulários
    produto_form = ProdutoForm(request.POST or None)
    custo_fixo_form = CustoFixoForm(request.POST or None, instance=ultimo_custo_fixo)
    formset = MaterialFormSet(
        request.POST or None,
        queryset=MaterialUsado.objects.none()
    )

    # Processa o POST
    if request.method == 'POST':
        print("\n" + "=" * 60)
        print("📥 POST RECEBIDO - CADASTRO DE PRODUTO")
        print("=" * 60)

        # Valida os formulários
        produto_valido = produto_form.is_valid()
        formset_valido = formset.is_valid()
        custo_fixo_valido = custo_fixo_form.is_valid()

        print(f"✓ Produto válido: {produto_valido}")
        print(f"✓ Materiais válido: {formset_valido}")
        print(f"✓ Custos fixos válido: {custo_fixo_valido}")

        # Exibe erros
        if not produto_valido:
            print("❌ Erros do produto:", produto_form.errors)
        if not formset_valido:
            print("❌ Erros dos materiais:", formset.errors)
        if not custo_fixo_valido:
            print("❌ Erros dos custos fixos:", custo_fixo_form.errors)

        # Se tudo válido, salva
        if produto_valido and formset_valido and custo_fixo_valido:
            try:
                # 1. Salva o custo fixo (atualiza se já existir)
                custo_fixo = custo_fixo_form.save()
                print(f"💰 Custo fixo salvo: R$ {custo_fixo.custo_fixo_total:.2f}")

                # 2. Salva o produto
                produto = produto_form.save(commit=False)
                produto.custo_fixo_total = custo_fixo.custo_fixo_total
                produto.save()
                print(f"📦 Produto salvo: {produto.nome}")

                # 3. Salva os materiais usados
                materiais_salvos = 0
                for form in formset:
                    if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                        material = form.save(commit=False)
                        material.produto = produto
                        material.save()
                        materiais_salvos += 1

                        print(f"   🎨 Material: {material.compra_materia_prima.materia_prima.nome}")
                        print(f"      Quantidade: {material.qtd_material_usado} {material.get_tipo_unidade_display()}")
                        print(f"      Valor unitário: R$ {material.valor_unitario:.4f}")
                        print(f"      Valor total: R$ {material.valor_total:.2f}")

                print(f"✅ {materiais_salvos} materiais salvos")

                # 4. Cria ou atualiza o estoque
                estoque, criado = Estoque.objects.get_or_create(
                    produto=produto,
                    defaults={'quantidade_produto': produto.quantidade_em_estoque}
                )

                if not criado:
                    estoque.quantidade_produto = produto.quantidade_em_estoque
                    estoque.save()

                estoque.atualizar_valores()
                print(f"📊 Estoque {'criado' if criado else 'atualizado'}")

                # Resumo final
                print("\n" + "-" * 60)
                print(f"💵 RESUMO DO PRODUTO")
                print(f"   Nome: {produto.nome}")
                print(f"   Custo materiais: R$ {sum([m.valor_total for m in produto.materiais_usados.all()]):.2f}")
                print(f"   Custos fixos: R$ {produto.custo_fixo_total:.2f}")
                print(f"   Custo total: R$ {produto.custo_total:.2f}")
                print(f"   Valor de venda: R$ {produto.valor_venda:.2f}")
                print(f"   Lucro: R$ {produto.lucro_por_venda:.2f}")
                print("-" * 60)

                messages.success(
                    request,
                    f'✅ Produto "{produto.nome}" cadastrado com sucesso!'
                )

                print("=" * 60)
                print("✅ CADASTRO CONCLUÍDO COM SUCESSO")
                print("=" * 60 + "\n")

                # 🔹 Redireciona, mas mantém o último custo fixo (pois foi salvo)
                return redirect('cadastrar_produto')

            except Exception as e:
                print(f"\n❌ ERRO ao salvar: {e}")
                import traceback
                traceback.print_exc()

                messages.error(
                    request,
                    f'❌ Erro ao cadastrar produto: {str(e)}'
                )

    # ========== PREPARA DADOS DOS MATERIAIS ==========
    materiais_data = {}

    try:
        compras = CompraMateriaPrima.objects.select_related('materia_prima').all()

        for compra in compras:
            valor_por_cm = float(compra.valor_por_cm or Decimal('0'))
            valor_por_quantidade = float(compra.valor_por_quantidade or Decimal('0'))

            materiais_data[str(compra.id)] = {
                'nome': f"{compra.materia_prima.nome} - {compra.marca}",
                'unidade_padrao': compra.unidade,
                'valor_por_cm': valor_por_cm,
                'valor_por_quantidade': valor_por_quantidade
            }

        print(f"📦 {len(materiais_data)} materiais disponíveis para seleção")

    except Exception as e:
        print(f"❌ Erro ao carregar materiais: {e}")
        materiais_data = {}

    # Contexto para o template
    context = {
        'produto_form': produto_form,
        'formset': formset,
        'custo_fixo_form': custo_fixo_form,
        'materiais_data_json': json.dumps(materiais_data),
    }

    return render(request, 'cadastrar_produto.html', context)


def estoque(request):
    # atualiza caches/valores
    estoques = Estoque.objects.select_related('produto').all()
    for e in estoques:
        e.atualizar_valores()
    return render(request, 'estoque.html', {'estoques': estoques})


def financeiro(request):
    vendas = Venda.objects.all()
    despesas = Despesa.objects.all()
    produtos = Produto.objects.all()
    custo_fixo = CustoFixo.objects.last()
    context = {
        'vendas': vendas,
        'despesas': despesas,
        'produtos': produtos,
        'custo_fixo': custo_fixo,
    }
    return render(request, 'financeiro.html', context)


@require_POST
def api_update_estoque(request):
    """
    Recebe JSON: { "estoque_id": int, "quantidade_produto": int (opcional), "valor_produto": "12.50" (opcional) }
    Retorna JSON com novo estado.
    """
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except Exception:
        return HttpResponseBadRequest("JSON inválido")

    estoque_id = payload.get('estoque_id')
    if not estoque_id:
        return HttpResponseBadRequest("estoque_id required")

    estoque = get_object_or_404(Estoque, id=estoque_id)

    if 'quantidade_produto' in payload:
        try:
            estoque.quantidade_produto = int(payload['quantidade_produto'])
        except Exception:
            pass

    if 'valor_produto' in payload:
        try:
            estoque.valor_produto = Decimal(str(payload['valor_produto']))
        except Exception:
            pass

    estoque.atualizar_valores()
    return JsonResponse({
        'ok': True,
        'estoque_id': estoque.id,
        'quantidade_produto': estoque.quantidade_produto,
        'valor_produto': str(estoque.valor_produto),
        'produto_total': str(estoque.produto_total),
        'materia_prima_total': str(estoque.materia_prima_total),
    })


@require_POST
def api_create_venda(request):
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except Exception:
        return HttpResponseBadRequest("JSON inválido")

    produto_id = payload.get('produto_id')
    quantidade = int(payload.get('quantidade', 1))
    valor_unitario = Decimal(str(payload.get('valor_unitario', '0')))

    produto = get_object_or_404(Produto, id=produto_id)
    venda = Venda(produto=produto, quantidade=quantidade, valor_unitario=valor_unitario)
    venda.save()
    return JsonResponse({'ok': True, 'venda_id': venda.id})


@require_POST
def api_create_despesa(request):
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except Exception:
        return HttpResponseBadRequest("JSON inválido")
    descricao = payload.get('descricao', 'Despesa')
    categoria = payload.get('categoria', 'OUTROS')
    valor = Decimal(str(payload.get('valor', '0')))
    data = payload.get('data')
    despesa = Despesa(descricao=descricao, categoria=categoria, valor=valor)
    if data:
        from django.utils.dateparse import parse_date
        parsed = parse_date(data)
        if parsed:
            despesa.data = parsed
    despesa.save()
    return JsonResponse({'ok': True, 'despesa_id': despesa.id})


def autocomplete_marcas(request):
    """Retorna lista de marcas únicas já registradas"""
    query = request.GET.get('q', '').lower()
    marcas = CompraMateriaPrima.objects.values_list('marca', flat=True).distinct()
    marcas_filtradas = [m for m in marcas if m and query in m.lower()]
    return JsonResponse(list(marcas_filtradas), safe=False)


def autocomplete_fornecedores(request):
    """Retorna lista de fornecedores únicos já registrados"""
    query = request.GET.get('q', '').lower()
    fornecedores = CompraMateriaPrima.objects.values_list('fornecedor', flat=True).distinct()
    fornecedores_filtrados = [f for f in fornecedores if f and query in f.lower()]
    return JsonResponse(list(fornecedores_filtrados), safe=False)

def api_financeiro_resumo(request):
    """Retorna resumo financeiro (últimos 12 meses)"""
    vendas = Venda.objects.all().order_by('data_venda')
    despesas = Despesa.objects.all().order_by('data')
    custo_fixo = CustoFixo.objects.last()

    vendas_por_mes = {}
    for v in vendas:
        mes = v.data_venda.strftime("%Y-%m")
        vendas_por_mes.setdefault(mes, Decimal(0))
        vendas_por_mes[mes] += v.valor_total

    despesas_por_mes = {}
    for d in despesas:
        mes = d.data.strftime("%Y-%m")
        despesas_por_mes.setdefault(mes, Decimal(0))
        despesas_por_mes[mes] += d.valor

    return JsonResponse({
        "vendas": [{"mes": k, "valor": float(v)} for k, v in vendas_por_mes.items()],
        "despesas": [{"mes": k, "valor": float(v)} for k, v in despesas_por_mes.items()],
        "custo_fixo": float(custo_fixo.custo_fixo_total) if custo_fixo else 0,
    })


@csrf_exempt
def api_registrar_venda(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        produto_id = data.get('produto_id')
        quantidade = int(data.get('quantidade', 1))
        valor_unitario = Decimal(str(data.get('valor_unitario', 0)))

        produto = Produto.objects.get(id=produto_id)
        venda = Venda.objects.create(
            produto=produto,
            quantidade=quantidade,
            valor_unitario=valor_unitario,
            data_venda=timezone.now(),
        )
        return JsonResponse({"status": "ok", "venda_id": venda.id})
    return JsonResponse({"error": "Método não permitido"}, status=405)


@csrf_exempt
def api_registrar_despesa(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        descricao = data.get('descricao')
        categoria = data.get('categoria', 'OUTROS')
        valor = Decimal(str(data.get('valor', 0)))
        Despesa.objects.create(
            descricao=descricao,
            categoria=categoria,
            valor=valor,
            data=timezone.now()
        )
        return JsonResponse({"status": "ok"})
    return JsonResponse({"error": "Método não permitido"}, status=405)