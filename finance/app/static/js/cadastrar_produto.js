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
            materiaisData = JSON.parse(materiaisJsonElement.textContent);
            console.log("✅ Materiais carregados:", Object.keys(materiaisData).length);
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

        // Atualiza todos os elementos
        novoItem.querySelectorAll("input, select, label").forEach(elemento => {
            if (elemento.tagName === "LABEL") {
                const forAttr = elemento.getAttribute("for");
                if (forAttr) {
                    elemento.setAttribute("for", forAttr.replace(/form-\d+-/, `form-${currentFormCount}-`));
                }
            } else {
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
        console.log("🔄 Aplicando eventos");

        // EVENTOS: Botões remover
        document.querySelectorAll(".btn-remover-material").forEach(btn => {
            btn.replaceWith(btn.cloneNode(true));
        });

        document.querySelectorAll(".btn-remover-material").forEach(btn => {
            btn.addEventListener("click", function() {
                const materiais = document.querySelectorAll(".material-item");

                // ⚠️ Impede remover se houver apenas 1 material
                if (materiais.length <= 1) {
                    alert("⚠️ É necessário manter pelo menos um material no formulário.");
                    return;
                }

                console.log("🗑️ Removendo material definitivamente");
                const item = this.closest(".material-item");
                if (!item) return;

                item.remove();

                // Atualiza índices
                const items = document.querySelectorAll(".material-item");
                items.forEach((el, index) => {
                    el.querySelectorAll("input, select, label").forEach(elemento => {
                        if (elemento.name) elemento.name = elemento.name.replace(/form-\d+-/, `form-${index}-`);
                        if (elemento.id) elemento.id = elemento.id.replace(/form-\d+-/, `form-${index}-`);
                        if (elemento.tagName === "LABEL" && elemento.getAttribute("for"))
                            elemento.setAttribute("for", elemento.getAttribute("for").replace(/form-\d+-/, `form-${index}-`));
                    });
                });

                totalFormsInput.value = items.length;
                console.log(`📉 Novo total de materiais: ${totalFormsInput.value}`);

                calcularTudo();
            });
        });

        // EVENTOS: Selects de material
        document.querySelectorAll('.material-select').forEach(select => {
            select.removeEventListener("change", calcularTudo);
            select.addEventListener("change", calcularTudo);
        });

        // EVENTOS: Tipo de unidade
        document.querySelectorAll('.tipo-unidade-select').forEach(select => {
            select.removeEventListener("change", calcularTudo);
            select.addEventListener("change", calcularTudo);
        });

        // EVENTOS: Quantidade de material
        document.querySelectorAll('.qtd-material-input').forEach(input => {
            input.removeEventListener("input", calcularTudo);
            input.addEventListener("input", calcularTudo);
        });

        // EVENTOS: Custos fixos
        document.querySelectorAll('.custo-fixo-input').forEach(input => {
            input.removeEventListener("input", calcularTudo);
            input.addEventListener("input", calcularTudo);
        });

        // EVENTOS: Valor de venda
        if (valorVendaInput) {
            valorVendaInput.removeEventListener("input", calcularTudo);
            valorVendaInput.addEventListener("input", calcularTudo);
        }
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
                    } else if (tipoUnidade === 'QUANTIDADE') {
                        valorUnitario = material.valor_por_quantidade || 0;
                    }

                    const custoMaterial = valorUnitario * quantidade;
                    totalMateriais += custoMaterial;

                    if (valorSpan) valorSpan.textContent = custoMaterial.toFixed(2);
                } else if (valorSpan) {
                    valorSpan.textContent = '0.00';
                }
            }
        });

        document.querySelectorAll('.custo-fixo-input').forEach(input => {
            totalCustosFixos += parseFloat(input.value) || 0;
        });

        const custoTotal = totalMateriais + totalCustosFixos;

        if (totalMateriaisSpan) totalMateriaisSpan.textContent = totalMateriais.toFixed(2);
        if (totalCustosFixosSpan) totalCustosFixosSpan.textContent = totalCustosFixos.toFixed(2);
        if (custoTotalInput) custoTotalInput.value = custoTotal.toFixed(2);

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
