from .models import (Produto, Estoque, MateriaPrima,
                     MaterialUsado, CompraMateriaPrima, CustoFixo,
                     LancamentoFinanceiro, Venda, ItemVenda, CustoFixoMensal)
from .forms import (MateriaPrimaForm, CompraMateriaPrimaForm, ProdutoForm,
                    MaterialUsadoForm, CustoFixoForm, CustoMensalForm)
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from django.views.decorators.csrf import csrf_exempt
from django.db.models.functions import TruncDay
from django.shortcuts import render, redirect
from django.forms import modelformset_factory
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from decimal import Decimal
import json


# Create your views here.
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

    # Prepara o contexto base, incluindo dados do POST para manter os campos preenchidos em caso de erro
    context = {
        'produto_form': produto_form,
        'formset': formset,
        'custo_fixo_form': custo_fixo_form,
        'materiais_data_json': json.dumps({}),  # Será preenchido abaixo ou no final
    }

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

        # Se tudo válido, executa a verificação e o salvamento
        if produto_valido and formset_valido and custo_fixo_valido:

            # Obtém os dados dos formulários
            produto_data = produto_form.cleaned_data

            # A quantidade de produtos que o usuário está cadastrando no estoque
            quantidade_de_produtos = produto_data.get('quantidade_em_estoque', 0)

            # =========================================================
            # 🎯 NOVO PASSO: VERIFICAÇÃO DE ESTOQUE INSUFICIENTE
            # =========================================================
            estoque_suficiente = True

            # Loop sobre os materiais para verificar a demanda total
            for form in formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    material_data = form.cleaned_data

                    compra = material_data.get('compra_materia_prima')
                    qtd_material_por_produto = material_data.get('qtd_material_usado')  # Qtd. por UM produto
                    tipo_unidade = material_data.get('tipo_unidade')

                    if compra and qtd_material_por_produto and quantidade_de_produtos:

                        # Calcula a demanda TOTAL para o lote de produtos
                        demanda_total = qtd_material_por_produto * Decimal(quantidade_de_produtos)

                        estoque_atual = Decimal(0)

                        # Identifica o campo de estoque e o valor atual
                        if tipo_unidade == 'CM':
                            estoque_atual = compra.unidade_em_cm or Decimal(0)
                            unidade_str = "CM"
                        else:  # QUANTIDADE
                            estoque_atual = compra.unidade_em_quantidade or Decimal(0)
                            unidade_str = "UNIDADES"

                        # Verifica se o estoque é suficiente
                        if demanda_total > estoque_atual:
                            estoque_suficiente = False

                            # Mensagem de erro detalhada
                            messages.error(
                                request,
                                f'❌ ESTOQUE INSUFICIENTE: Você precisa de {demanda_total:.2f} {unidade_str} de "{compra.materia_prima.nome}", mas só há {estoque_atual:.2f} {unidade_str} em estoque.'
                            )
                            break  # Interrompe o loop

            # Trava o cadastro se o estoque for insuficiente
            if not estoque_suficiente:
                print("❌ CADASTRO BLOQUEADO: Estoque insuficiente.")

                # Para manter a view funcional e retornar o JSON dos materiais em caso de erro
                # O código de preparo do JSON é movido para dentro do if/else
                pass  # Prossegue para o bloco try/except ou para o render final

            # =========================================================
            # 🎯 FIM DA VERIFICAÇÃO DE ESTOQUE
            # =========================================================

            # Se a verificação de estoque passou, tenta salvar
            if estoque_suficiente:
                try:
                    # 1. Salva o custo fixo (atualiza se já existir)
                    custo_fixo = custo_fixo_form.save()
                    print(f"💰 Custo fixo salvo: R$ {custo_fixo.custo_fixo_total:.2f}")

                    # 2. Salva o produto
                    produto = produto_form.save(commit=False)
                    produto.custo_fixo_total = custo_fixo.custo_fixo_total
                    produto.save()
                    print(f"📦 Produto salvo: {produto.nome}")

                    # 3. Salva os materiais usados E SUBTRAI A DEMANDA TOTAL DO ESTOQUE
                    materiais_salvos = 0
                    for form in formset:
                        if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                            material = form.save(commit=False)
                            material.produto = produto
                            material.save()
                            materiais_salvos += 1

                            # --- Lógica de Subtração (Usando demanda_total) ---
                            compra = material.compra_materia_prima
                            quantidade_usada_por_produto = material.qtd_material_usado

                            # Recalcula a demanda total (a mesma usada na verificação)
                            demanda_total = quantidade_usada_por_produto * Decimal(quantidade_de_produtos)

                            print(
                                f"   📉 Estoque de compra #{compra.id} antes: CM={compra.unidade_em_cm}, QTD={compra.unidade_em_quantidade}")

                            if material.tipo_unidade == 'CM':
                                compra.unidade_em_cm = F('unidade_em_cm') - demanda_total
                                print(
                                    f"   ➖ Subtraindo {demanda_total:.2f} CM (Total para {quantidade_de_produtos} produtos)")
                            else:  # QUANTIDADE
                                compra.unidade_em_quantidade = F('unidade_em_quantidade') - demanda_total
                                print(
                                    f"   ➖ Subtraindo {demanda_total:.2f} UNIDADES (Total para {quantidade_de_produtos} produtos)")

                            compra.save()
                            compra.refresh_from_db()
                            print(
                                f"   ✅ Estoque de compra #{compra.id} atualizado: CM={compra.unidade_em_cm}, QTD={compra.unidade_em_quantidade}")
                            # ----------------------------------------------------

                            print(f"   🎨 Material: {material.compra_materia_prima.materia_prima.nome}")
                            print(
                                f"      Quantidade: {material.qtd_material_usado} {material.get_tipo_unidade_display()}")
                            print(f"      Valor unitário: R$ {material.valor_unitario:.4f}")
                            print(f"      Valor total: R$ {material.valor_total:.2f}")

                    print(f"✅ {materiais_salvos} materiais salvos e estoque atualizado")

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
            # Se o estoque não era suficiente, o código continua para o render abaixo.

    # ========== PREPARA DADOS DOS MATERIAIS PARA O JAVASCRIPT ==========
    materiais_data = {}

    try:
        # Garante que os dados sejam carregados, mesmo após um erro de POST,
        # para que o JS possa recalcular e manter os valores na tela.
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
        print(f"❌ Erro ao carregar materiais para JS: {e}")
        materiais_data = {}

    # Atualiza o contexto com os dados dos materiais
    context['materiais_data_json'] = json.dumps(materiais_data)

    return render(request, 'cadastrar_produto.html', context)


