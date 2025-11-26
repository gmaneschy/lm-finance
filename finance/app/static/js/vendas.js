// static/js/vendas.js

let carrinho = [];

function adicionarAoCarrinho(id, nome, preco, estoqueMax) {
    preco = parseFloat(preco.replace(',', '.'));

    // Verifica se já existe no carrinho
    let itemExistente = carrinho.find(item => item.id === id);

    if (itemExistente) {
        if (itemExistente.quantidade + 1 > estoqueMax) {
            alert("Limite de estoque atingido para este item!");
            return;
        }
        itemExistente.quantidade++;
        itemExistente.subtotal = itemExistente.quantidade * preco;
    } else {
        carrinho.push({
            id: id,
            nome: nome,
            preco: preco,
            quantidade: 1,
            subtotal: preco,
            estoqueMax: estoqueMax
        });
    }

    renderizarCarrinho();
}

function removerItem(index) {
    carrinho.splice(index, 1);
    renderizarCarrinho();
}

function renderizarCarrinho() {
    const tbody = document.getElementById('tabelaCarrinho');
    tbody.innerHTML = '';
    let total = 0;

    carrinho.forEach((item, index) => {
        total += item.subtotal;

        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${item.nome}</td>
            <td>
                <input type="number" class="form-control form-control-sm"
                       value="${item.quantidade}" min="1" max="${item.estoqueMax}"
                       onchange="atualizarQuantidade(${index}, this.value)">
            </td>
            <td>R$ ${item.subtotal.toFixed(2)}</td>
            <td>
                <button class="btn btn-sm btn-danger" onclick="removerItem(${index})">×</button>
            </td>
        `;
        tbody.appendChild(tr);
    });

    document.getElementById('valorTotalDisplay').innerText = `R$ ${total.toFixed(2)}`;
}

function atualizarQuantidade(index, novaQtd) {
    let item = carrinho[index];
    novaQtd = parseInt(novaQtd);

    if (novaQtd > item.estoqueMax) {
        alert("Quantidade maior que o estoque!");
        novaQtd = item.estoqueMax;
    }
    if (novaQtd < 1) novaQtd = 1;

    item.quantidade = novaQtd;
    item.subtotal = item.quantidade * item.preco;
    renderizarCarrinho();
}

// Filtro de busca na tela
document.getElementById('buscaProduto').addEventListener('keyup', function() {
    let valor = this.value.toLowerCase();
    let itens = document.querySelectorAll('.produto-item');

    itens.forEach(item => {
        let nome = item.getAttribute('data-nome');
        if (nome.includes(valor)) {
            item.style.display = 'block';
        } else {
            item.style.display = 'none';
        }
    });
});

async function finalizarVenda() {
    if (carrinho.length === 0) {
        alert("O carrinho está vazio!");
        return;
    }

    const metodoPagamento = document.getElementById('metodoPagamento').value;
    const clienteNome = document.getElementById('clienteNome').value;

    // Calcula total novamente para segurança
    const totalVenda = carrinho.reduce((sum, item) => sum + item.subtotal, 0);

    const dadosVenda = {
        itens: carrinho,
        metodo_pagamento: metodoPagamento,
        cliente_nome: clienteNome,
        total_venda: totalVenda.toFixed(2)
    };

    try {
        const response = await fetch('/api/salvar_venda/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(dadosVenda)
        });

        const result = await response.json();

        if (result.success) {
            alert("Venda realizada com sucesso!");
            window.location.reload(); // Recarrega para atualizar estoques
        } else {
            alert("Erro ao salvar venda: " + result.error);
        }

    } catch (error) {
        console.error('Erro:', error);
        alert("Erro de conexão.");
    }
}