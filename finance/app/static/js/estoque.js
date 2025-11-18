// estoque.js - Sistema Completo de Estoque

document.addEventListener('DOMContentLoaded', function() {
    console.log('Sistema de Estoque Iniciado');
    inicializarEventos();
    inicializarPesquisas();
});

function inicializarEventos() {
    // Formulário de Produto
    document.getElementById('form-produto').addEventListener('submit', salvarProduto);

    // Formulário de Matéria-Prima
    document.getElementById('form-materia').addEventListener('submit', salvarMateria);

    // Fechar modais ao clicar fora
    window.addEventListener('click', function(event) {
        const modalProduto = document.getElementById('modal-produto');
        const modalMateria = document.getElementById('modal-materia');

        if (event.target === modalProduto) {
            fecharModalProduto();
        }
        if (event.target === modalMateria) {
            fecharModalMateria();
        }
    });
}

function inicializarPesquisas() {
    // Pesquisa em tempo real para produtos
    document.getElementById('pesquisa-produto').addEventListener('input', function(e) {
        const termo = e.target.value.toLowerCase();
        const linhas = document.querySelectorAll('#tbody-produtos tr');

        linhas.forEach(linha => {
            const texto = linha.textContent.toLowerCase();
            linha.style.display = texto.includes(termo) ? '' : 'none';
        });
    });

    // Pesquisa em tempo real para matérias-primas
    document.getElementById('pesquisa-materia').addEventListener('input', function(e) {
        const termo = e.target.value.toLowerCase();
        const linhas = document.querySelectorAll('#tbody-materias tr');

        linhas.forEach(linha => {
            const texto = linha.textContent.toLowerCase();
            linha.style.display = texto.includes(termo) ? '' : 'none';
        });
    });
}

// ==================== PRODUTOS ====================
function editarProduto(id) {
    fetch(`/api/produtos/${id}/`)
        .then(response => {
            if (!response.ok) throw new Error('Erro ao carregar produto');
            return response.json();
        })
        .then(produto => {
            document.getElementById('titulo-modal-produto').textContent = 'Editar Produto';
            document.getElementById('produto-id').value = produto.id;
            document.getElementById('produto-nome').value = produto.nome;
            document.getElementById('produto-categoria').value = produto.categoria;
            document.getElementById('produto-estoque').value = produto.quantidade_em_estoque;
            document.getElementById('produto-valor-venda').value = produto.valor_venda || '';

            document.getElementById('modal-produto').style.display = 'block';
        })
        .catch(error => {
            console.error('Erro ao carregar produto:', error);
            alert('Erro ao carregar dados do produto');
        });
}

function salvarProduto(e) {
    e.preventDefault();

    const id = document.getElementById('produto-id').value;
    const url = id ? `/api/produtos/${id}/editar/` : '/api/produtos/novo/';
    const method = 'POST';

    const dados = {
        nome: document.getElementById('produto-nome').value,
        categoria: document.getElementById('produto-categoria').value,
        quantidade_em_estoque: parseInt(document.getElementById('produto-estoque').value),
        valor_venda: document.getElementById('produto-valor-venda').value ?
                     parseFloat(document.getElementById('produto-valor-venda').value) : null
    };

    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify(dados)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            fecharModalProduto();
            location.reload();
        } else {
            alert('Erro ao salvar produto: ' + (data.error || 'Erro desconhecido'));
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        alert('Erro ao salvar produto');
    });
}

function excluirProduto(id) {
    if (confirm('Tem certeza que deseja excluir este produto?')) {
        fetch(`/api/produtos/${id}/excluir/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCSRFToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert('Erro ao excluir produto: ' + (data.error || 'Erro desconhecido'));
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            alert('Erro ao excluir produto');
        });
    }
}

function fecharModalProduto() {
    document.getElementById('modal-produto').style.display = 'none';
}

// ==================== MATÉRIAS-PRIMAS ====================
function editarMateria(id) {
    fetch(`/api/materias/${id}/`)
        .then(response => {
            if (!response.ok) throw new Error('Erro ao carregar matéria-prima');
            return response.json();
        })
        .then(materia => {
            document.getElementById('titulo-modal-materia').textContent = 'Editar Matéria-Prima';
            document.getElementById('materia-id').value = materia.id;
            document.getElementById('materia-nome').value = materia.nome;
            document.getElementById('materia-categoria').value = materia.categoria;
            document.getElementById('materia-especificacao').value = materia.especificacao;
            document.getElementById('materia-cor').value = materia.cor || '';

            document.getElementById('modal-materia').style.display = 'block';
        })
        .catch(error => {
            console.error('Erro ao carregar matéria-prima:', error);
            alert('Erro ao carregar dados da matéria-prima');
        });
}

function salvarMateria(e) {
    e.preventDefault();

    const id = document.getElementById('materia-id').value;
    const url = id ? `/api/materias/${id}/editar/` : '/api/materias/nova/';
    const method = 'POST';

    const dados = {
        nome: document.getElementById('materia-nome').value,
        categoria: document.getElementById('materia-categoria').value,
        especificacao: document.getElementById('materia-especificacao').value,
        cor: document.getElementById('materia-cor').value
    };

    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify(dados)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            fecharModalMateria();
            location.reload();
        } else {
            alert('Erro ao salvar matéria-prima: ' + (data.error || 'Erro desconhecido'));
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        alert('Erro ao salvar matéria-prima');
    });
}

function excluirMateria(id) {
    if (confirm('Tem certeza que deseja excluir esta matéria-prima?')) {
        fetch(`/api/materias/${id}/excluir/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCSRFToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert('Erro ao excluir matéria-prima: ' + (data.error || 'Erro desconhecido'));
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            alert('Erro ao excluir matéria-prima');
        });
    }
}

function fecharModalMateria() {
    document.getElementById('modal-materia').style.display = 'none';
}

// ==================== FUNÇÕES AUXILIARES ====================

function getCSRFToken() {
    const name = 'csrftoken';
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}