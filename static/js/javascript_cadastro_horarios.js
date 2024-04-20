// Event listener para o botão "Salvar"
document.getElementById("dia_semana").addEventListener("checked", function(event) {
  event.preventDefault();

  console.log("tá")

  // Obtém todos os checkboxes de dias da semana selecionados
  var checkboxes = document.querySelectorAll('input[type="checkbox"]:checked');
  var diasSelecionados = [];

  checkboxes.forEach(function(checkbox) {
    diasSelecionados.push(checkbox.value);
  });

  // Define o valor do campo de input invisível com os dias selecionados
  document.getElementById("diasSemana").value = diasSelecionados.join(', ');

  console.log(diasSelecionados)
  

});