def estoque(request):
    produtos = Produto.objects.all().order_by('nome')
    materias = MateriaPrima.objects.all().order_by('nome')

    # Cálculos dos totais
    valor_total_produtos = sum([(p.custo_total or Decimal(0)) * (p.quantidade_em_estoque or 0) for p in produtos])

    valor_total_materias = Decimal(0)
    for m in materias:
        last_compra = m.compras.last()
        if last_compra and last_compra.preco:
            valor_total_materias += last_compra.preco

    context = {
        'produtos': produtos,
        'materias': materias,
        'valor_total_produtos': f"{valor_total_produtos:.2f}",
        'valor_total_materias': f"{valor_total_materias:.2f}",
    }
    return render(request, 'estoque.html', context)


# API PARA PRODUTOS
@csrf_exempt
def api_produto_detalhe(request, id):
    try:
        produto = Produto.objects.get(id=id)

        valor_total = float(produto.custo_total or 0) * float(produto.quantidade_em_estoque or 0)

        return JsonResponse({
            'id': produto.id,
            'nome': produto.nome,
            'categoria': produto.categoria,
            'quantidade_em_estoque': produto.quantidade_em_estoque,
            'valor_venda': float(produto.valor_venda) if produto.valor_venda else None,
            'custo_total': float(produto.custo_total) if produto.custo_total else 0,
            'valor_total': valor_total
        })

    except Produto.DoesNotExist:
        return JsonResponse({'error': 'Produto não encontrado'}, status=404)


