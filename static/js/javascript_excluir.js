
function exibirModal(matricula, email) {
    // Preencher os inputs do modal com os detalhes do usuário
    $('#detalhes-matricula').val(matricula);
    $('#detalhes-email').val(email);

    // Exibir o modal
    $('#confirmacao-modal').modal('show');
}


function fecharModal() {
    $('#confirmacao-modal').modal('hide');
}

var recarregarBtn = document.getElementById('btn-sim');

    // Adiciona um ouvinte de evento para o clique no botão
    recarregarBtn.addEventListener('click', function() {
        // Recarrega a página
        window.location.reload();
    });

