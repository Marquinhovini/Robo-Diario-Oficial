document.addEventListener('DOMContentLoaded', function() {
    const currentDate = new Date().toISOString().split('T')[0];
    const minStartDate = '2015-01-01';  // Data mínima para a data inicial

    const startDateInput = document.getElementById('startDate');
    const endDateInput = document.getElementById('endDate');

    // Define as restrições de data
    startDateInput.setAttribute('min', minStartDate);
    startDateInput.setAttribute('max', currentDate);
    endDateInput.setAttribute('max', currentDate);

    // Remover o atributo readonly quando a página carrega
    startDateInput.removeAttribute('readonly');
    endDateInput.removeAttribute('readonly');



    // Inicializar tooltips usando tippy.js
    tippy('label', {
        content(reference) {
            return reference.getAttribute('data-tippy');
        },
        animation: 'shift-away',
        arrow: true,
        placement: 'right', // Posição do tooltip em relação ao elemento
        showOnCreate: true // Mostrar tooltip imediatamente ao criar
    });
});

document.getElementById('dateForm').addEventListener('submit', function(event) {
    event.preventDefault();

    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;
    const statusDiv = document.getElementById('status');

    // Validar se o ano começa com zero e se a data inicial é pelo menos 2015-01-01
    const startDateYear = startDate.split('-')[0];
    const endDateYear = endDate.split('-')[0];

    if (startDateYear.startsWith('0') || endDateYear.startsWith('0')) {
        statusDiv.textContent = 'Ano não pode começar com zero.';
        statusDiv.style.color = 'white';
        alert('Ano não pode começar com zero.');
        return;
    }

    if (new Date(startDate) < new Date('2015-01-01')) {
        statusDiv.textContent = 'A data inicial não pode ser anterior a 2015.';
        statusDiv.style.color = 'white';
        alert('A data inicial não pode ser anterior a 2015.');
        return;
    }

    // Verificar se os campos estão vazios
    if (!startDate || !endDate) {
        alert('Preencha ambos os campos de data.');
        return;
    }

    // Mostrar mensagem de status enquanto está pesquisando
    statusDiv.textContent = 'Pesquisando...';
    statusDiv.style.color = 'white';

    fetch('/collect', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ startDate: startDate, endDate: endDate })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            statusDiv.textContent = data.message;
            statusDiv.style.color = 'white';
            // Resetar readonly após sucesso
            document.getElementById('startDate').removeAttribute('readonly');
            document.getElementById('endDate').removeAttribute('readonly');
        } else {
            statusDiv.textContent = data.message + (data.error ? ': ' + data.error : '');
            statusDiv.style.color = 'white';
        }
    })
    .catch(error => {
        statusDiv.textContent = 'Erro: ' + error;
        statusDiv.style.color = 'white';
    });
});

function setStatusMessage(message, color) {
    const statusDiv = document.getElementById('status');
    statusDiv.textContent = message;
    statusDiv.style.color = color;
}