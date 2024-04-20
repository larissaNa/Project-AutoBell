function excluirUsuarios() {
    $.ajax({
        url: '/excluir_usuarios',
        method: 'POST',
        xhrFields: {
            onprogress: function(e) {
                if (e.lengthComputable) {
                    var progress = (e.loaded / e.total) * 100;
                    $('#progressBar').val(progress);
                }
            }
        },
        success: function(response) {
            // Lógica após a conclusão da exclusão dos usuários (se necessário)
        },
        error: function(error) {
            // Lógica em caso de erro na requisição AJAX
            console.error('Erro:', error);
        }
    });
}

    
function exibirModal() {
    // Preencher os inputs do modal com os detalhes do usuário
  
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

