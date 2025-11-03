document.addEventListener('DOMContentLoaded', function () {
  const unidadeSelect = document.querySelector('#id_unidade');
  const camposQuantidade = document.getElementById('campos_quantidade');
  const camposCm = document.getElementById('campos_cm');

  if (!unidadeSelect || !camposQuantidade || !camposCm) return;

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
  }

  unidadeSelect.addEventListener('change', toggleCampos);
  toggleCampos();
});