@csrf_exempt
def api_produto_editar(request, id):
    if request.method == 'POST':
        try:
            produto = Produto.objects.get(id=id)
            data = json.loads(request.body)

            produto.nome = data.get('nome', produto.nome)
            produto.categoria = data.get('categoria', produto.categoria)
            produto.quantidade_em_estoque = data.get('quantidade_em_estoque', produto.quantidade_em_estoque)
            produto.valor_venda = data.get('valor_venda', produto.valor_venda)
            produto.save()

            return JsonResponse({'success': True})
        except Produto.DoesNotExist:
            return JsonResponse({'error': 'Produto não encontrado'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
def api_produto_excluir(request, id):
    if request.method == 'DELETE':
        try:
            produto = Produto.objects.get(id=id)
            produto.delete()
            return JsonResponse({'success': True})
        except Produto.DoesNotExist:
            return JsonResponse({'error': 'Produto não encontrado'}, status=404)


# API PARA MATÉRIAS-PRIMAS
@csrf_exempt
def api_materia_detalhe(request, id):
    try:
        materia = MateriaPrima.objects.get(id=id)
        compra = materia.compras.last()

        compra_data = None
        if compra:
            compra_data = {
                'id': compra.id,
                'preco': float(compra.preco) if compra.preco else 0,
                'fornecedor': compra.fornecedor or "",
                'unidade': compra.unidade,
                'quantidade': (
                    float(compra.unidade_em_cm)
                    if compra.unidade == 'CM'
                    else float(compra.unidade_em_quantidade)
                ),
                'sufixo': 'cm' if compra.unidade == 'CM' else 'un'
            }

        return JsonResponse({
            'id': materia.id,
            'nome': materia.nome,
            'categoria': materia.categoria,
            'especificacao': materia.especificacao,
            'cor': materia.cor or "",
            'compra': compra_data
        })

    except MateriaPrima.DoesNotExist:
        return JsonResponse({'error': 'Matéria-prima não encontrada'}, status=404)

    except Exception as e:
        print("ERRO API MATERIA DETALHE:", e)
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def api_materia_editar(request, id):
    if request.method == 'POST':
        try:
            materia = MateriaPrima.objects.get(id=id)
            data = json.loads(request.body)

            materia.nome = data.get('nome', materia.nome)
            materia.categoria = data.get('categoria', materia.categoria)
            materia.especificacao = data.get('especificacao', materia.especificacao)
            materia.cor = data.get('cor', materia.cor)
            materia.save()

            return JsonResponse({'success': True})
        except MateriaPrima.DoesNotExist:
            return JsonResponse({'error': 'Matéria-prima não encontrada'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
def api_materia_excluir(request, id):
    if request.method == 'DELETE':
        try:
            materia = MateriaPrima.objects.get(id=id)
            materia.delete()
            return JsonResponse({'success': True})
        except MateriaPrima.DoesNotExist:
            return JsonResponse({'error': 'Matéria-prima não encontrada'}, status=404)



def vendas(request):
    """
    Renderiza a tela de PDV (Ponto de Venda)
    """
    produtos = Produto.objects.filter(quantidade_em_estoque__gt=0).order_by('nome')
    return render(request, 'vendas.html', {'produtos': produtos})


@csrf_exempt
def api_salvar_venda(request):
    """
    API que recebe o JSON do carrinho e processa a venda completa
    """
    if request.method == 'POST':
        try:
            dados = json.loads(request.body)
            itens_carrinho = dados.get('itens', [])
            metodo_pagamento = dados.get('metodo_pagamento')
            cliente_nome = dados.get('cliente_nome', 'Cliente Balcão')
            total_venda = Decimal(dados.get('total_venda'))

            if not itens_carrinho:
                return JsonResponse({'success': False, 'error': 'Carrinho vazio.'})

            # Inicia uma transação atômica (segurança de dados)
            with transaction.atomic():
                # 1. Criar a Venda (Cabeçalho)
                nova_venda = Venda.objects.create(
                    valor_total=total_venda,
                    metodo_pagamento=metodo_pagamento,
                    cliente_nome=cliente_nome
                )

                # 2. Processar Itens e Baixar Estoque
                for item in itens_carrinho:
                    produto = Produto.objects.select_for_update().get(id=item['id'])

                    # Verificação de estoque extra
                    if produto.quantidade_em_estoque < int(item['quantidade']):
                        raise Exception(f"Estoque insuficiente para {produto.nome}")

                    # Cria o item da venda
                    ItemVenda.objects.create(
                        venda=nova_venda,
                        produto=produto,
                        quantidade=item['quantidade'],
                        valor_unitario=item['preco'],
                        subtotal=Decimal(item['preco']) * int(item['quantidade'])
                    )

                    # Baixa no estoque
                    produto.quantidade_em_estoque -= int(item['quantidade'])
                    produto.save()

                    # Atualiza valores do modelo Estoque auxiliar se existir
                    if hasattr(produto, 'estoque'):
                        produto.estoque.quantidade_produto = produto.quantidade_em_estoque
                        produto.estoque.atualizar_valores()

                # 3. Criar Lançamento Financeiro (Entrada de Caixa)
                LancamentoFinanceiro.objects.create(
                    tipo='ENTRADA',
                    categoria='VENDA',
                    descricao=f"Venda #{nova_venda.id} - {cliente_nome}",
                    valor=total_venda,
                    venda_origem=nova_venda,
                    data=timezone.now().date()
                )

            return JsonResponse({'success': True, 'venda_id': nova_venda.id})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    return JsonResponse({'success': False, 'error': 'Método não permitido'}, status=405)


def financeiro(request):
    # 1. Filtro de Data (Padrão: Mês atual ou mês selecionado na URL ?mes=1&ano=2025)
    hoje = timezone.now().date()
    mes_url = request.GET.get('mes')
    ano_url = request.GET.get('ano')

    if mes_url and ano_url:
        data_referencia = datetime(int(ano_url), int(mes_url), 1).date()
    else:
        data_referencia = hoje.replace(day=1)

    # Define intervalo do mês
    proximo_mes = (data_referencia + timedelta(days=32)).replace(day=1)
    ultimo_dia_mes = proximo_mes - timedelta(days=1)

    # 2. Processamento do Formulário de Custos
    # Certifique-se que CustoMensalForm está importado e CustoFixoMensal existe
    # Substitua CustoMensalForm pelo nome real do seu formulário
    # Substitua CustoFixoMensal pelo nome real do seu modelo de custos mensais
    try:
        custo_obj, created = CustoFixoMensal.objects.get_or_create(data_referencia=data_referencia)
    except NameError:
        # Fallback se o modelo CustoFixoMensal não estiver definido (apenas para evitar crash no teste)
        return render(request, "financeiro.html", {'error': 'Modelo CustoFixoMensal não definido'})

    # Substitua CustoMensalForm pelo nome real do seu formulário
    form = CustoMensalForm(request.POST or None, instance=custo_obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        # Nota: Corrigido o redirect para 'financeiro/' conforme o erro anterior, se aplicável
        return redirect(f'/templates/financeiro/?mes={data_referencia.month}&ano={data_referencia.year}')

    # === NOVOS FILTROS RECEBIDOS DA URL ===
    filtro_metodo = request.GET.get('metodo')
    filtro_categoria = request.GET.get('categoria')
    filtro_produto_id = request.GET.get('produto_id')

    # Define listas de dados para os filtros no template
    try:
        produtos = Produto.objects.all().order_by('nome')
        metodos_pagamento = Venda.METODOS_PAGAMENTO
        categorias_produto = Produto.CATEGORIAS
    except NameError:
        # Fallback se os modelos não estiverem definidos
        produtos = []
        metodos_pagamento = []
        categorias_produto = []

    # 3. Cálculos de Receita
    vendas_mes = Venda.objects.filter(data_venda__date__range=[data_referencia, ultimo_dia_mes])

    # === APLICAÇÃO DOS FILTROS DE VENDA NAS VENDAS DO MÊS ===
    if filtro_metodo:
        vendas_mes = vendas_mes.filter(metodo_pagamento=filtro_metodo)

    if filtro_categoria:
        # Filtra vendas que contêm pelo menos um item da categoria selecionada
        vendas_mes = vendas_mes.filter(itens__produto__categoria=filtro_categoria).distinct()
    # =======================================================

    # Recalcula KPIs com as vendas filtradas
    faturamento_bruto = vendas_mes.aggregate(Sum('valor_total'))['valor_total__sum'] or Decimal('0.00')
    total_vendas_qtd = vendas_mes.count()

    # 4. CMV (Custo da Mercadoria Vendida - Refiltrar itens vendidos com base nas vendas filtradas)
    itens_vendidos = ItemVenda.objects.filter(venda__in=vendas_mes).annotate(
        custo_total_item=ExpressionWrapper(
            F('custo_unitario_snapshot') * F('quantidade'),
            output_field=DecimalField()
        )
    )
    cmv = itens_vendidos.aggregate(Sum('custo_total_item'))['custo_total_item__sum'] or Decimal('0.00')

    # 5. Custos Operacionais (Do Formulário)
    custos_operacionais = custo_obj.custo_variavel_total
    custos_fixos_mei = custo_obj.custo_fixo_total

    # 6. Resultados (Recalculados com base nos filtros)
    custo_total_geral = cmv + custos_operacionais + custos_fixos_mei
    lucro_liquido = faturamento_bruto - custo_total_geral

    margem_lucro = (lucro_liquido / faturamento_bruto * 100) if faturamento_bruto > 0 else 0
    ticket_medio = faturamento_bruto / total_vendas_qtd if total_vendas_qtd > 0 else 0
    # Ponto de Equilíbrio é mais complexo de filtrar, mantendo o cálculo geral
    ponto_equilibrio = custos_fixos_mei / (
            1 - ((custos_operacionais + cmv) / faturamento_bruto)) if faturamento_bruto > 0 and (
            custos_operacionais + cmv) < faturamento_bruto else 0

    # 7. Dados para Gráficos (JSON)
    # Gráfico 1: Vendas por Dia (Linha) - JÁ USA vendas_mes FILTRADO
    vendas_diarias = vendas_mes.annotate(dia=TruncDay('data_venda')).values('dia').annotate(
        total=Sum('valor_total')).order_by('dia')
    chart_dias = [v['dia'].strftime('%d/%m') for v in vendas_diarias]
    chart_valores = [float(v['total']) for v in vendas_diarias]

    # Gráfico 2: Distribuição de Custos (Rosca) - Mantido com custos TOTAIS (sem filtro de venda)
    chart_custos_labels = ['Matéria Prima (CMV)', 'Insumos (Cola/Emb/Energia)', 'Taxas/MEI']
    chart_custos_values = [float(cmv), float(custos_operacionais), float(custos_fixos_mei)]

    # === SEÇÃO NOVA: COMPOSIÇÃO DE CUSTO POR PRODUTO UNITÁRIO ===
    custo_produto_selecionado = None

    if filtro_produto_id:
        try:
            produto_selecionado = Produto.objects.get(pk=filtro_produto_id)

            # Custo de Matéria Prima (CMV unitário)
            # Assumindo que Produto.custo_total já calcula (CMV unitário + Custo Fixo Unitário)
            custo_unitario_total = produto_selecionado.custo_total
            custo_operacional_unitario = produto_selecionado.custo_fixo_total
            custo_materiais = custo_unitario_total - custo_operacional_unitario

            # Valor de Venda
            valor_venda = produto_selecionado.valor_venda or Decimal('0.00')
            lucro_bruto_unitario = valor_venda - custo_unitario_total

            # === NOVO: COMPOSIÇÃO DE CUSTO PARA O GRÁFICO ===

            # 1. Obter os custos dos materiais individuais
            materiais_para_grafico = []

            for mu in produto_selecionado.materiais_usados.all():
                nome_material = mu.compra_materia_prima.materia_prima.nome if mu.compra_materia_prima else 'Mat. Não Especificado'
                materiais_para_grafico.append({
                    'label': nome_material,
                    'valor': mu.valor_total
                })

            # 2. Adicionar o Custo Operacional Unitário como uma fatia separada
            materiais_para_grafico.append({
                'label': 'Custo Fixo/Op. Unitário',
                'valor': custo_operacional_unitario
            })

            # 3. Preparar as listas JSON
            chart_labels = [m['label'] for m in materiais_para_grafico]
            chart_values = [float(m['valor']) for m in materiais_para_grafico]

            # 4. Criar o objeto de contexto atualizado
            custo_produto_selecionado = {
                'nome': produto_selecionado.nome,
                'custo_total': custo_unitario_total,
                'valor_venda': valor_venda,
                'lucro_liquido': lucro_bruto_unitario,
                'materiais_detalhe': [
                    {
                        'nome': mu.compra_materia_prima.materia_prima.nome if mu.compra_materia_prima else 'Mat. Não Especificado',
                        'valor': mu.valor_total}
                    for mu in produto_selecionado.materiais_usados.all()
                ],
                # Passando as novas listas de materiais para o Chart.js
                'custos_unitarios_chart': json.dumps(chart_values),
                'custos_unitarios_labels': json.dumps(chart_labels),
                'produto_id': produto_selecionado.id,
            }

        except Produto.DoesNotExist:
            pass  # Continua com None se o ID for inválido
    # ===================================================

    context = {
        'data_atual': data_referencia,
        'form': form,
        'kpis': {
            'faturamento': faturamento_bruto,
            'lucro_liquido': lucro_liquido,
            'margem': round(margem_lucro, 1),
            'ticket_medio': ticket_medio,
            'custo_total': custo_total_geral,
            'roi': (lucro_liquido / custo_total_geral * 100) if custo_total_geral > 0 else 0,
        },
        'charts': {
            'dias': json.dumps(chart_dias),
            'vendas_dia': json.dumps(chart_valores),
            'custos_labels': json.dumps(chart_custos_labels),
            'custos_values': json.dumps(chart_custos_values),
        },
        'meses_nav': {
            'anterior': (data_referencia - timedelta(days=1)).replace(day=1),
            'proximo': (data_referencia + timedelta(days=32)).replace(day=1)
        },
        # === DADOS DE CONTEXTO PARA OS FILTROS ===
        'produtos': produtos,
        'metodos_pagamento': metodos_pagamento,
        'categorias_produto': categorias_produto,
        'filtro_metodo_ativo': filtro_metodo,
        'filtro_categoria_ativo': filtro_categoria,
        'custo_produto_selecionado': custo_produto_selecionado,
        # ========================================
    }

    return render(request, "financeiro.html", context)


@csrf_exempt
def get_custo_produto_json(request):
    """Retorna os dados de custo de um produto específico como JSON."""
    produto_id = request.GET.get('produto_id')

    if not produto_id:
        return JsonResponse({'success': False, 'message': 'ID do produto não fornecido'}, status=400)

    try:
        # Reutilize a lógica de busca do produto e cálculo de custos
        produto_selecionado = Produto.objects.get(pk=produto_id)

        custo_unitario_total = produto_selecionado.custo_total
        custo_operacional_unitario = produto_selecionado.custo_fixo_total

        valor_venda = produto_selecionado.valor_venda or Decimal('0.00')
        lucro_bruto_unitario = valor_venda - custo_unitario_total

        # 1. Obter os custos dos materiais individuais
        materiais_para_grafico = []
        html_materiais_detalhe = ""  # Variável para construir o HTML dos detalhes

        for mu in produto_selecionado.materiais_usados.all():
            nome_material = mu.compra_materia_prima.materia_prima.nome if mu.compra_materia_prima else 'Mat. Não Especificado'

            materiais_para_grafico.append({
                'label': nome_material,
                'valor': mu.valor_total
            })

            # Constrói a lista de materiais para o HTML
            html_materiais_detalhe += f"""
                <li class="list-group-item d-flex justify-content-between align-items-center py-1">
                    {nome_material[:30]}
                    <span class="badge bg-secondary rounded-pill">R$ {mu.valor_total:.2f}</span>
                </li>
            """

        # Adicionar o Custo Operacional Unitário
        materiais_para_grafico.append({
            'label': 'Custo Fixo/Op. Unitário',
            'valor': custo_operacional_unitario
        })

        chart_labels = [m['label'] for m in materiais_para_grafico]
        chart_values = [float(m['valor']) for m in materiais_para_grafico]

        # 2. Constrói o HTML dos Detalhes (Colunas Direita)
        html_detalhe = f"""
            <hr>
            <div class="row">
                <div class="col-md-6">
                    <h6 class="text-secondary">Composição do Custo Unitário ({produto_selecionado.nome})</h6>
                    <canvas id="chartProdutoCusto" height="200"></canvas>
                </div>
                <div class="col-md-6">
                    <h6 class="text-secondary">Detalhes e Rentabilidade</h6>
                    <ul class="list-group list-group-flush">
                        <li class="list-group-item d-flex justify-content-between align-items-center">
                            Valor de Venda (Preço)
                            <span class="badge bg-success rounded-pill">R$ {valor_venda:.2f}</span>
                        </li>
                        <li class="list-group-item d-flex justify-content-between align-items-center">
                            **CUSTO TOTAL (CMV + Fixo)**
                            <span class="badge bg-danger rounded-pill">R$ {custo_unitario_total:.2f}</span>
                        </li>
                        <li class="list-group-item d-flex justify-content-between align-items-center bg-light">
                            **LUCRO BRUTO UNITÁRIO**
                            <span class="badge bg-primary rounded-pill">R$ {lucro_bruto_unitario:.2f}</span>
                        </li>
                    </ul>

                    <h6 class="mt-3 text-secondary">Matérias-Primas Detalhadas:</h6>
                    <small class="d-block mb-1">Custo de cada material no produto:</small>
                    <ul class="list-group">
                        {html_materiais_detalhe}
                    </ul>
                </div>
            </div>
        """

        # 3. Retorna os dados em JSON
        return JsonResponse({
            'success': True,
            'nome': produto_selecionado.nome,
            'custos_unitarios_chart': chart_values,  # Lista de floats
            'custos_unitarios_labels': chart_labels,  # Lista de strings
            'html_detalhe': html_detalhe  # HTML formatado
        })

    except Produto.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Produto não encontrado'}, status=404)
    except NameError:
        # Garante que funciona mesmo se os modelos não estiverem definidos (para fins de teste)
        return JsonResponse({'success': False, 'message': 'Erro de Definição de Modelo'}, status=500)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)