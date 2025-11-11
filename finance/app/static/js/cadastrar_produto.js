// Aguarda o carregamento completo do DOM
document.addEventListener("DOMContentLoaded", function() {
    console.log("🚀 Script cadastrar_produto iniciado");

    // Elementos do DOM
    const totalFormsInput = document.getElementById("id_form-TOTAL_FORMS");
    const formsetContainer = document.getElementById("materiais-formset");
    const addButton = document.getElementById("add-material");
    const custoTotalSpan = document.getElementById("custo-total");
    const valorVendaInput = document.getElementById("id_valor_venda");
    const lucroVendaInput = document.getElementById("id_lucro_por_venda");

    // Verifica se os elementos existem
    if (!totalFormsInput || !formsetContainer || !addButton) {
        console.error("❌ Elementos essenciais não encontrados!");
        return;
    }

    // Carrega os dados dos materiais passados pelo Django
    let materiaisData = {};
    try {
        const scriptTag = document.querySelector('script[data-materiais]');
        if (scriptTag) {
            materiaisData = JSON.parse(scriptTag.textContent);
        } else {
            // Fallback: tenta buscar do template
            const materiaisJsonElement = document.getElementById('materiais-data');
            if (materiaisJsonElement) {
                materiaisData = JSON.parse(materiaisJsonElement.textContent);
            }
        }
        console.log("✅ Dados dos materiais carregados:", materiaisData);
    } catch (e) {
        console.error("❌ Erro ao carregar dados dos materiais:", e);
    }

    // ========== FUNÇÃO: ADICIONAR NOVO MATERIAL ==========
    addButton.addEventListener("click", function() {
        console.log("➕ Adicionando novo material");

        const currentFormCount = parseInt(totalFormsInput.value);
        const primeiroItem = document.querySelector(".material-item");

        if (!primeiroItem) {
            console.error("❌ Não foi possível encontrar o template do material");
            return;
        }

        // Clona o primeiro item
        const novoItem = primeiroItem.cloneNode(true);

        // Remove a classe "deletado" se existir
        novoItem.classList.remove("deletado");

        // Atualiza todos os campos do novo item
        novoItem.querySelectorAll("input, select, label").forEach(elemento => {
            if (elemento.tagName === "LABEL") {
                // Atualiza o atributo "for" das labels
                const forAttr = elemento.getAttribute("for");
                if (forAttr) {
                    elemento.setAttribute("for", forAttr.replace(/form-\d+-/, `form-${currentFormCount}-`));
                }
            } else {
                // Atualiza name e id de inputs e selects
                if (elemento.name) {
                    elemento.name = elemento.name.replace(/form-\d+-/, `form-${currentFormCount}-`);
                }
                if (elemento.id) {
                    elemento.id = elemento.id.replace(/form-\d+-/, `form-${currentFormCount}-`);
                }

                // Limpa os valores
                if (elemento.tagName === "SELECT") {
                    elemento.selectedIndex = 0;
                } else if (elemento.type === "number" || elemento.type === "text") {
                    elemento.value = "";
                } else if (elemento.type === "checkbox") {
                    elemento.checked = false;
                }
            }
        });

        // Atualiza o data-index do botão remover
        const removeBtn = novoItem.querySelector(".remove-btn");
        if (removeBtn) {
            removeBtn.setAttribute("data-index", currentFormCount);
        }

        // Adiciona o novo item ao container
        formsetContainer.appendChild(novoItem);

        // Incrementa o contador de forms
        totalFormsInput.value = currentFormCount + 1;

        console.log(`✅ Novo material adicionado. Total de forms: ${totalFormsInput.value}`);

        // Reaplica os eventos
        aplicarEventos();
        calcularCustoTotal();
    });

    // ========== FUNÇÃO: APLICAR EVENTOS ==========
    function aplicarEventos() {
        console.log("🔄 Aplicando eventos nos elementos");

        // Eventos dos botões REMOVER
        document.querySelectorAll(".remove-btn").forEach(btn => {
            // Remove evento antigo (se existir)
            btn.replaceWith(btn.cloneNode(true));
        });

        document.querySelectorAll(".remove-btn").forEach(btn => {
            btn.addEventListener("click", function() {
                console.log("🗑️ Removendo material");

                const item = this.closest(".material-item");
                const deleteCheckbox = item.querySelector("input[type='checkbox'][name*='DELETE']");

                if (deleteCheckbox) {
                    // Se tem checkbox DELETE, marca para deletar (item já existente)
                    deleteCheckbox.checked = true;
                    item.classList.add("deletado");
                    item.style.opacity = "0.5";
                    item.style.background = "#ffebee";
                } else {
                    // Se não tem checkbox, remove do DOM (item novo)
                    item.remove();
                }

                calcularCustoTotal();
            });
        });

        // Eventos dos SELECTS de material
        document.querySelectorAll('select[name*="compra_materia_prima"]').forEach(select => {
            select.removeEventListener("change", calcularCustoTotal);
            select.addEventListener("change", calcularCustoTotal);
        });

        // Eventos dos INPUTS de quantidade
        document.querySelectorAll('input[name*="qtd_material_usado"]').forEach(input => {
            input.removeEventListener("input", calcularCustoTotal);
            input.addEventListener("input", calcularCustoTotal);
        });

        // Eventos dos CUSTOS FIXOS
        const custoFixoInputs = [
            document.querySelector('input[name="energia"]'),
            document.querySelector('input[name="cola"]'),
            document.querySelector('input[name="isqueiro"]'),
            document.querySelector('input[name="das_mei"]'),
            document.querySelector('input[name="taxas_bancarias"]'),
            document.querySelector('input[name="tempo"]')
        ];

        custoFixoInputs.forEach(input => {
            if (input) {
                input.removeEventListener("input", calcularCustoTotal);
                input.addEventListener("input", calcularCustoTotal);
            }
        });

        // Evento do VALOR DE VENDA
        if (valorVendaInput) {
            valorVendaInput.removeEventListener("input", calcularCustoTotal);
            valorVendaInput.addEventListener("input", calcularCustoTotal);
        }
    }

    // ========== FUNÇÃO: CALCULAR CUSTO TOTAL ==========
    function calcularCustoTotal() {
        console.log("💰 Calculando custo total");

        let totalMateriais = 0;
        let totalCustosFixos = 0;

        // ===== CALCULA CUSTO DOS MATERIAIS =====
        document.querySelectorAll(".material-item").forEach(item => {
            // Ignora itens marcados para deletar
            const deleteCheckbox = item.querySelector("input[type='checkbox'][name*='DELETE']");
            if (deleteCheckbox && deleteCheckbox.checked) {
                console.log("⏭️ Item marcado para deletar, ignorando");
                return;
            }

            const selectMaterial = item.querySelector('select[name*="compra_materia_prima"]');
            const inputQtd = item.querySelector('input[name*="qtd_material_usado"]');

            if (selectMaterial && inputQtd) {
                const materialId = selectMaterial.value;
                const quantidade = parseFloat(inputQtd.value) || 0;

                if (materialId && quantidade > 0) {
                    // Busca o valor unitário nos dados carregados
                    const material = materiaisData[materialId];

                    if (material) {
                        const valorUnitario = material.valor_unitario || 0;
                        const custoMaterial = valorUnitario * quantidade;
                        totalMateriais += custoMaterial;

                        console.log(`📦 Material ID ${materialId}: ${quantidade} x R$ ${valorUnitario.toFixed(4)} = R$ ${custoMaterial.toFixed(2)}`);
                    } else {
                        console.warn(`⚠️ Material ID ${materialId} não encontrado nos dados`);
                    }
                }
            }
        });

        // ===== CALCULA CUSTOS FIXOS =====
        const custoFixoInputs = [
            { nome: 'energia', input: document.querySelector('input[name="energia"]') },
            { nome: 'cola', input: document.querySelector('input[name="cola"]') },
            { nome: 'isqueiro', input: document.querySelector('input[name="isqueiro"]') },
            { nome: 'das_mei', input: document.querySelector('input[name="das_mei"]') },
            { nome: 'taxas_bancarias', input: document.querySelector('input[name="taxas_bancarias"]') },
            { nome: 'tempo', input: document.querySelector('input[name="tempo"]') }
        ];

        custoFixoInputs.forEach(({ nome, input }) => {
            if (input) {
                const valor = parseFloat(input.value) || 0;
                totalCustosFixos += valor;
                if (valor > 0) {
                    console.log(`🔧 ${nome}: R$ ${valor.toFixed(2)}`);
                }
            }
        });

        // ===== CALCULA TOTAL =====
        const custoTotal = totalMateriais + totalCustosFixos;

        console.log(`📊 RESUMO:`);
        console.log(`   Materiais: R$ ${totalMateriais.toFixed(2)}`);
        console.log(`   Custos Fixos: R$ ${totalCustosFixos.toFixed(2)}`);
        console.log(`   TOTAL: R$ ${custoTotal.toFixed(2)}`);

        // Atualiza o span do custo total
        if (custoTotalSpan) {
            custoTotalSpan.textContent = custoTotal.toFixed(2);
        }

        // ===== CALCULA LUCRO =====
        if (valorVendaInput && lucroVendaInput) {
            const valorVenda = parseFloat(valorVendaInput.value) || 0;
            const lucro = valorVenda - custoTotal;
            lucroVendaInput.value = lucro.toFixed(2);

            console.log(`💵 Valor Venda: R$ ${valorVenda.toFixed(2)}`);
            console.log(`💰 Lucro: R$ ${lucro.toFixed(2)}`);
        }
    }

    // ========== INICIALIZAÇÃO ==========
    console.log("🎬 Inicializando sistema");
    aplicarEventos();
    calcularCustoTotal();
    console.log("✅ Sistema pronto!");
});