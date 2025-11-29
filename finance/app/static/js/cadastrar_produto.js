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
            const jsonText = materiaisJsonElement.textContent.trim();
            if (jsonText) {
                materiaisData = JSON.parse(jsonText);
                console.log("✅ Materiais carregados:", Object.keys(materiaisData).length);
                // Log de debug para ver a estrutura dos dados
                console.log("DEBUG CARGA: materiaisData (Primeiro item):", Object.values(materiaisData)[0]);
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
        calcularTudo();
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

        const novoItem = primeiroItem.cloneNode(true);
        novoItem.classList.remove("deletado");
        novoItem.setAttribute("data-form-index", currentFormCount);

        novoItem.querySelectorAll("input, select, label").forEach(elemento => {
            const regex = /form-\d+-/;

            if (elemento.tagName === "LABEL") {
                const forAttr = elemento.getAttribute("for");
                if (forAttr) {
                    elemento.setAttribute("for", forAttr.replace(regex, `form-${currentFormCount}-`));
                }
            } else {
                if (elemento.name) elemento.name = elemento.name.replace(regex, `form-${currentFormCount}-`);
                if (elemento.id) elemento.id = elemento.id.replace(regex, `form-${currentFormCount}-`);

                if (elemento.tagName === "SELECT") {
                    elemento.selectedIndex = 0;
                } else if (elemento.type === "number" || elemento.type === "text") {
                    elemento.value = "";
                } else if (elemento.type === "checkbox") {
                    elemento.checked = false;
                }
            }
        });

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
        document.querySelectorAll(".btn-remover-material").forEach(btn => {
            btn.removeEventListener("click", removerMaterialHandler);
            btn.addEventListener("click", removerMaterialHandler);
        });

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


    // ========== FUNÇÃO: CALCULAR TUDO (COM CORREÇÃO DE LOCALE E LOGS DE DEBUG) ==========
    function calcularTudo() {
        console.log("========================================");
        console.log("💰 INICIANDO CÁLCULO DE CUSTOS");
        console.log("========================================");

        let totalMateriais = 0;
        let totalCustosFixos = 0;
        let formIndex = 0;

        document.querySelectorAll(".material-item").forEach(item => {
            console.log(`\n--- Item Material #${formIndex} ---`);
            const selectMaterial = item.querySelector('.material-select');
            const selectTipoUnidade = item.querySelector('.tipo-unidade-select');
            const inputQtd = item.querySelector('.qtd-material-input');
            const valorSpan = item.querySelector('.valor-material-span');

            // 1. Verificar se os elementos foram encontrados
            if (!selectMaterial || !selectTipoUnidade || !inputQtd) {
                 console.error(`❌ Elementos de formulário não encontrados no item #${formIndex}. Pulando...`);
                 formIndex++;
                 return;
            }

            const materialId = selectMaterial.value;
            const tipoUnidade = selectTipoUnidade.value;

            // 2. Leitura e conversão da Quantidade
            const inputQtdValue = inputQtd.value;
            const quantidade = parseFloat(inputQtdValue.replace(',', '.')) || 0;

            console.log(`   - materialId Selecionado: "${materialId}"`);
            console.log(`   - Tipo de Unidade: "${tipoUnidade}"`);
            console.log(`   - Qtd (String Lida): "${inputQtdValue}"`);
            console.log(`   - Qtd (Convertida Float): ${quantidade}`);

            let valorUnitario = 0;
            let custoMaterial = 0;

            // 3. Verificar se há material selecionado e dados disponíveis
            if (materialId && materiaisData[materialId]) {
                const material = materiaisData[materialId];
                console.log(`   - Dados do Material (JSON):`, material);

                if (tipoUnidade === 'CM') {
                    valorUnitario = parseFloat(material.valor_por_cm || 0) || 0;
                } else if (tipoUnidade === 'QUANTIDADE') {
                    valorUnitario = parseFloat(material.valor_por_quantidade || 0) || 0;
                }

                // 4. Cálculo final do material
                custoMaterial = valorUnitario * quantidade;
                totalMateriais += custoMaterial;

                console.log(`   - Valor Unitário Final: ${valorUnitario.toFixed(4)}`);
                console.log(`   - Custo Material Calculado: R$ ${custoMaterial.toFixed(2)}`);

                if (valorSpan) valorSpan.textContent = custoMaterial.toFixed(2);

            } else {
                console.log("   - ⚠️ Material não selecionado ou dados indisponíveis.");
                if (valorSpan) valorSpan.textContent = '0.00';
            }
            formIndex++;
        });

        console.log("\n--- Cálculo Custos Fixos ---");
        // Cálculo dos custos fixos
        document.querySelectorAll('.custo-fixo-input').forEach(input => {
            const custoValor = parseFloat(input.value.replace(',', '.')) || 0;
            totalCustosFixos += custoValor;
        });
        console.log(`   - Total Custos Fixos (Calculado): R$ ${totalCustosFixos.toFixed(2)}`);

        // Cálculo Total
        const custoTotal = totalMateriais + totalCustosFixos;
        console.log(`--- Resumo Final ---`);
        console.log(`   - Total Materiais: R$ ${totalMateriais.toFixed(2)}`);
        console.log(`   - Custo Total Estimado: R$ ${custoTotal.toFixed(2)}`);


        if (totalMateriaisSpan) totalMateriaisSpan.textContent = totalMateriais.toFixed(2);
        if (totalCustosFixosSpan) totalCustosFixosSpan.textContent = totalCustosFixos.toFixed(2);

        // Atualiza o Custo Total no formulário do produto
        if (custoTotalInput) custoTotalInput.value = custoTotal.toFixed(2);

        // Cálculo do Lucro
        if (valorVendaInput && lucroVendaInput) {
            const valorVenda = parseFloat(valorVendaInput.value.replace(',', '.')) || 0;
            const lucro = valorVenda - custoTotal;
            lucroVendaInput.value = lucro.toFixed(2);
            console.log(`   - Valor de Venda: R$ ${valorVenda.toFixed(2)}`);
            console.log(`   - Lucro por Venda: R$ ${lucro.toFixed(2)}`);
        }

        console.log("========================================");
        console.log("💰 CÁLCULO CONCLUÍDO");
        console.log("========================================");
    }

    // ===============================================
    // ========== FUNÇÃO: EXIBIR TOAST/MENSAGEM ==========
    // ===============================================

    /**
     * Exibe uma mensagem de toast que desaparece automaticamente.
     * @param {string} message - O texto da mensagem.
     * @param {string} type - 'success' ou 'error'.
     * @param {number} duration - Duração em milissegundos (padrão 2000ms).
     */
    function showToast(message, type, duration = 2000) {
        const toast = document.getElementById('toast-message');
        const toastText = document.getElementById('toast-text');

        if (!toast || !toastText) {
            console.error("Elemento Toast não encontrado.");
            return;
        }

        toastText.textContent = message;
        toast.classList.remove('success', 'error');
        toast.classList.add(type);

        // 1. Mostrar o toast
        toast.style.display = 'block';
        // Força o reflow para garantir a transição de opacidade
        void toast.offsetWidth;
        toast.classList.add('show');

        // 2. Esconder o toast após a duração
        setTimeout(() => {
            toast.classList.remove('show');
            // Esconde completamente após a transição de fade-out
            setTimeout(() => {
                toast.style.display = 'none';
            }, 500); // 500ms é o tempo de transição do CSS
        }, duration);
    }


    // ========== INICIALIZAÇÃO E TRATAMENTO DE MENSAGENS ==========
    console.log("🎬 Inicializando sistema");
    aplicarEventos();
    calcularTudo();

    // ========== VERIFICA MENSAGENS DO DJANGO E EXIBE TOAST ==========
    // Procura por mensagens do Django (geralmente em ul.messagelist li)
    document.querySelectorAll('.messagelist li').forEach(messageEl => {
        const messageText = messageEl.textContent.trim();
        const isSuccess = messageEl.classList.contains('success');
        const isError = messageEl.classList.contains('error');

        if (isSuccess) {
            showToast(messageText.replace('✅', ''), 'success', 3000); // Exibe por 3 segundos
        } else if (isError) {
            // Mensagens de erro de estoque são longas, exibe por mais tempo
            showToast(messageText.replace('❌', ''), 'error', 6000);
        }

        // Remove a mensagem do DOM original para que só o toast apareça
        messageEl.remove();
    });

    console.log("✅ Sistema pronto!");
});