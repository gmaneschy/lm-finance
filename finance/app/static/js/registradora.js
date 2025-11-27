document.addEventListener('DOMContentLoaded', function () {
  const unidadeSelect = document.querySelector('#id_unidade');
  const camposQuantidade = document.getElementById('campos_quantidade');
  const camposCm = document.getElementById('campos_cm');
  const precoTotalInput = document.querySelector('#id_preco');

  // Campos de QUANTIDADE
  const qtdUnidadeInput = document.querySelector('#id_unidade_em_quantidade');
  const valorUnidadeInput = document.querySelector('#id_valor_por_quantidade');

  // Campos de CM
  const qtdCmInput = document.querySelector('#id_unidade_em_cm');
  const valorCmInput = document.querySelector('#id_valor_por_cm');

  if (!unidadeSelect || !camposQuantidade || !camposCm || !precoTotalInput) return;

  // ========== 1. FUNÇÃO DE CÁLCULO DE PREÇO TOTAL ==========
  function calcularPrecoTotal() {
    const tipoUnidade = unidadeSelect.value;
    let quantidade = 0;
    let valorUnitario = 0;

    if (tipoUnidade === 'QUANTIDADE') {
      // Usa os campos de QUANTIDADE
      quantidade = parseFloat(qtdUnidadeInput.value) || 0;
      valorUnitario = parseFloat(valorUnidadeInput.value) || 0;
    } else if (tipoUnidade === 'CM') {
      // Usa os campos de CM
      quantidade = parseFloat(qtdCmInput.value) || 0;
      valorUnitario = parseFloat(valorCmInput.value) || 0;
    }

    const precoTotal = quantidade * valorUnitario;

    // Atualiza o campo 'Preço Total' com o valor calculado, formatado com 2 casas decimais
    // O toFixed(2) é importante para garantir a precisão de moeda.
    precoTotalInput.value = precoTotal.toFixed(2);
  }

  // ========== 2. FUNÇÃO DE EXIBIÇÃO DE CAMPOS (EXISTENTE) ==========
  function toggleCampos() {
    const v = unidadeSelect.value;
    if (v === 'QUANTIDADE') {
      camposQuantidade.style.display = 'block';
      camposCm.style.display = 'none';
    } else if (v === 'CM') {
      camposQuantidade.style.display = 'none';
      camposCm.style.display = 'block';
    } else {
      camposQuantidade.style.display = 'none';
      camposCm.style.display = 'none';
    }
    // Garante que o cálculo seja refeito ao mudar o tipo de unidade
    calcularPrecoTotal();
  }

  // Monitora a mudança na unidade
  unidadeSelect.addEventListener('change', toggleCampos);

  // Monitora as entradas nos campos relevantes para o cálculo
  [qtdUnidadeInput, valorUnidadeInput, qtdCmInput, valorCmInput].forEach(input => {
    if (input) {
      input.addEventListener('input', calcularPrecoTotal);
    }
  });

  // Inicializa a exibição e o cálculo
  toggleCampos();
  calcularPrecoTotal();
});

document.addEventListener("DOMContentLoaded", function() {

    function createAutocomplete(inputId, url) {
        const input = document.getElementById(inputId);
        if (!input) return;

        const dropdown = document.createElement("ul");
        dropdown.className = "autocomplete-list";
        document.body.appendChild(dropdown);

        let currentFocus = -1; // índice da opção selecionada
        let options = [];

        // Posiciona o dropdown logo abaixo do input
        function positionDropdown() {
            const rect = input.getBoundingClientRect();
            dropdown.style.position = "absolute";
            dropdown.style.top = `${rect.bottom + window.scrollY}px`;
            dropdown.style.left = `${rect.left + window.scrollX}px`;
            dropdown.style.width = `${rect.width}px`;
        }

        // Fecha e limpa dropdown
        function closeDropdown() {
            dropdown.innerHTML = "";
            dropdown.style.display = "none";
            currentFocus = -1;
        }

        // Renderiza lista com base nas opções
        function renderOptions(data) {
            dropdown.innerHTML = "";
            options = data;
            if (data.length === 0) {
                closeDropdown();
                return;
            }

            data.forEach((item, index) => {
                const li = document.createElement("li");
                li.textContent = item;
                li.dataset.index = index;
                li.addEventListener("mousedown", (e) => {
                    e.preventDefault(); // evita blur antes do clique
                    input.value = item;
                    closeDropdown();
                });
                dropdown.appendChild(li);
            });

            positionDropdown();
            dropdown.style.display = "block";
        }

        async function fetchOptions(query = "") {
            const response = await fetch(`${url}?q=${encodeURIComponent(query)}`);
            const data = await response.json();
            renderOptions(data);
        }

        // Gerencia teclas de navegação
        input.addEventListener("keydown", (e) => {
            const items = dropdown.querySelectorAll("li");

            if (e.key === "ArrowDown") {
                currentFocus = (currentFocus + 1) % items.length;
                setActive(items);
                e.preventDefault();
            }
            else if (e.key === "ArrowUp") {
                currentFocus = (currentFocus - 1 + items.length) % items.length;
                setActive(items);
                e.preventDefault();
            }
            else if (e.key === "Enter") {
                e.preventDefault();
                if (currentFocus >= 0 && items[currentFocus]) {
                    input.value = items[currentFocus].textContent;
                    closeDropdown();
                }
            }
            else if (e.key === "Tab") {
                closeDropdown();
            }
        });

        function setActive(items) {
            items.forEach(li => li.classList.remove("active"));
            if (currentFocus >= 0 && items[currentFocus]) {
                items[currentFocus].classList.add("active");
                items[currentFocus].scrollIntoView({ block: "nearest" });
            }
        }

        // Eventos do campo
        input.addEventListener("focus", async () => {
            await fetchOptions("");
        });

        input.addEventListener("input", async function() {
            const query = this.value.trim();
            await fetchOptions(query);
        });

        input.addEventListener("blur", () => {
            setTimeout(closeDropdown, 150);
        });

        // Fecha ao clicar fora
        document.addEventListener("click", (e) => {
            if (e.target !== input && !dropdown.contains(e.target)) {
                closeDropdown();
            }
        });

        // Reposiciona em rolagem ou resize
        window.addEventListener("resize", positionDropdown);
        window.addEventListener("scroll", positionDropdown);
    }

    // Cria autocompletes separados
    createAutocomplete("id_marca", "/autocomplete/marcas/");
    createAutocomplete("id_fornecedor", "/autocomplete/fornecedores/");
});