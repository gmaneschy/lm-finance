// ========== CADASTRAR PRODUTO - JAVASCRIPT ==========

document.addEventListener("DOMContentLoaded", function() {
    console.log("🚀 Sistema de Cadastro de Produto iniciado");

    // ========== ELEMENTOS DO DOM ==========
    const totalFormsInput = document.getElementById("id_form-TOTAL_FORMS");
    const formsetContainer = document.getElementById("materiais-formset");
    const addButton = document.getElementById("add-material");
    const custoTotalInput = document.getElementById("id_custo_total_estimado");
    const valorVendaInput = document.getElementById("id_valor_venda");
    const lucroVendaInput = document.getElementById("id_lucro_por_venda");
    const totalMateriaisSpan = document.getElementById("total-materiais");
    const totalCustosFixosSpan = document.getElementById("total-custos-fixos");
    const bloqueioCheckbox = document.getElementById("id_custos_bloqueados");

    // Verifica elementos essenciais
    if (!totalFormsInput || !formsetContainer || !addButton) {
        console.error("❌ Elementos essenciais não encontrados!");
        return;
    }

    // ========== CARREGA DADOS DOS MATERIAIS ==========
    let materiaisData = {};
    try {
        const materiaisJsonElement = document.getElementById('materiais-data');
        if (materiaisJsonElement) {
            // Garante que o conteúdo seja lido como string antes do parse
            const jsonText = materiaisJsonElement.textContent.trim();
            if (jsonText) {
                materiaisData = JSON.parse(jsonText);
                console.log("✅ Materiais carregados:", Object.keys(materiaisData).length);
                // 💡 DEBUG: Loga o objeto de dados recebido do Django para inspeção
                console.log("DEBUG: materiaisData (Primeiros 5 itens):", Object.fromEntries(Object.entries(materiaisData).slice(0, 5)));
            }
        }
    } catch (e) {
        console.error("❌ Erro ao carregar materiais:", e);
    }

    // ========== FUNÇÃO: TOGGLE BLOQUEIO CUSTOS FIXOS ==========
    function toggleBloqueioCalculado() {
        const inputs = document.querySelectorAll('.custo-fixo-input');
        const bloqueado = bloqueioCheckbox.checked;

        inputs.forEach(input => {
            if (bloqueado) {
                input.setAttribute('readonly', 'readonly');
                input.style.cursor = 'not-allowed';
            } else {
                input.removeAttribute('readonly');
                input.style.cursor = 'text';
            }
        });

        const textoEl = document.querySelector('.texto-bloqueio');
        if (textoEl) {
            textoEl.textContent = bloqueado ? 'Bloqueado' : 'Desbloqueado';
        }
    }

    if (bloqueioCheckbox) {
        bloqueioCheckbox.addEventListener('change', toggleBloqueioCalculado);
        toggleBloqueioCalculado();
    }

    // ========== FUNÇÃO: ADICIONAR MATERIAL ==========
    addButton.addEventListener("click", function() {
        console.log("➕ Adicionando novo material");

        const currentFormCount = parseInt(totalFormsInput.value);
        const primeiroItem = document.querySelector(".material-item");

        if (!primeiroItem) {
            console.error("❌ Template não encontrado");
            return;
        }

        // Clona o primeiro item
        const novoItem = primeiroItem.cloneNode(true);
        novoItem.classList.remove("deletado");
        novoItem.setAttribute("data-form-index", currentFormCount);

        // Remove listeners temporariamente antes da clonagem (embora cloneNode(true) já faça isso)
        // E limpa os valores do novo item
        novoItem.querySelectorAll("input, select, label").forEach(elemento => {
            if (elemento.tagName === "LABEL") {
                const forAttr = elemento.getAttribute("for");
                if (forAttr) {
                    elemento.setAttribute("for", forAttr.replace(/form-\d+-/, `form-${currentFormCount}-`));
                }
            } else {
                // Atualiza name e id
                if (elemento.name) elemento.name = elemento.name.replace(/form-\d+-/, `form-${currentFormCount}-`);
                if (elemento.id) elemento.id = elemento.id.replace(/form-\d+-/, `form-${currentFormCount}-`);

                // Limpa valores
                if (elemento.tagName === "SELECT") {
                    elemento.selectedIndex = 0;
                } else if (elemento.type === "number" || elemento.type === "text") {
                    elemento.value = "";
                } else if (elemento.type === "checkbox") {
                    elemento.checked = false;
                }
            }
        });

        // Reseta o valor do material
        const valorSpan = novoItem.querySelector('.valor-material-span');
        if (valorSpan) valorSpan.textContent = '0.00';

        formsetContainer.appendChild(novoItem);
        totalFormsInput.value = currentFormCount + 1;

        console.log(`✅ Material adicionado. Total: ${totalFormsInput.value}`);

        aplicarEventos();
        calcularTudo();
    });

    // ========== FUNÇÃO: APLICAR EVENTOS ==========
    function aplicarEventos() {
        // console.log("🔄 Aplicando eventos");

        // EVENTOS: Botões remover
        document.querySelectorAll(".btn-remover-material").forEach(btn => {
            btn.removeEventListener("click", removerMaterialHandler);
            btn.addEventListener("click", removerMaterialHandler);
        });

        // Eventos de cálculo (change e input)
        const selectors = [
            '.material-select',
            '.tipo-unidade-select',
            '.qtd-material-input',
            '.custo-fixo-input'
        ];

        selectors.forEach(selector => {
            document.querySelectorAll(selector).forEach(elemento => {
                elemento.removeEventListener("change", calcularTudo);
                elemento.removeEventListener("input", calcularTudo);

                elemento.addEventListener("change", calcularTudo);
                elemento.addEventListener("input", calcularTudo);
            });
        });

        // EVENTOS: Valor de venda (apenas input)
        if (valorVendaInput) {
            valorVendaInput.removeEventListener("input", calcularTudo);
            valorVendaInput.addEventListener("input", calcularTudo);
        }
    }

    // Handler para o botão de remoção
    function removerMaterialHandler() {
        const materiais = document.querySelectorAll(".material-item");

        if (materiais.length <= 1) {
            console.warn("⚠️ É necessário manter pelo menos um material no formulário.");
            // Substitua alert() por um modal customizado no seu projeto final
            return;
        }

        console.log("🗑️ Removendo material");
        const item = this.closest(".material-item");
        if (!item) return;

        item.remove();

        const items = document.querySelectorAll(".material-item");
        items.forEach((el, index) => {
            el.setAttribute("data-form-index", index);
            el.querySelectorAll("input, select, label").forEach(elemento => {
                const regex = /form-\d+-/;
                if (elemento.name) elemento.name = elemento.name.replace(regex, `form-${index}-`);
                if (elemento.id) elemento.id = elemento.id.replace(regex, `form-${index}-`);
                if (elemento.tagName === "LABEL" && elemento.getAttribute("for"))
                    elemento.setAttribute("for", elemento.getAttribute("for").replace(regex, `form-${index}-`));
            });
        });

        totalFormsInput.value = items.length;
        console.log(`📉 Novo total de materiais: ${totalFormsInput.value}`);

        calcularTudo();
    }


    // ========== FUNÇÃO: CALCULAR TUDO ==========
    function calcularTudo() {
        console.log("💰 Calculando valores");

        let totalMateriais = 0;
        let totalCustosFixos = 0;

        document.querySelectorAll(".material-item").forEach(item => {
            const selectMaterial = item.querySelector('.material-select');
            const selectTipoUnidade = item.querySelector('.tipo-unidade-select');
            const inputQtd = item.querySelector('.qtd-material-input');
            const valorSpan = item.querySelector('.valor-material-span');

            if (selectMaterial && selectTipoUnidade && inputQtd) {
                const materialId = selectMaterial.value;
                const tipoUnidade = selectTipoUnidade.value;
                const quantidade = parseFloat(inputQtd.value) || 0;

                let valorUnitario = 0;

                if (materialId && materiaisData[materialId]) {
                    const material = materiaisData[materialId];

                    if (tipoUnidade === 'CM') {
                        valorUnitario = material.valor_por_cm || 0;
                        console.log(`DEBUG CÁLCULO: Material ID ${materialId} (CM). Valor Unitário LIDO: ${valorUnitario}. Qtd: ${quantidade}`);
                    } else if (tipoUnidade === 'QUANTIDADE') {
                        valorUnitario = material.valor_por_quantidade || 0;
                        // 💡 LOG DE DEBUG ADICIONADO AQUI
                        console.log(`DEBUG CÁLCULO: Material ID ${materialId} (QUANTIDADE). Valor Unitário LIDO: ${valorUnitario}. Qtd: ${quantidade}`);
                    }

                    const custoMaterial = valorUnitario * quantidade;
                    totalMateriais += custoMaterial;

                    if (valorSpan) valorSpan.textContent = custoMaterial.toFixed(2);
                } else if (valorSpan) {
                    valorSpan.textContent = '0.00';
                }
            }
        });

        // Cálculo dos custos fixos
        document.querySelectorAll('.custo-fixo-input').forEach(input => {
            totalCustosFixos += parseFloat(input.value) || 0;
        });

        const custoTotal = totalMateriais + totalCustosFixos;

        if (totalMateriaisSpan) totalMateriaisSpan.textContent = totalMateriais.toFixed(2);
        if (totalCustosFixosSpan) totalCustosFixosSpan.textContent = totalCustosFixos.toFixed(2);

        // Atualiza o Custo Total no formulário do produto
        if (custoTotalInput) custoTotalInput.value = custoTotal.toFixed(2);

        // Cálculo do Lucro
        if (valorVendaInput && lucroVendaInput) {
            const valorVenda = parseFloat(valorVendaInput.value) || 0;
            const lucro = valorVenda - custoTotal;
            lucroVendaInput.value = lucro.toFixed(2);
        }

        console.log(`📊 Materiais: R$ ${totalMateriais.toFixed(2)} | Custos: R$ ${totalCustosFixos.toFixed(2)} | Total: R$ ${custoTotal.toFixed(2)}`);
    }

    // ========== INICIALIZAÇÃO ==========
    console.log("🎬 Inicializando sistema");
    aplicarEventos();
    calcularTudo();
    console.log("✅ Sistema pronto!");
});