document.addEventListener("DOMContentLoaded", async () => {
  const vendasCtx = document.getElementById("vendasChart")?.getContext("2d");

  // =========================
  // FUNÇÃO: CARREGAR RESUMO
  // =========================
  async function carregarResumo() {
    try {
      const response = await fetch("/api/financeiro/resumo/");
      if (!response.ok) throw new Error("Erro ao carregar dados");
      const data = await response.json();

      const meses = data.vendas.map(v => v.mes);
      const vendas = data.vendas.map(v => v.valor);
      const despesas = data.despesas.map(d => d.valor);

      // Atualiza gráfico (se existir)
      if (vendasCtx) {
        new Chart(vendasCtx, {
          type: "bar",
          data: {
            labels: meses,
            datasets: [
              { label: "Vendas", data: vendas, backgroundColor: "rgba(75,192,192,0.7)" },
              { label: "Despesas", data: despesas, backgroundColor: "rgba(255,99,132,0.7)" }
            ]
          },
          options: {
            responsive: true,
            scales: { y: { beginAtZero: true } }
          }
        });
      }

      // Atualiza totais
      const totalVendas = vendas.reduce((a, b) => a + b, 0);
      const totalDespesas = despesas.reduce((a, b) => a + b, 0);

      if (document.getElementById("totalVendas"))
        document.getElementById("totalVendas").textContent = totalVendas.toFixed(2);

      if (document.getElementById("totalDespesas"))
        document.getElementById("totalDespesas").textContent = totalDespesas.toFixed(2);

      if (document.getElementById("custoFixo"))
        document.getElementById("custoFixo").textContent = data.custo_fixo.toFixed(2);

    } catch (error) {
      console.error("Erro ao carregar resumo financeiro:", error);
    }
  }

  // =========================
  // CONTROLE DE MODAIS
  // =========================
  const modais = document.querySelectorAll(".modal");
  const abrirModalVenda = document.getElementById("abrirModalVenda");
  const abrirModalDespesa = document.getElementById("abrirModalDespesa");

  function abrirModal(id) {
    const modal = document.getElementById(id);
    if (modal) modal.style.display = "flex";
  }

  function fecharModal(id) {
    const modal = document.getElementById(id);
    if (modal) modal.style.display = "none";
  }

  abrirModalVenda?.addEventListener("click", () => abrirModal("modalVenda"));
  abrirModalDespesa?.addEventListener("click", () => abrirModal("modalDespesa"));

  // Fechar modal ao clicar no botão de cancelar ou no X
  document.querySelectorAll("[data-close]").forEach(btn => {
    btn.addEventListener("click", () => fecharModal(btn.dataset.close));
  });

  // Fechar ao clicar fora do conteúdo
  modais.forEach(modal => {
    modal.addEventListener("click", e => {
      if (e.target === modal) modal.style.display = "none";
    });
  });

  // =========================
  // FORMULÁRIO: NOVA VENDA
  // =========================
  const formVenda = document.getElementById("formVenda");
  if (formVenda) {
    formVenda.addEventListener("submit", async e => {
      e.preventDefault();

      const formData = new FormData(formVenda);
      const payload = Object.fromEntries(formData.entries());

      try {
        const resp = await fetch("/api/financeiro/venda/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });

        if (!resp.ok) throw new Error("Erro ao registrar venda");
        alert("✅ Venda registrada com sucesso!");
        fecharModal("modalVenda");
        formVenda.reset();
        await carregarResumo();

      } catch (error) {
        console.error(error);
        alert("Erro ao registrar venda.");
      }
    });
  }

  // =========================
  // FORMULÁRIO: NOVA DESPESA
  // =========================
  const formDespesa = document.getElementById("formDespesa");
  if (formDespesa) {
    formDespesa.addEventListener("submit", async e => {
      e.preventDefault();

      const formData = new FormData(formDespesa);
      const payload = Object.fromEntries(formData.entries());

      try {
        const resp = await fetch("/api/financeiro/despesa/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });

        if (!resp.ok) throw new Error("Erro ao registrar despesa");
        alert("✅ Despesa registrada com sucesso!");
        fecharModal("modalDespesa");
        formDespesa.reset();
        await carregarResumo();

      } catch (error) {
        console.error(error);
        alert("Erro ao registrar despesa.");
      }
    });
  }

  // =========================
  // CARREGA DADOS INICIAIS
  // =========================
  await carregarResumo();
});
