// static/js/estoque.js
document.addEventListener("DOMContentLoaded", function() {
  function toNumber(v){ return isNaN(parseFloat(v)) ? 0 : parseFloat(v); }

  document.querySelectorAll('#estoque-table tbody tr').forEach(row => {
    // torna células editáveis (com input ao clicar)
    row.querySelectorAll('.editable').forEach(cell => {
      cell.addEventListener('click', () => {
        if (cell.querySelector('input')) return;
        const val = cell.textContent.trim();
        const input = document.createElement('input');
        input.type = (cell.classList.contains('quantidade') ? 'number' : 'text');
        input.value = val;
        input.style.width = '100%';
        cell.innerHTML = '';
        cell.appendChild(input);
        input.focus();
      });

      // ao sair do input, restaura texto
      cell.addEventListener('focusout', (e) => {
        const input = cell.querySelector('input');
        if (!input) return;
        let v = input.value;
        if (cell.classList.contains('quantidade')) {
          v = parseInt(v) || 0;
        } else {
          v = (parseFloat(v) || 0).toFixed(2);
        }
        cell.innerHTML = v;
      });
    });

    // botão salvar
    const salvar = row.querySelector('.salvar-btn');
    salvar.addEventListener('click', async () => {
      const id = row.dataset.estoqueId;
      const qtdCell = row.querySelector('.quantidade');
      const valCell = row.querySelector('.valor');
      const qtd = parseInt(qtdCell.textContent.trim().replace(',', '.')) || 0;
      const valor = parseFloat(valCell.textContent.trim().replace(',', '.')) || 0;

      const payload = { estoque_id: id, quantidade_produto: qtd, valor_produto: valor };
      try {
        const resp = await fetch('/api/estoque/update/', {
          method: 'POST',
          headers: {'Content-Type': 'application/json', 'X-CSRFToken': getCSRF()},
          body: JSON.stringify(payload)
        });
        const data = await resp.json();
        if (data.ok) {
          row.querySelector('.produto_total').textContent = data.produto_total;
          row.querySelector('.materia_prima_total').textContent = data.materia_prima_total;
          alert('Estoque atualizado');
        } else {
          alert('Erro ao atualizar');
        }
      } catch (e) {
        console.error(e);
        alert('Erro de rede');
      }
    });

    // botão atualizar (força recálculo do backend)
    const atualizar = row.querySelector('.atualizar-btn');
    atualizar.addEventListener('click', async () => {
      const id = row.dataset.estoqueId;
      try {
        const resp = await fetch('/api/estoque/update/', {
          method: 'POST',
          headers: {'Content-Type': 'application/json', 'X-CSRFToken': getCSRF()},
          body: JSON.stringify({estoque_id: id})
        });
        const data = await resp.json();
        if (data.ok) {
          row.querySelector('.quantidade').textContent = data.quantidade_produto;
          row.querySelector('.valor').textContent = data.valor_produto;
          row.querySelector('.produto_total').textContent = data.produto_total;
          row.querySelector('.materia_prima_total').textContent = data.materia_prima_total;
          alert('Recalculado no servidor');
        } else alert('Erro');
      } catch(e){ console.error(e); alert('Erro de rede'); }
    });
  });

  function getCSRF(){
    const name = 'csrftoken';
    const cookies = document.cookie.split(';').map(c=>c.trim());
    for (let c of cookies){
      if (c.startsWith(name+'=')) return decodeURIComponent(c.split('=')[1]);
    }
    return '';
  }
});
